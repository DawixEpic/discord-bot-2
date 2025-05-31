import discord
from discord.ext import commands
import os
import traceback

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

GUILD_ID = 1373253103176122399
VERIFY_CHANNEL_ID = 1373258480382771270

@bot.event
async def on_ready():
    print(f"✅ Zalogowano jako {bot.user}")
    guild = bot.get_guild(GUILD_ID)
    if guild is None:
        print("❌ Nie znaleziono guild! Sprawdź GUILD_ID")
        return

    verify_channel = guild.get_channel(VERIFY_CHANNEL_ID)
    if verify_channel is None:
        print("❌ Nie znaleziono kanału weryfikacji! Sprawdź VERIFY_CHANNEL_ID")
        return

    try:
        await verify_channel.send("Bot działa! ✅")
        print("✅ Wysłano testową wiadomość do kanału weryfikacji.")
    except Exception:
        print("❌ Błąd podczas wysyłania wiadomości:")
        traceback.print_exc()

bot.run(os.getenv("TOKEN"))
