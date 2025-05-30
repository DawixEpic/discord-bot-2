import discord
from discord import app_commands
from discord.ext import commands

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Zalogowano jako {bot.user} (ID: {bot.user.id})')
    try:
        synced = await bot.tree.sync()
        print(f'Zsynchronizowano {len(synced)} komend slash.')
    except Exception as e:
        print(f'Błąd synchronizacji komend: {e}')

@bot.tree.command(name="ping", description="Sprawdź czy bot odpowiada")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")

import os
TOKEN = os.getenv("DISCORD_TOKEN")

bot.run(TOKEN)
