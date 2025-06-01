import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

CHANNEL_ID = 1378641563868991548  # ID kanału

@bot.event
async def on_ready():
    print(f"✅ Zalogowano jako {bot.user}")
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        embed = discord.Embed(
            title="📦 BOX ⮕ LF",
            description="💰 **85k = 1mln**",
            color=discord.Color.blue()
        )
        await channel.send(embed=embed)
        print("📨 Embed wysłany.")
    else:
        print("❌ Nie znaleziono kanału!")

bot.run(os.getenv("DISCORD_TOKEN"))
