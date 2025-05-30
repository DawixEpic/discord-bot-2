import discord
from discord import app_commands
import os

TOKEN = os.getenv("DISCORD_TOKEN")  # Zakładam, że na Railway masz ustawiony sekret DISCORD_TOKEN

class MyClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # Zarejestruj slash commands globalnie (można też na guildę)
        await self.tree.sync()

client = MyClient()

@client.tree.command(name="ping", description="Odpowiada pongiem")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")

if __name__ == "__main__":
    client.run(TOKEN)
