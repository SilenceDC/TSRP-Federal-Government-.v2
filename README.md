# TSRP Federal Government — Cloudflare setup

The public website, TSRP AI API, Discord slash-command endpoint and OAuth login are designed to run on Cloudflare Workers with static assets and D1. The existing GitHub Actions vacancy sync remains separate and unchanged.

## Hosting architecture

- **Cloudflare Workers + Static Assets:** serves the existing website and AI API from one origin.
- **Cloudflare D1:** stores Discord OAuth sessions, one-time login states, rate-limit counters, and any future restricted documents.
- **Discord Interactions API:** handles /ask through signed HTTPS requests; no always-on bot process is required.
- **Groq API:** generates source-grounded answers. Groq is a separate provider and may have its own free-tier limits or charges.
- **GitHub Actions:** continues to run the existing vacancy snapshot job.

Cloudflare currently lists a Workers Free allowance of 100,000 requests/day and a 10 ms CPU limit per request. D1 has a free tier for prototyping. Limits can change, and Groq usage is not included in Cloudflare's free tier. See [Cloudflare Workers limits](https://developers.cloudflare.com/workers/platform/limits/) and [D1 FAQ](https://developers.cloudflare.com/d1/reference/faq/).

## One-time Cloudflare setup

1. Create or sign in to a Cloudflare account.
2. Install Node.js LTS on your computer, download this repository, and run **npm install** in its folder.
3. Run **npx wrangler login** and authorize the Cloudflare account you want to use.
4. Run **npm run db:create**. Cloudflare prints a D1 database ID.
5. Replace the placeholder database_id in **wrangler.jsonc** with that exact ID.
6. Run **npm run db:migrate:remote** to create the tables.
7. Add Worker secrets:
   - **npx wrangler secret put GROQ_API_KEY**
   - **npx wrangler secret put DISCORD_CLIENT_SECRET**
   - **npx wrangler secret put DISCORD_PUBLIC_KEY**
8. Set non-secret Worker variables in Cloudflare dashboard (Worker → Settings → Variables) or wrangler.jsonc:
   - **DISCORD_CLIENT_ID** and **DISCORD_APPLICATION_ID** — your dedicated TSRP AI Discord application ID.
   - **DISCORD_GUILD_ID** — the TSRP Discord server ID.
   - **DISCORD_REDIRECT_URI** — after the first deployment, set this to https://YOUR-WORKER.workers.dev/auth/discord/callback using your actual Worker hostname.
   - **WEB_POST_LOGIN_URL** — after the first deployment, set this to the website URL, normally the same Worker origin.
   - **AI_MODEL** — defaults to llama-3.3-70b-versatile.
9. In Discord Developer Portal → General Information, copy the Public Key into Worker secret DISCORD_PUBLIC_KEY.
10. Deploy once with **npm run deploy**. The first deployment creates the workers.dev hostname. The OAuth routes will remain unconfigured until you set the remaining variables.
11. Set DISCORD_REDIRECT_URI and WEB_POST_LOGIN_URL to the actual Worker hostname, then add the exact redirect URI in Discord Developer Portal → OAuth2. OAuth scopes are identify and guilds.members.read.
12. Deploy again with **npm run deploy**.
13. Register the server slash command from the project folder:
    - macOS/Linux: **DISCORD_APPLICATION_ID=... DISCORD_BOT_TOKEN=... DISCORD_GUILD_ID=... npm run discord:register**
    - Windows PowerShell: set those three environment variables first, then run **npm run discord:register**.
14. In Discord Developer Portal → General Information, set Interactions Endpoint URL to https://YOUR-WORKER.workers.dev/discord/interactions. Save after the endpoint is deployed and responding.
15. Test https://YOUR-WORKER.workers.dev/api/health, sign in from the website, then test /ask in the TSRP server.

For Git-based automatic deployments, connect the repository to Cloudflare Workers Builds after the first successful manual deployment. Do not commit API keys or tokens. A Cloudflare API token and account ID are needed if you instead choose to deploy from GitHub Actions.

## Discord bot permissions

Use a dedicated Discord application for TSRP AI. Invite it with the applications.commands scope; it does not need Administrator or a persistent Gateway connection. Set the public key from the Developer Portal as a Worker secret. The Worker verifies Discord's Ed25519 request signature and only accepts commands from the configured TSRP guild.

The slash command is registered by **scripts/register-discord-command.mjs**. Set DISCORD_APPLICATION_ID, DISCORD_BOT_TOKEN and DISCORD_GUILD_ID in your local terminal only when running the registration script; the bot token is not stored in Cloudflare and is not needed for handling interactions once the command is registered.

## Website and login

The existing website AI panel calls the Worker on the same origin. Discord OAuth login redirects back to the site, and the browser receives only an opaque HttpOnly session cookie. Access and refresh tokens remain in D1. The Worker refreshes tokens when needed and checks current Discord membership and roles against Discord before authenticated requests.

## Document security

- Public documents can be listed in data/knowledge/manifest.json with visibility set to public.
- Restricted documents must never be placed in this public GitHub repository or static asset directory.
- To add a restricted document, insert its text into the D1 private_documents table, with a unique document_id, title, and JSON array of exact authorized role IDs in allowed_role_ids_json. Then add only a manifest pointer with visibility set to restricted and that document_id. The Worker checks the D1 role allowlist before reading private text.
- Division roles are not blanket permission grants. Add only the roles explicitly approved for each document.
- Current knowledge files are public only. The Melonly export has not been imported; review and classify it before adding any material.

Known role IDs supplied for TSRP:
- Executive Branch: 1561074965363560568
- Cabinet: 1561075778303828190
- Legislative Branch: 1561076079710576700
- Judicial Branch: 1561076654170832958
- USSS: 1567623961544757349

## Existing vacancy sync

The GitHub Actions vacancy workflow and its DISCORD_TOKEN / GUILD_ID secrets remain unchanged. Do not replace the vacancy bot token with the dedicated AI bot token.

## Troubleshooting

- D1 errors: verify the database ID in wrangler.jsonc and apply migrations remotely.
- OAuth redirect error: the Discord Developer Portal redirect and DISCORD_REDIRECT_URI must match exactly.
- Invalid interaction signature: copy the exact Discord application's Public Key into DISCORD_PUBLIC_KEY.
- Slash command missing: rerun npm run discord:register with the correct application, bot token and guild IDs.
- AI provider errors: verify the Groq key and model name. Cloudflare hosting does not include LLM inference.
