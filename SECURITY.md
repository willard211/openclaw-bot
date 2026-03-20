# Security Policy

## Reporting a Vulnerability

If you discover a security issue in this repository, do not open a public GitHub issue with exploit details.

Instead, report it privately to the repository owner through GitHub account contact or another private channel you already use with the maintainer. Include:

- a short description of the issue
- the affected file, endpoint, or workflow
- reproduction steps or a minimal proof of concept
- the potential impact

The target response for an initial acknowledgement is within 7 days.

## In Scope

Security reports are especially useful for:

- webhook verification bypasses
- unsafe handling of `.env` or channel credentials
- message-routing or handoff logic that could cause unsafe auto-replies
- request parsing issues that could crash the service or bypass intended controls

## Out of Scope

The current repo is an MVP and does not yet promise:

- a public bug bounty program
- formal SLA commitments
- support for unsupported forks or modified deployments

## Current Security Notes

- `.env` is intentionally ignored by git and should never be committed
- WhatsApp live sending is disabled by default unless `WHATSAPP_AUTO_REPLY=1`
- High-risk topics such as pricing, contract terms, credit terms, and exclusivity are intended to trigger human handoff
