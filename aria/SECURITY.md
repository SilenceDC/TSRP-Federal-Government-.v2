# ARIA security requirements

The current repository is public. Treat every committed file as readable by anyone.

## Do not commit

- Confidential Melonly exports or private government documents.
- Discord bot tokens, AI API keys, OAuth client secrets, signing secrets, or session cookies.
- Personal information, private messages, or member records.

## Required before restricted-document support

- Use private object storage or a private repository for confidential source files.
- Keep the production access policy and credentials in server-side secret storage.
- Verify Discord interaction signatures and guild membership on the backend.
- Resolve role IDs from the verified guild member object, never from user-supplied text.
- Authorize each document before retrieval. Filtering results after sending all documents to the model is not sufficient.
- Do not expose confidential document text in logs, analytics, error messages, browser responses, or public citations.
- Test unauthorized, missing-role, stale-role, API-failure, and cross-guild cases.
- Keep public and restricted indexes physically or logically separated with enforced access checks.

The example policy in `config/access-policy.example.json` is intentionally disabled until the actual role IDs and backend enforcement have been configured.
