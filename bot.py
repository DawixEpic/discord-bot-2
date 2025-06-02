import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()  # wczytaj zmienne środowiskowe z pliku .env

intents = discord.Intents.default()
intents.members = True
intents.message_content = True  # jeśli chcesz reagować na treść wiadomości (opcjonalne)

bot = commands.Bot(command_prefix="!", intents=intents)

GUILD_ID = 1373253103176122399
ROLE_ID = 1373275307150278686
VERIFY_CHANNEL_ID = 1373258480382771270
TICKET_CHANNEL_ID = 1373305137228939416
TICKET_CATEGORY_ID = 1373277957446959135
LOG_CHANNEL_ID = 1374479815914291240
ADMIN_ROLE_ID = 1373275898375176232

SERVER_OPTIONS = {
    "𝐂𝐑𝐀𝐅𝐓𝐏𝐋𝐀𝐘": {
        "𝐆𝐈𝐋𝐃𝐈𝐄": ["Elytra", "Buty flasha", "Miecz 6", "Kasa", "Shulker s2", "Shulker totemów"],
        "𝐁𝐎𝐗𝐏𝐕𝐏": ["Set 25", "Miecz 25", "Kilof 25", "Kasa"]
    },
    "𝐀𝐍𝐀𝐑𝐂𝐇𝐈𝐀": {
        "𝐋𝐈𝐅𝐄𝐒𝐓𝐄𝐀𝐋": ["Kasa", "Anarchiczny set 2", "Anarchiczny set 1", "Anarchiczny miecz", "Zajęczy miecz", "Totem ułaskawienia", "Excalibur"],
        "𝐁𝐎𝐗𝐏𝐕𝐏": ["Kasa", "Excalibur", "Totem ułaskawienia", "Sakiewka"]
    },
    "𝐑𝐀𝐏𝐘": {
        "𝐋𝐈𝐅𝐄𝐒𝐓𝐄𝐀𝐋": ["nie dostępne", "nie dostępne", "nie dostępne"],
        "𝐁𝐎𝐗𝐏𝐕𝐏": ["Kasa", "Miecz 35", "Set 35"]
    },
    "𝐏𝐘𝐊𝐌𝐂": {
        "𝐋𝐈𝐅𝐄𝐒𝐓𝐄𝐀𝐋": ["Kasa", "Buda", "Love swap", "Klata meduzy"],
        "𝐁𝐎𝐗𝐏𝐕𝐏": ["nie dostępne", "nie dostępne", "nie dostępne"]
    }
}

# -- tu reszta klas jak w Twoim kodzie -- WeryfikacjaButton, CloseButton, AmountModal, PurchaseView, OrderActionView, TicketButton --

# (Przepisz dokładnie tak jak masz, nic nie zmieniaj w nich, jeśli chcesz mogę też je wkleić)

@bot.event
async def on_ready():
    print(f"✅ Zalogowano jako {bot.user}")
    bot.add_view(WeryfikacjaButton())
    bot.add_view(TicketButton())
    bot.add_view(CloseButton())
    bot.add_view(OrderActionView(None, None, None, None))

    guild = bot.get_guild(GUILD_ID)
    if guild:
        verify_channel = guild.get_channel(VERIFY_CHANNEL_ID)
        if verify_channel:
            messages = await verify_channel.history(limit=20).flatten()
            if not any("Kliknij przycisk aby się zweryfikować:" in (m.content or "") for m in messages):
                embed = discord.Embed(
                    title="🔒 Weryfikacja dostępu",
                    description="Kliknij przycisk poniżej, aby się zweryfikować i uzyskać dostęp do systemu zakupów na różnych serwerach Minecraft.",
                    color=discord.Color.green()
                )
                await verify_channel.send(embed=embed, view=WeryfikacjaButton())

        ticket_channel = guild.get_channel(TICKET_CHANNEL_ID)
        if ticket_channel:
            messages = await ticket_channel.history(limit=20).flatten()
            if not any("Kliknij przycisk aby utworzyć ticket:" in (m.content or "") for m in messages):
                embed = discord.Embed(
                    title="🎫 Tworzenie ticketów",
                    description="Kliknij przycisk poniżej, aby utworzyć ticket i złożyć zamówienie.",
                    color=discord.Color.blue()
                )
                await ticket_channel.send(embed=embed, view=TicketButton())

# Pobierz token z .env lub z systemu, jeśli brak - wyrzuć błąd
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise RuntimeError("Brak tokena bota! Ustaw zmienną środowiskową TOKEN lub dodaj plik .env z TOKEN=...")

bot.run(TOKEN)
