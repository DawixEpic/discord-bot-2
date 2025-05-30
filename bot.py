import discord
from discord import app_commands
import os
import sys
import traceback

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = 1373253103176122399  # Twój serwer na sztywno

if TOKEN is None:
    print("Błąd: Brak tokena bota w zmiennej środowiskowej DISCORD_TOKEN!")
    sys.exit(1)

class MyClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        guild = discord.Object(id=GUILD_ID)
        await self.tree.sync(guild=guild)
        print(f"Slash commands zarejestrowane dla serwera {GUILD_ID}")

client = MyClient()

@client.tree.command(name="ping", description="Odpowiada pongiem")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")

try:
    client.run(TOKEN)
except Exception:
    print("Bot napotkał błąd podczas uruchamiania:")
    traceback.print_exc()
