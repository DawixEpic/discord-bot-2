import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# ID kanału ticketów (przycisk prowadzi tutaj)
TICKET_CHANNEL_ID = 1373305137228939416

# Lista ofert (kanał_id, treść oferty)
OFFERS = [
    (1373266589310517338, """🛒 Oferta itemów na sprzedaż
:Elytra: Elytra — Cena: 12zł
:Buty: Buty flasha — Cena: 5zł
:Miecz: Miecz 6 — Cena: 3zł

:Shulker: Shulker s2 — Cena: 7zł
:Shulker: Shulker totemów — Cena: 6zł

Kliknij przycisk poniżej, aby otworzyć ticket i dokonać zakupu!"""),

    (1373267159576481842, """🛒 Oferta itemów na sprzedaż
:Klata: Set 25 — Cena: 30zł
:Miecz: Miecz 25 — Cena: 25zł
:Kilof: Kilof 25 — Cena: 10zł
💸 1mln$ — Cena: 18zł

Kliknij przycisk poniżej, aby otworzyć ticket i dokonać zakupu!"""),

    (1373268875407396914, """🛒 Oferta itemów na sprzedaż
💵 4,5k$ — Cena: 1zł
💸 50k$ — Cena: 12zł 
💸 550k$ — Cena: 130zł
:ANA2: Anarchiczny set 2 — Cena: 28zł
:Klata: Anarchiczny set 1 — Cena: 9zł
⚔️ MIECZE:
:Miecz: Anarchiczny miecz — Cena: 3zł
🎉 EVENTÓWKI:
:MieczZajeczy: Zajęczy miecz — Cena: 65zł
:Totem: Totem ułaskawienia — Cena: 630zł 
:Excalibur: Excalibur — Cena: 370zł

Kliknij przycisk poniżej, aby otworzyć ticket i dokonać zakupu!"""),

    (1373270295556788285, """🛒 Oferta itemów na sprzedaż
💵 50k$ — Cena: 1zł
💸 1mln$ — Cena: 33zł 
🎉 EVENTOWKI:
:Excalibur: Excalibur — Cena: 111zł 
:Totem: Totem ułaskawienia — Cena: 270zł 
:Sakiewka: Sakiewka — Cena: 50zł 

Kliknij przycisk poniżej, aby otworzyć ticket i dokonać zakupu!"""),

    (1378641563868991548, """BOX ⮕ LF
💸 85k = 1mln"""),

    (1373273108093337640, """🛒 Oferta itemów na sprzedaż
💸 10mld$ — Cena: 2zł 
:Miecz: Miecz 35 — Cena: 65zł 
:Klata: Set 35 — Cena: 90zł 

Kliknij przycisk poniżej, aby otworzyć ticket i dokonać zakupu!"""),

    (1374380939970347019, """🛒 Oferta itemów na sprzedaż
💵 15k$ — Cena: 1zł
:Buda: Buda — Cena: 30zł
:LoveSwap: Love swap — Cena: 100zł
:KlataMeduzy: Klata meduzy — Cena: 140zł

Kliknij przycisk poniżej, aby otworzyć ticket i dokonać zakupu!"""),
]

class TicketButton(discord.ui.View):
    def __init__(self, guild_id):
        super().__init__()
        self.add_item(discord.ui.Button(
            label="🎫 Otwórz ticket",
            style=discord.ButtonStyle.link,
            url=f"https://discord.com/channels/{guild_id}/{TICKET_CHANNEL_ID}"
        ))

@bot.event
async def on_ready():
    print(f"✅ Zalogowano jako {bot.user}")

    for channel_id, message_text in OFFERS:
        channel = bot.get_channel(channel_id)
        if not channel:
            print(f"❌ Nie znaleziono kanału o ID {channel_id}")
            continue

        guild_id = channel.guild.id
        view = TicketButton(guild_id)

        embed = discord.Embed(
            description=message_text,
            color=discord.Color.green()
        )

        try:
            await channel.send(embed=embed, view=view)
            print(f"📨 Wysłano do kanału {channel.name}")
        except Exception as e:
            print(f"❌ Błąd przy wysyłaniu do kanału {channel_id}: {e}")

bot.run(os.getenv("DISCORD_TOKEN"))
