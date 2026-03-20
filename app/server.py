import json
import os
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from engine import build_response, to_json
from env_loader import load_env_file
from whatsapp_cloud import is_configured as whatsapp_is_configured
from whatsapp_cloud import send_text_message as whatsapp_send_text_message

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
BASE_DIR = ROOT.parent
load_env_file(BASE_DIR)
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "dev_verify_token")
WECOM_TOKEN = os.getenv("WECOM_TOKEN", "dev_wecom_token")
WHATSAPP_AUTO_REPLY = os.getenv("WHATSAPP_AUTO_REPLY", "0").lower() in ("1", "true", "yes", "on")


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, code: int, payload: dict):
        raw = to_json(payload)
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _send_text(self, code: int, text: str):
        raw = text.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _query(self):
        parsed = urlparse(self.path)
        return parsed.path, parse_qs(parsed.query)

    def do_GET(self):
        path, query = self._query()
        if path == "/health":
            return self._send_json(200, {"ok": True})
        if path in ["/", "/index.html"]:
            page = (STATIC / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(page)))
            self.end_headers()
            self.wfile.write(page)
            return
        if path == "/webhook/whatsapp":
            return self._verify_whatsapp(query)
        if path == "/webhook/wecom":
            return self._verify_wecom(query)
        self._send_json(404, {"error": "not_found"})

    def do_POST(self):
        path, _ = self._query()
        if path == "/chat":
            return self._handle_chat()
        if path == "/webhook/whatsapp":
            return self._handle_whatsapp()
        if path == "/webhook/wecom":
            return self._handle_wecom()
        return self._send_json(404, {"error": "not_found"})

    def _parse_message_body(self):
        content_length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(content_length) if content_length > 0 else b"{}"
        payload = json.loads(body.decode("utf-8"))
        return payload, str(payload.get("message", "")).strip()

    def _verify_whatsapp(self, query):
        # Meta verify handshake:
        # hub.mode=subscribe&hub.verify_token=...&hub.challenge=...
        mode = query.get("hub.mode", [""])[0]
        verify_token = query.get("hub.verify_token", [""])[0]
        challenge = query.get("hub.challenge", [""])[0]
        if mode == "subscribe" and verify_token == WHATSAPP_VERIFY_TOKEN and challenge:
            return self._send_text(200, challenge)
        return self._send_json(403, {"error": "verify_failed"})

    def _verify_wecom(self, query):
        # Basic signature check using token/timestamp/nonce.
        # For encrypted callbacks, echo_str is returned as-is after signature check.
        signature = query.get("signature", [""])[0] or query.get("msg_signature", [""])[0]
        timestamp = query.get("timestamp", [""])[0]
        nonce = query.get("nonce", [""])[0]
        echostr = query.get("echostr", [""])[0]
        if not (signature and timestamp and nonce):
            return self._send_json(400, {"error": "missing_signature_fields"})
        expected = _wecom_signature(WECOM_TOKEN, timestamp, nonce)
        if expected != signature:
            return self._send_json(403, {"error": "verify_failed"})
        return self._send_text(200, echostr or "ok")

    def _handle_chat(self):
        try:
            _, message = self._parse_message_body()
        except Exception:
            return self._send_json(400, {"error": "invalid_json"})

        if not message:
            return self._send_json(400, {"error": "empty_message"})

        result = build_response(message)
        self._send_json(200, result)

    def _handle_whatsapp(self):
        try:
            payload, _ = self._parse_message_body()
        except Exception:
            return self._send_json(400, {"error": "invalid_json"})

        # Supports:
        # 1) MVP: {"from":"...","message":"..."}
        # 2) Meta Cloud API webhook payload
        from_id, message = _parse_whatsapp_payload(payload)

        if not message:
            # Ignore non-message events (status updates, delivery receipts, etc.)
            return self._send_json(200, {"channel": "whatsapp", "ignored": True})
        result = build_response(message)
        delivery = {
            "mode": "preview",
            "sent": False,
            "reason": "auto_reply_disabled",
        }
        if WHATSAPP_AUTO_REPLY:
            if whatsapp_is_configured():
                status_code, provider_resp = whatsapp_send_text_message(from_id, str(result["reply"]))
                delivery = {
                    "mode": "live",
                    "sent": 200 <= status_code < 300,
                    "provider_status": status_code,
                    "provider_response": provider_resp,
                }
            else:
                delivery = {
                    "mode": "preview",
                    "sent": False,
                    "reason": "missing_whatsapp_config",
                }

        return self._send_json(
            200,
            {
                "channel": "whatsapp",
                "to": from_id,
                "reply": result["reply"],
                "skills": result["skills"],
                "handoff": result["handoff"],
                "delivery": delivery,
            },
        )

    def _handle_wecom(self):
        _, query = self._query()
        signature = query.get("signature", [""])[0] or query.get("msg_signature", [""])[0]
        timestamp = query.get("timestamp", [""])[0]
        nonce = query.get("nonce", [""])[0]
        if not (signature and timestamp and nonce):
            return self._send_json(400, {"error": "missing_signature_fields"})
        expected = _wecom_signature(WECOM_TOKEN, timestamp, nonce)
        if expected != signature:
            return self._send_json(403, {"error": "verify_failed"})

        try:
            payload, _ = self._parse_message_body()
        except Exception:
            return self._send_json(400, {"error": "invalid_json"})

        # MVP JSON shape:
        # {"from":"...","message":"..."}
        from_id = str(payload.get("from", "unknown"))
        message = str(payload.get("message", "")).strip()
        if not message:
            return self._send_json(400, {"error": "empty_message"})

        result = build_response(message)
        return self._send_json(
            200,
            {
                "channel": "wecom",
                "to": from_id,
                "reply": result["reply"],
                "skills": result["skills"],
                "handoff": result["handoff"],
            },
        )

    def log_message(self, fmt, *args):
        return


def _wecom_signature(token: str, timestamp: str, nonce: str) -> str:
    items = sorted([token, timestamp, nonce])
    src = "".join(items).encode("utf-8")
    return hashlib.sha1(src).hexdigest()


def _parse_whatsapp_payload(payload: dict):
    from_id = str(payload.get("from", "unknown"))
    message = str(payload.get("message", "")).strip()

    if message:
        return from_id, message

    messages = payload.get("messages")
    if isinstance(messages, list) and messages:
        first = messages[0]
        if isinstance(first, dict):
            from_id = str(first.get("from", from_id))
            text = first.get("text", "")
            if isinstance(text, dict):
                message = str(text.get("body", "")).strip()
            else:
                message = str(text).strip()
            if message:
                return from_id, message

    # Meta Cloud API shape: entry[].changes[].value.messages[]
    entry = payload.get("entry")
    if isinstance(entry, list):
        for e in entry:
            if not isinstance(e, dict):
                continue
            for ch in e.get("changes", []):
                if not isinstance(ch, dict):
                    continue
                value = ch.get("value", {})
                if not isinstance(value, dict):
                    continue
                for m in value.get("messages", []):
                    if not isinstance(m, dict):
                        continue
                    from_id = str(m.get("from", from_id))
                    text = m.get("text", {})
                    if isinstance(text, dict):
                        message = str(text.get("body", "")).strip()
                    else:
                        message = str(text).strip()
                    if message:
                        return from_id, message
    return from_id, message


def run():
    server = ThreadingHTTPServer(("127.0.0.1", 8787), Handler)
    print("Server running on http://127.0.0.1:8787")
    server.serve_forever()


if __name__ == "__main__":
    run()
