import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# ID kanału docelowego
CHANNEL_ID = 1378641563868991548

@bot.event
async def on_ready():
    print(f"✅ Zalogowano jako {bot.user}")
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send("**BOX⮕LF**\n85k=1mln")
        print("📨 Wiadomość wysłana.")
    else:
        print("❌ Nie znaleziono kanału!")

# Start bota z tokenem z Railway (ustawionym jako zmienna środowiskowa)
bot.run(os.getenv("DISCORD_TOKEN"))
