import json
import os
import urllib.error
import urllib.request
from typing import Dict, Tuple


def _config():
    return {
        "graph_version": os.getenv("WHATSAPP_GRAPH_VERSION", "v22.0"),
        "phone_number_id": os.getenv("WHATSAPP_PHONE_NUMBER_ID", ""),
        "access_token": os.getenv("WHATSAPP_ACCESS_TOKEN", ""),
    }


def is_configured() -> bool:
    cfg = _config()
    return bool(cfg["phone_number_id"] and cfg["access_token"])


def send_text_message(to: str, text: str) -> Tuple[int, Dict[str, object]]:
    cfg = _config()
    if not is_configured():
        return 400, {"error": "missing_whatsapp_config"}

    url = (
        f"https://graph.facebook.com/"
        f"{cfg['graph_version']}/{cfg['phone_number_id']}/messages"
    )
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": text[:4096],
        },
    }
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url=url,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {cfg['access_token']}",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode("utf-8")
            data = json.loads(raw) if raw else {}
            return resp.status, data
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            data = json.loads(raw) if raw else {}
        except Exception:
            data = {"error": raw}
        return e.code, data
    except Exception as e:
        return 500, {"error": str(e)}
