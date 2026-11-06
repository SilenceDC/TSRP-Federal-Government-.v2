"""Discord slash-command entry point for TSRP AI."""
from __future__ import annotations

import os
import discord
from discord import app_commands

from tsrp_ai.answer import answer_question

# Use a dedicated AI bot application/token. The vacancy snapshot job is a separate bot.
TOKEN = os.getenv("TSRP_AI_DISCORD_TOKEN", "").strip()
if not TOKEN:
    raise RuntimeError("Set the TSRP_AI_DISCORD_TOKEN environment variable.")

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@tree.command(name="ask", description="Ask TSRP AI about government information.")
@app_commands.describe(question="Your question about TSRP government or procedures")
async def ask(interaction: discord.Interaction, question: str):
    await interaction.response.defer(thinking=True, ephemeral=True)
    member_roles = getattr(interaction.user, "roles", [])
    role_ids = {str(role.id) for role in member_roles}
    response = await answer_question(question, requester_role_ids=role_ids)
    await interaction.followup.send(response[:1900], ephemeral=True)


@client.event
async def on_ready():
    await tree.sync()
    print(f"TSRP AI Discord assistant ready as {client.user}")


client.run(TOKEN)
