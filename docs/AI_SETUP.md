# TSRP AI — Cloudflare deployment and security

The Cloudflare Worker in src/index.js replaces the Python/FastAPI web service and the always-on Discord Gateway bot. The same Worker serves website assets, Discord OAuth, the public AI API and signed Discord interactions.

Follow the one-time setup in the repository README.

## Routes

- GET /api/health — deployment health check.
- POST /api/ask — source-grounded AI response; anonymous users are public-only.
- GET /api/me — checks current Discord login and membership.
- GET /auth/discord and GET /auth/discord/callback — Discord OAuth.
- POST /auth/logout — deletes the server-side session.
- POST /discord/interactions — signed Discord PING and slash-command endpoint.

## Secrets and variables

Store secrets with Wrangler or in Cloudflare Worker Settings → Variables and Secrets. Never commit real values.

Secrets:
- GROQ_API_KEY
- DISCORD_CLIENT_SECRET
- DISCORD_PUBLIC_KEY
- DISCORD_BOT_TOKEN is used locally only when registering or updating the slash command; do not add it as a Worker secret.

Non-secret variables:
- DISCORD_CLIENT_ID
- DISCORD_APPLICATION_ID
- DISCORD_GUILD_ID
- DISCORD_REDIRECT_URI
- WEB_POST_LOGIN_URL
- AI_MODEL

The redirect URI registered in Discord must exactly match DISCORD_REDIRECT_URI. OAuth scopes are identify and guilds.members.read.

## Security model

- OAuth state is one-time and expires after 10 minutes.
- Session identifiers are random, stored server-side in D1, and sent only in Secure, HttpOnly, SameSite=Lax cookies.
- Access and refresh tokens are stored in D1, never in browser JavaScript.
- Current Discord server membership is checked on authenticated requests.
- The website never sends role IDs; the Worker obtains roles directly from Discord.
- Discord interactions are verified with the application's Ed25519 public key and a timestamp freshness check.
- The slash command acknowledges immediately and edits the ephemeral response after the AI request finishes.
- Public static assets may be read by anyone. Never upload restricted plaintext to this repository or static asset directory.

## Private documents

Restricted content is stored in D1, not in the static manifest or public files. The Worker first reads only the private document's title and role allowlist, checks for an intersection with the verified user's live Discord roles, and only then reads the private document text. The manifest contains a document_id pointer, not the private text.

The supplied division roles (Executive, Cabinet, Legislative, Judicial, USSS) do not automatically grant access to every restricted document. Each document must have its own approved role allowlist. Keep presidential, cabinet, and USSS documents restricted to the exact people/roles authorized by TSRP leadership.

## Current limitations

- Only existing reviewed public knowledge files are loaded today.
- The Melonly export has not yet been imported.
- No confidential documents have been copied into D1.
- Discord slash-command registration and Cloudflare account configuration require the administrator steps in the README.
- Groq is a separate AI provider and may have separate usage limits or charges.
