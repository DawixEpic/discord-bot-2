import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

CHANNEL_ID = 1378641563868991548  # ← tutaj wpisz ID kanału, gdzie ma wysłać wiadomość

@bot.event
async def on_ready():
    print(f"✅ Zalogowano jako {bot.user}")
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send("BOX⮕LF
85k=1mln")
    else:
        print("❌ Nie znaleziono kanału!")

bot.run(os.getenv("DISCORD_TOKEN"))  # Lub podaj token bezpośrednio
# bot.run("TWÓJ_TOKEN_TUTAJ")
