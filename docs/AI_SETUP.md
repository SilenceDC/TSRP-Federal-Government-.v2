# TSRP AI setup

TSRP AI is being added as a separate service so the existing static website and vacancy synchronizer remain intact.

## Current components
- Discord bot slash command: `/ask` (run `python -m bot.assistant`).
- Public website API: FastAPI `web:app`, with `GET /api/health` and `POST /api/ask`.
- Knowledge base: Markdown files listed in `data/knowledge/manifest.json`.
- Source-grounded answers with source titles and an explicit "not found" response.

## Required secrets and environment
Set these in the hosting provider's secret/environment settings. Never commit real values:
- `TSRP_AI_DISCORD_TOKEN`: token for a dedicated TSRP AI Discord bot application. Keep it separate from the vacancy snapshot bot token.
- `GROQ_API_KEY`: Groq API key used server-side.
- `AI_MODEL` (optional): defaults to `llama-3.3-70b-versatile`.
- `AI_BASE_URL` (optional): defaults to Groq's OpenAI-compatible API.
- `WEB_ALLOWED_ORIGINS`: comma-separated website origins allowed to call the API, e.g. the GitHub Pages origin.

The AI bot needs permission to use application commands in the server. It does not need Administrator permission or the privileged Members intent for the current role-check implementation.

## Deployment
The included `render.yaml` defines separate web and worker services. Connect the repository to Render, configure the secret values when prompted, and deploy. The website API is not live until the web service is deployed and its public URL is configured in the static website frontend.

## Knowledge and confidentiality
- Only documents marked `visibility: public` are currently included in the public repository.
- A restricted document must have an explicit `allowed_role_ids` allowlist in the manifest. The code checks this allowlist before reading the file.
- The supplied Executive, Cabinet, Legislative, Judicial, and USSS division IDs are recorded for reference only; they are not document permissions.
- Do not upload private Melonly exports, presidential/cabinet/USSS confidential records, personal data, API keys, or bot tokens to this public repository.
- Website requests are anonymous and can retrieve public documents only. Discord requests use the invoking member's current Discord roles for per-document allowlist checks.
- For restricted material, add a document only in a private repository or private storage location and explicitly authorize the exact role IDs that may read it. Do not rely on prompt instructions as access control.

## Add knowledge
1. Export the relevant Melonly document as text or Markdown.
2. Review it for personal data, secrets, and confidential content.
3. Put public material in `data/knowledge/public/`.
4. Add its title, relative path, visibility, and allowlist to `data/knowledge/manifest.json`.
5. Keep restricted material outside this public repository until a private storage integration is configured.

## Important limitation
This initial release does not implement Discord OAuth login for the website. The website API is therefore public-knowledge-only. Do not expose private document search on the website until OAuth identity verification and server-side role checks are implemented.
