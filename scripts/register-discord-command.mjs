const { DISCORD_APPLICATION_ID, DISCORD_BOT_TOKEN, DISCORD_GUILD_ID } = process.env;
if (!DISCORD_APPLICATION_ID || !DISCORD_BOT_TOKEN || !DISCORD_GUILD_ID) {
  throw new Error("Set DISCORD_APPLICATION_ID, DISCORD_BOT_TOKEN, and DISCORD_GUILD_ID before registering the command.");
}
const endpoint = "https://discord.com/api/v10/applications/" + DISCORD_APPLICATION_ID + "/guilds/" + DISCORD_GUILD_ID + "/commands";
const response = await fetch(endpoint, {
  method: "PUT",
  headers: { Authorization: "Bot " + DISCORD_BOT_TOKEN, "content-type": "application/json" },
  body: JSON.stringify([{
    name: "ask",
    description: "Ask TSRP AI about government information.",
    options: [{ type: 3, name: "question", description: "Your question about TSRP government or procedures", required: true, max_length: 1500 }]
  }])
});
const result = await response.json();
if (!response.ok) throw new Error("Discord command registration failed (" + response.status + "): " + JSON.stringify(result));
console.log("Registered /ask for the configured TSRP server.");
