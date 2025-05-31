import discord
from discord import app_commands
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True
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

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    await interaction.response.send_message(f"Wystąpił błąd: {error}", ephemeral=True)

TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN is None:
    raise ValueError("Token bota nie został ustawiony. Ustaw zmienną środowiskową DISCORD_TOKEN.")

if __name__ == "__main__":
    bot.run(TOKEN)
