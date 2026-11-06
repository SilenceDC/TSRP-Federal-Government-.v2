# TSRP Federal Government Website and Discord Role Tracker

This repository contains the government website and a Discord bot that keeps the website's open-position list synchronized with Discord role assignments.

## Responsibilities

- **Website:** displays available government positions and hosts the AI chatbot for authenticated government officials.
- **Discord bot:** reads member role assignments and publishes vacancy snapshots to the website. It does not provide an AI chatbot in Discord.

## Discord bot setup

1. Create a Discord application and bot, invite it to the server, and enable **Server Members Intent** in the Discord Developer Portal.
2. Configure these environment variables in the bot host:
   - `DISCORD_TOKEN`
   - `GUILD_ID`
   - `WEBSITE_SYNC_URL` — the website's authenticated vacancy-sync endpoint (for example `/api/discord/positions`).
   - `WEBSITE_SYNC_SECRET` — a long random secret shared only by the bot host and website server.
3. Keep the `POSITIONS` role names and seat capacities in `bot/main.py` aligned with the actual Discord roles.
4. Deploy as a persistent background worker with `python bot/main.py`.

The bot publishes a complete vacancy snapshot on startup, when a member joins or leaves, and whenever a member's roles change. The website endpoint must accept an authenticated JSON `POST` with a `positions` array and persist the latest snapshot. The bot sends role counts and vacancy totals, not member names.

Example position item:

```json
{
  "branch": "Executive Branch",
  "title": "President",
  "capacity": 1,
  "filled": 1,
  "vacant": 0,
  "role_found": true,
  "status": "filled"
}
```

## Website AI chatbot

The website's server-side chatbot should call Groq using `GROQ_API_KEY` stored only in the website host's environment. Do not put the Groq key in browser code or the Discord bot. Protect the chatbot with website official-account authentication and server-side rate limits.

## Security

Never commit real tokens, API keys, or shared secrets. GitHub repository secrets do not automatically configure environment variables on Render or another hosting provider.
