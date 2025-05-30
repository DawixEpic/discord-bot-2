from discord.ext import commands
from discord import app_commands

bot = commands.Bot(command_prefix="!")

@bot.event
async def on_ready():
    await bot.tree.sync()  # synchronizacja komend slash z Discordem
    print(f"Zalogowano jako {bot.user}")

@bot.tree.command(name="444ping", description="Odpowiada Pong!")
async def ping(interaction):
    await interaction.response.send_message("Pong!")

bot.run("TOKEN_TUTAJ")
