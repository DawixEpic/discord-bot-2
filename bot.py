import discord
from discord import app_commands
import os

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("1373253103176122399"))  # ID serwera (guild) jako int

class MyClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # Synchronizacja tylko na konkretnym serwerze - działa od razu
        guild = discord.Object(id=GUILD_ID)
        await self.tree.sync(guild=guild)

client = MyClient()

@client.tree.command(name="ping", description="Odpowiada pongiem")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")

if __name__ == "__main__":
    client.run(TOKEN)
