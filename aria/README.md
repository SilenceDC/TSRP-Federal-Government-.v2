# ARIA — TSRP Government AI

ARIA is the planned knowledge assistant for the fictional TSRP roleplay community.

## First milestone: knowledge foundation

This directory establishes a source-controlled, public-safe knowledge base and an example access policy. It does not yet deploy a working chatbot or connect to Melonly.

### Knowledge sources

- `knowledge/public/government-directory.md`: facts supplied for the public government directory.
- Future approved exports from Melonly should be added only after their confidentiality level has been reviewed.

### Security model

1. Keep this repository's public content strictly non-confidential.
2. Never commit Melonly exports marked confidential, Discord bot tokens, AI provider keys, OAuth secrets, or user data.
3. The example policy in `config/access-policy.example.json` is a template, not an active authorization system.
4. Before restricted documents are indexed, configure actual Discord role IDs and enforce authorization in a trusted server-side service on every request.
5. Fail closed: if identity, role membership, policy, or document classification cannot be verified, do not return restricted content.
6. Do not rely on prompt instructions, hidden frontend controls, or role names supplied by a user as access control.

## Planned architecture

- Discord interaction: slash command such as `/ask`.
- Trusted backend: verifies the Discord interaction signature and obtains the member's server roles.
- Knowledge retrieval: searches only documents the verified member is authorized to access.
- AI provider: receives only the permitted excerpts needed to answer.
- Response: includes document title/section references and says when the approved knowledge base does not contain an answer.
- Website chat: later uses the same backend and a separately verified login/session.

## Current status

- [x] Name selected: ARIA.
- [x] Initial public government directory documented.
- [x] Example access-policy template added.
- [ ] Confirm exact Discord role IDs for access groups.
- [ ] Select and configure a private backend/hosting environment.
- [ ] Select AI provider and store its key as a server-side secret.
- [ ] Add Melonly export ingestion and document classification.
- [ ] Implement and test Discord authorization and `/ask`.
- [ ] Add website chat after authentication is in place.

## Important

This is a roleplay community project, not a real government service. The directory records only the information supplied by the community owner; it does not invent legal powers, procedures, or job duties.
