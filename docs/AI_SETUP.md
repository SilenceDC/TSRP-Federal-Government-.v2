# TSRP AI setup

TSRP AI is a separate service so the existing static website and vacancy synchronizer remain intact.

## Components
- Discord bot slash command: `/ask` (run `python -m bot.assistant`).
- FastAPI website API: `GET /api/health`, `POST /api/ask`, and `GET /api/me`.
- Discord OAuth routes: `GET /auth/discord`, `GET /auth/discord/callback`, and `POST /auth/logout`.
- Knowledge base: Markdown files listed in `data/knowledge/manifest.json`.

## Required environment variables
Set these in the hosting provider. Never commit real values:
- `TSRP_AI_DISCORD_TOKEN`: dedicated AI bot token.
- `GROQ_API_KEY`: server-side model API key.
- `AI_MODEL` (optional): defaults to `llama-3.3-70b-versatile`.
- `AI_BASE_URL` (optional): defaults to Groq's OpenAI-compatible API.
- `WEB_ALLOWED_ORIGINS`: exact website origin(s), comma-separated.
- `SESSION_SECRET`: long random secret used to sign opaque session cookies. Render can generate this.
- `DISCORD_CLIENT_ID` and `DISCORD_CLIENT_SECRET`: OAuth2 application credentials for the TSRP AI Discord application.
- `DISCORD_GUILD_ID`: the TSRP Discord server ID.
- `DISCORD_REDIRECT_URI`: exact callback URL, `https://YOUR-API-HOST/auth/discord/callback`; register this exact URL in Discord Developer Portal.
- `WEB_POST_LOGIN_URL`: absolute website URL to return to after login.

## Configure Discord OAuth
1. Open the Discord Developer Portal for the dedicated TSRP AI application.
2. Under OAuth2, add the exact `DISCORD_REDIRECT_URI` as a redirect.
3. Use the OAuth2 scopes `identify` and `guilds.members.read`. The app uses the returned access token to verify current membership and fetch the member's live role IDs from the configured server.
4. Invite the AI bot to the TSRP server with application-command permissions. Do not grant Administrator.
5. In Render, set every environment variable above. Do not put client secrets or tokens in frontend JavaScript.

The login flow uses a one-time state value and an HttpOnly, Secure, SameSite=None cookie. OAuth access tokens remain in the API process, not in the browser cookie. Member roles are fetched from Discord on every authenticated ask; role IDs supplied by the browser are never trusted. The current session store is in-memory and single-instance: restarting the API logs users out, and multiple API instances require a shared server-side session store (for example Redis).

## Website integration
Add a visible "Sign in with Discord" link to `https://YOUR-API-HOST/auth/discord`. For API calls from the website, use `fetch` with `credentials: "include"` and JSON content type. Call `GET /api/me` to show login state. Anonymous users may ask public questions; authenticated members are checked against their current Discord roles. Cross-site cookies can be blocked by some browser privacy settings; a same-site custom domain for the website and API is preferable.

Example browser request:

```js
const response = await fetch("https://YOUR-API-HOST/api/ask", {
  method: "POST",
  credentials: "include",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ question: "What does the Executive Branch do?" })
});
const data = await response.json();
```

## Document access rules
- Each manifest entry must explicitly specify `visibility` and `allowed_role_ids`.
- Public documents use `visibility: "public"`.
- Restricted documents use `visibility: "restricted"` and an explicit allowlist of exact Discord role IDs. The retrieval code authorizes a document before opening or scoring its contents.
- Division roles supplied for TSRP are: Executive `1561074965363560568`, Cabinet `1561075778303828190`, Legislative Branch `1561076079710576700`, Judicial Branch `1561076654170832958`, and USSS `1567623961544757349`. They are membership/grouping roles, not automatic permission grants; add only the role IDs approved for each document.
- Discord `/ask` uses the invoking member's live roles. Website `/api/ask` uses live roles fetched through OAuth. Anonymous website requests are public-only.
- **This GitHub repository is public.** Never put confidential or restricted plaintext documents in it: GitHub visitors can read files directly, regardless of API authorization. Restricted documents must be stored in a private repository or private storage provider and retrieved server-side only. That private storage adapter is not included in this change.
- The Melonly export has not yet been imported. Only reviewed, non-confidential information currently present in the public knowledge base can be answered.

## Deploy
The Render blueprint defines a web API and a separate Discord worker. Connect the repository to Render, set the variables, deploy both services, then add the website sign-in link and API URL to the static site. The API is not live until deployment is complete.
