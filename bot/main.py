import asyncio
import os
from collections import defaultdict
from datetime import datetime, timezone

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "").strip()
GUILD_ID = os.getenv("GUILD_ID", "").strip()
WEBSITE_SYNC_URL = os.getenv("WEBSITE_SYNC_URL", "").strip()
WEBSITE_SYNC_SECRET = os.getenv("WEBSITE_SYNC_SECRET", "").strip()

if not DISCORD_TOKEN:
    raise RuntimeError("Missing DISCORD_TOKEN environment variable.")
if not GUILD_ID.isdigit():
    raise RuntimeError("GUILD_ID must be your Discord server ID.")
if not WEBSITE_SYNC_URL:
    raise RuntimeError("Missing WEBSITE_SYNC_URL environment variable.")
if not WEBSITE_SYNC_SECRET:
    raise RuntimeError("Missing WEBSITE_SYNC_SECRET environment variable.")

# Keep these role names and seat counts aligned with the roles in your Discord server.
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
intents.members = True  # Also enable Server Members Intent in the Developer Portal.
bot = commands.Bot(command_prefix="!", intents=intents)
sync_lock = asyncio.Lock()
http_session: aiohttp.ClientSession | None = None


async def publish_positions(guild: discord.Guild) -> None:
    """Publish a complete vacancy snapshot to the website after a role change."""
    async with sync_lock:
        role_by_name = {role.name: role for role in guild.roles}
        counts: dict[int, int] = defaultdict(int)

        # Fetch the full member list so the website always receives a consistent snapshot.
        async for member in guild.fetch_members(limit=None):
            if member.bot:
                continue
            for role in member.roles:
                counts[role.id] += 1

        positions = []
        for branch, branch_positions in POSITIONS:
            for role_name, capacity in branch_positions:
                role = role_by_name.get(role_name)
                filled = counts[role.id] if role else 0
                positions.append({
                    "branch": branch,
                    "title": role_name,
                    "capacity": capacity,
                    "filled": min(filled, capacity),
                    "vacant": max(capacity - filled, 0),
                    "role_found": role is not None,
                    "status": "unconfigured" if role is None else (
                        "open" if filled < capacity else "filled"
                    ),
                })

        payload = {
            "guild_id": str(guild.id),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "positions": positions,
        }
        headers = {
            "Authorization": f"Bearer {WEBSITE_SYNC_SECRET}",
            "Content-Type": "application/json",
        }

        try:
            assert http_session is not None
            async with http_session.post(
                WEBSITE_SYNC_URL, json=payload, headers=headers,
                timeout=aiohttp.ClientTimeout(total=20),
            ) as response:
                response.raise_for_status()
                print(f"Published {len(positions)} positions to website (HTTP {response.status}).")
        except Exception as exc:
            print(f"Website vacancy sync failed: {type(exc).__name__}: {exc}")


async def sync_configured_guild() -> None:
    guild = bot.get_guild(int(GUILD_ID))
    if guild is None:
        try:
            guild = await bot.fetch_guild(int(GUILD_ID))
        except discord.HTTPException as exc:
            print(f"Could not find configured guild: {exc}")
            return
    await publish_positions(guild)


@bot.event
async def on_ready():
    global http_session
    if http_session is None or http_session.closed:
        http_session = aiohttp.ClientSession()
    print(f"Role tracker online as {bot.user} (ID: {bot.user.id})")
    await sync_configured_guild()


@bot.event
async def on_member_join(member: discord.Member):
    if member.guild.id == int(GUILD_ID):
        await publish_positions(member.guild)


@bot.event
async def on_member_remove(member: discord.Member):
    if member.guild.id == int(GUILD_ID):
        await publish_positions(member.guild)


@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    if after.guild.id != int(GUILD_ID):
        return
    before_roles = {role.id for role in before.roles}
    after_roles = {role.id for role in after.roles}
    if before_roles != after_roles:
        await publish_positions(after.guild)


@bot.tree.command(name="ping", description="Check whether the government role tracker is online.")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"Role tracker online. Latency: {round(bot.latency * 1000)} ms",
        ephemeral=True,
    )


@bot.tree.command(name="about", description="Explain what the government role tracker does.")
async def about(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Government Role Tracker",
        description=(
            "I monitor government role assignments and send position availability "
            "to the government website. The website hosts the officials' AI assistant; "
            "AI chat is not provided inside Discord."
        ),
        color=discord.Color.blurple(),
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)


async def close_http_session():
    global http_session
    if http_session and not http_session.closed:
        await http_session.close()


bot.run(DISCORD_TOKEN)
