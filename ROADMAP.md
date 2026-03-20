# Roadmap

This roadmap keeps the project scoped as a practical MVP first, then pushes it toward a safer production-ready trade assistant.

## Current State

- Local chat demo is working
- Rule-based routing and handoff logic are in place
- Replay and multi-intent evaluation scripts are passing on the current bundled cases
- WhatsApp and WeCom webhook entry points exist, with WhatsApp live send behind env-gated config

## Next Milestones

### v0.2 Knowledge Quality

- Replace template KB rows with real company, product, and sales content
- Expand multilingual coverage beyond the current example cases
- Add clearer citation or source-trace behavior in replies where needed
- Increase replay-case coverage for pricing, MOQ, certification, and objection-handling flows

### v0.3 Safer Handoff and Channel Readiness

- Tighten the high-risk handoff rules for pricing, payment terms, contract language, and exclusivity
- Add stronger webhook validation coverage for WhatsApp and WeCom request shapes
- Define operator review workflow for flagged conversations
- Improve logging for inbound messages, routing decisions, and handoff reasons

### v0.4 Productization

- Add automated tests beyond the current replay scripts
- Introduce configuration and deployment guidance for a hosted environment
- Add basic analytics for first response time, handoff rate, and answer quality
- Document operating runbooks for support and incident handling

## Out of Scope for the Current MVP

- Model-based retrieval or agent orchestration
- Multi-tenant account management
- Production-grade auth, persistence, and observability
- Automated outbound sales workflows
