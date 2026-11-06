import json
import os
from datetime import datetime, timezone
from pathlib import Path

import discord

TOKEN = os.environ.get("DISCORD_TOKEN", "").strip()
GUILD_ID = os.environ.get("GUILD_ID", "").strip()

if not TOKEN:
    raise RuntimeError("Add the DISCORD_TOKEN repository secret.")
if not GUILD_ID.isdigit():
    raise RuntimeError("Add GUILD_ID as the numeric Discord server ID.")

# Role names must match your Discord server exactly. Adjust seat capacities here.
POSITIONS = [
    ("Executive Branch", [
        ("President", 1), ("Vice President", 1), ("Chief of Staff", 1),
        ("Press Secretary", 1), ("White House Staff", 3),
    ]),
    ("Cabinet", [
        ("Attorney General", 1), ("Secretary of State", 1),
        ("Secretary of Defense", 1), ("Secretary of Treasury", 1),
        ("Secretary of Homeland Security", 1),
    ]),
    ("Legislative Branch", [
        ("Speaker of the House", 1), ("Representative", 5),
        ("Senate Majority Leader", 1), ("Senator", 5),
    ]),
    ("Judicial Branch", [
        ("Chief Justice", 1), ("Associate Justice", 2), ("Federal Judge", 3),
    ]),
]

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    try:
        guild = client.get_guild(int(GUILD_ID))
        if guild is None:
            guild = await client.fetch_guild(int(GUILD_ID))

        role_by_name = {role.name: role for role in guild.roles}
        counts = {}
        async for member in guild.fetch_members(limit=None):
            if member.bot:
                continue
            for role in member.roles:
                counts[role.id] = counts.get(role.id, 0) + 1

        positions = []
        for branch, entries in POSITIONS:
            for role_name, capacity in entries:
                role = role_by_name.get(role_name)
                filled_count = counts.get(role.id, 0) if role else 0
                positions.append({
                    "branch": branch,
                    "title": role_name,
                    "capacity": capacity,
                    "filled": min(filled_count, capacity),
                    "vacant": max(capacity - filled_count, 0),
                    "role_found": role is not None,
                    "status": "unconfigured" if role is None else (
                        "open" if filled_count < capacity else "filled"
                    ),
                })

        output = {
            "guild_id": str(guild.id),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "positions": positions,
        }
        target = Path("data/positions.json")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(output, indent=2) + "\\n", encoding="utf-8")
        print(f"Wrote {len(positions)} government positions to {target}.")
    except Exception as exc:
        print(f"Vacancy sync failed: {type(exc).__name__}: {exc}")
        raise
    finally:
        await client.close()


client.run(TOKEN)
