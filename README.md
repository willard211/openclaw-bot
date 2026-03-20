# OpenClaw Trade Employee

An MVP skeleton for a foreign-trade AI assistant that combines product facts, company profile answers, and sales follow-up guidance.

## What This Repo Includes

- `app/`: local chat demo and webhook endpoints
- `kb-templates/`: CSV knowledge-base templates for product, company, and sales content
- `skills/`: skill prompt drafts for the three core capability areas
- `routing/`: routing and risk-control rules
- `data/`: replay and multi-intent evaluation cases
- `scripts/`: local evaluation scripts and WhatsApp dev helper
- `docs/`: implementation notes and rollout checklist
- `tasks/`: local working rules, lessons, and task tracking

## Current MVP Scope

- Detects the likely skill path from a customer message
- Supports mixed product, company, and sales-assistant response composition
- Flags high-risk topics such as contract, credit terms, exclusivity, and final pricing for handoff
- Exposes local endpoints for chat, WhatsApp webhook, and WeCom webhook testing

## Local Setup

The project uses only Python standard library modules for the current MVP.

If `python` in your shell points to the WindowsApps stub, use the real interpreter:

```powershell
C:\Users\31072\AppData\Local\Programs\Python\Python310\python.exe
```

Optional local env file:

```powershell
Copy-Item .env.example .env
```

The app auto-loads `.env` from the project root.

## Verified Local Commands

Replay evaluation:

```powershell
& 'C:\Users\31072\AppData\Local\Programs\Python\Python310\python.exe' 'scripts\replay_eval.py'
```

Multi-intent evaluation:

```powershell
& 'C:\Users\31072\AppData\Local\Programs\Python\Python310\python.exe' 'scripts\multi_intent_eval.py'
```

Local server:

```powershell
& 'C:\Users\31072\AppData\Local\Programs\Python\Python310\python.exe' 'app\server.py'
```

Open `http://127.0.0.1:8787` after startup.

## Verified Local Results

- `scripts/replay_eval.py`: passed with `10/10` routing and `10/10` handoff accuracy
- `scripts/multi_intent_eval.py`: passed with `10/10` multi-intent and `10/10` handoff accuracy
- `GET /health`: returned `200` with `{"ok": true}`
- `POST /chat`: returned `200` and produced a product answer for `Please share M8 spec and MOQ`

## API Examples

`POST /chat`

```json
{"message":"Please share M8 spec and MOQ"}
```

`POST /webhook/whatsapp`

```json
{"from":"+123456","message":"Your price is too expensive"}
```

`POST /webhook/wecom`

```json
{"from":"u001","message":"Please share MOQ"}
```

## Webhook Notes

- `GET /webhook/whatsapp`: Meta verification endpoint using `hub.mode`, `hub.verify_token`, and `hub.challenge`
- `POST /webhook/whatsapp`: accepts both the simplified MVP payload and Meta Cloud API webhook payload
- `GET /webhook/wecom`: WeCom signature verification endpoint
- `POST /webhook/wecom`: accepts the MVP JSON payload

By default, `WHATSAPP_AUTO_REPLY=0`, so WhatsApp requests return a reply preview without sending a live message.

## Environment Variables

See [.env.example](C:\Users\31072\openclaw-trade-employee\.env.example).

- `WHATSAPP_VERIFY_TOKEN`
- `WHATSAPP_ACCESS_TOKEN`
- `WHATSAPP_PHONE_NUMBER_ID`
- `WHATSAPP_GRAPH_VERSION`
- `WHATSAPP_AUTO_REPLY`
- `WECOM_TOKEN`

For live WhatsApp sending, you must set:

- `WHATSAPP_AUTO_REPLY=1`
- `WHATSAPP_ACCESS_TOKEN`
- `WHATSAPP_PHONE_NUMBER_ID`

## Suggested Evaluation Metrics

- First response time
- Valid lead rate
- Quote conversion rate
- Human handoff rate
- Hallucination rate

## Known MVP Limitations

- Routing and handoff logic are keyword-weighted rules, not model-based reasoning
- Knowledge retrieval is template-driven and limited to the bundled CSV data
- WhatsApp live send depends on external Meta credentials and network access
- The repo does not yet include automated unit tests beyond the built-in replay scripts
