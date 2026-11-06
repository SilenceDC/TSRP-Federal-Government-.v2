# TSRP Federal Government Website — Free Hosting Setup

This repository uses a free, scheduled Discord-to-website vacancy sync. It does **not** require Render or a paid always-on bot host.

## Free architecture

- **GitHub Pages:** serves the public static website.
- **GitHub Actions:** starts a short-lived Python job every 5 minutes.
- **Discord bot token:** lets that job read member roles.
- **`data/positions.json`:** the job updates this public data file; the website reads it to display current vacancies.
- **Groq:** powers TSRP AI through its OpenAI-compatible API. The key stays server-side.

Because GitHub Actions runs on a schedule, vacancies are refreshed approximately every 5 minutes, not instantly; GitHub may delay scheduled runs during busy periods. Scheduled workflows run from the repository's default branch, so merge this setup before expecting the schedule to start. This repository is public, so standard GitHub-hosted runners are free for public repositories under GitHub's current policy. GitHub may automatically disable scheduled workflows in a public repository after 60 days without repository activity, so check Actions periodically.

## Existing vacancy sync setup

1. In Discord Developer Portal, enable **Server Members Intent** for the vacancy bot.
2. Invite the bot to your server with permission to view the server and members. It does not need Administrator.
3. In GitHub, open **Settings → Secrets and variables → Actions → New repository secret** and add:
   - `DISCORD_TOKEN` — the vacancy bot token.
   - `GUILD_ID` — your Discord server ID.
4. In `bot/snapshot.py`, make sure every role name and seat capacity matches your server's actual roles.
5. Merge the existing vacancy-sync setup into the default branch.
6. In GitHub, open **Settings → Pages** and select **Deploy from a branch**, choose `main` and `/ (root)`, then save. If Pages is already enabled, keep the existing configuration.
7. Open **Actions → Sync Discord government vacancies → Run workflow** once to test the first sync.

The workflow needs repository Actions permission to write contents. It commits only when vacancy data changes.

## TSRP AI

The TSRP AI foundation is merged into `main`; the Discord role-access upgrade is proposed in `feature/tsrp-discord-role-access`:

- Discord slash command: `/ask`.
- FastAPI website endpoint: `POST /api/ask`, health endpoint `GET /api/health`, and Discord OAuth identity endpoint `GET /api/me`.
- Permission-aware document retrieval and source-grounded answers.
- A public knowledge manifest and the government overview supplied for this project.
- A Render blueprint for separate web API and Discord worker services.

See [docs/AI_SETUP.md](docs/AI_SETUP.md) for deployment and configuration, including Discord OAuth and the website AI chat. The AI services are separate from the vacancy sync and do not replace it.

## Security and privacy

- Never commit bot tokens, Groq keys, or other secrets.
- The published vacancy JSON contains role totals and vacancy counts only; it does not publish member names.
- Do not give bots Administrator permission.
- If a token is exposed, reset it immediately in the Discord Developer Portal.
- This is a fictional roleplay community, not a real government agency.
- Website AI role access requires the Discord OAuth configuration described in `docs/AI_SETUP.md`; until it is configured, anonymous requests remain public-only.
- Never put confidential Melonly exports or restricted presidential, cabinet, or USSS documents in this public repository.

## Troubleshooting

- **No vacancy workflow runs:** scheduled workflows run from the default branch; check Actions and repository permissions.
- **Missing members / empty counts:** enable Server Members Intent in both the Developer Portal and the script, then verify the bot can access the server.
- **Role says unconfigured:** the role name in `bot/snapshot.py` does not exactly match a Discord role.
- **Website does not update:** confirm GitHub Pages is publishing the `main` branch root and check the latest workflow run.
