# TSRP Federal Government Website — Free Hosting Setup

This repository uses a free, scheduled Discord-to-website vacancy sync. It does **not** require Render or a paid always-on bot host.

## Free architecture

- **GitHub Pages:** serves the public static website.
- **GitHub Actions:** starts a short-lived Python job every 5 minutes.
- **Discord bot token:** lets that job read member roles.
- **`data/positions.json`:** the job updates this public data file; the website reads it to display current vacancies.
- **Groq:** may be used separately for the website AI through its free API tier, subject to Groq's current rate limits. Never expose `GROQ_API_KEY` in browser JavaScript.

Because GitHub Actions runs on a schedule, vacancies are refreshed approximately every 5 minutes, not instantly. Scheduled workflows run from the repository's default branch, so merge this setup before expecting the schedule to start. This repository is public, so standard GitHub-hosted runners are free for public repositories under GitHub's current policy.

## One-time setup

1. In Discord Developer Portal, enable **Server Members Intent** for the bot.
2. Invite the bot to your server with permission to view the server and members. It does not need Administrator.
3. In GitHub, open **Settings → Secrets and variables → Actions → New repository secret** and add:
   - `DISCORD_TOKEN` — the bot token.
   - `GUILD_ID` — your Discord server ID (enable Developer Mode in Discord, then right-click the server and Copy Server ID).
4. In `bot/snapshot.py`, make sure every role name and seat capacity matches your server's actual roles.
5. Merge this pull request into the default branch.
6. In GitHub, open **Settings → Pages** and select **Deploy from a branch**, choose `main` and `/ (root)`, then save. If Pages is already enabled, keep the existing configuration.
7. Open **Actions → Sync Discord government vacancies → Run workflow** once to test the first sync. After that, the schedule runs every 5 minutes.

The workflow needs repository Actions permission to write contents. It commits only when vacancy data changes.

## Website AI

The existing website is static HTML and does not currently include a secure AI backend or official-account login. To add an officials-only AI chatbot, we still need a server-side endpoint and authentication. A Groq key must be stored as a server-side secret (never in `index.html`). We should configure that separately rather than exposing the key.

## Security and privacy

- Never commit bot tokens, Groq keys, or other secrets.
- The published JSON contains role totals and vacancy counts only; it does not publish member names.
- Do not give the bot Administrator permission.
- If the token is exposed, reset it immediately in the Discord Developer Portal.

## Troubleshooting

- **No workflow runs:** merge the pull request first; scheduled workflows run from the default branch.
- **Missing members / empty counts:** enable Server Members Intent in both the Developer Portal and the script, then verify the bot can access the server.
- **Role says unconfigured:** the role name in `bot/snapshot.py` does not exactly match a Discord role.
- **Website does not update:** confirm GitHub Pages is publishing the `main` branch root and check the latest workflow run.
