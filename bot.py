import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

TICKET_CHANNEL_ID = 1373305137228939416  # ID kanału ticketów

# Słownik z ID kanałów i opisami ofert
CHANNEL_MESSAGES = {
    1373266589310517338: """
<:Elytra:1374797373406187580> **Elytra** — 12zł  
<:Buty:1374796797222064230> **Buty flasha** — 5zł  
<:Miecz:1374791139462352906> **Miecz 6** — 3zł  
<:Shulker:1374795916531335271> **Shulker s2** — 7zł  
<:Shulker:1374795916531335271> **Shulker totemów** — 6zł
""",
    1373267159576481842: """
<:Klata:1374793644246306866> **Set 25** — 30zł  
<:Miecz:1374791139462352906> **Miecz 25** — 25zł  
<:Kilof:1374795407493959751> **Kilof 25** — 10zł  
💸 **1mln$** — 18zł
""",
    1373268875407396914: """
💵 **4,5k$** — 1zł  
💸 **50k$** — 12zł  
💸 **550k$** — 130zł  
<:ANA2:1374799017359314944> **Anarchiczny set 2** — 28zł  
<:Klata:1374793644246306866> **Anarchiczny set 1** — 9zł  

⚔️ **MIECZE**  
<:Miecz:1374791139462352906> **Anarchiczny miecz** — 3zł  

🎉 **EVENTÓWKI**  
<:MieczZajeczy:1375486003891929088> **Zajęczy miecz** — 65zł  
<:Totem:1374788635211206757> **Totem ułaskawienia** — 630zł  
<:Excalibur:1374785662191927416> **Excalibur** — 370zł
""",
    1373270295556788285: """
💵 **50k$** — 1zł  
💸 **1mln$** — 33zł  

🎉 **EVENTÓWKI**  
<:Excalibur:1374785662191927416> **Excalibur** — 111zł  
<:Totem:1374788635211206757> **Totem ułaskawienia** — 270zł  
<:Sakiewka:1374799829120716892> **Sakiewka** — 50zł
""",
    1378641563868991548: """
BOX ⮕ LF  
💸 **85k = 1mln**
""",
    1373273108093337640: """
💸 **10mld$** — 2zł  
<:Miecz:1374791139462352906> **Miecz 35** — 65zł  
<:Klata:1374793644246306866> **Set 35** — 90zł
""",
    1374380939970347019: """
💵 **15k$** — 1zł  
<:Buda:1375488639496093828> **Buda** — 30zł  
<:LoveSwap:1375490111801790464> **Love swap** — 100zł  
<:KlataMeduzy:1375487632531918875> **Klata meduzy** — 140zł
"""
}


class TicketView(discord.ui.View):
    def __init__(self, channel_id):
        super().__init__()
        url = f"https://discord.com/channels/{bot.guilds[0].id}/{channel_id}"
        self.add_item(discord.ui.Button(label="🎫 Otwórz ticket", url=url))


@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user}!")

    guild = bot.guilds[0]

    for channel_id, message_text in CHANNEL_MESSAGES.items():
        channel = bot.get_channel(channel_id)
        if not channel:
            print(f"Nie znaleziono kanału o ID {channel_id}")
            continue

        # Usuń stare wiadomości bota z tego kanału
        try:
            async for msg in channel.history(limit=20):
                if msg.author == bot.user:
                    await msg.delete()
        except Exception as e:
            print(f"Nie udało się usunąć wiadomości w kanale {channel_id}: {e}")

        # Utwórz ładny embed
        embed = discord.Embed(
            title="🛒 Oferta itemów na sprzedaż",
            description=message_text,
            color=discord.Color.gold()
        )
        embed.set_footer(text="Kliknij przycisk poniżej, aby otworzyć ticket.")
        view = TicketView(TICKET_CHANNEL_ID)

        try:
            await channel.send(embed=embed, view=view)
            print(f"Wysłano wiadomość na kanał {channel_id}")
        except Exception as e:
            print(f"Błąd przy wysyłaniu do {channel_id}: {e}")

    print("Wszystkie oferty zostały zaktualizowane.")
    await bot.close()


if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_TOKEN")
    if not TOKEN:
        print("Proszę ustawić zmienną środowiskową DISCORD_TOKEN z tokenem bota.")
    else:
        bot.run(TOKEN)
