import discord
from discord.ext import commands
import os
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

TICKET_CHANNEL_ID = 1373305137228939416  # Twój kanał ticketów

CHANNEL_MESSAGES = {
    1373266589310517338: """
🛒 Oferta itemów na sprzedaż  

<:Elytra:1374797373406187580> Elytra — Cena: 12zł  
<:Buty:1374796797222064230> Buty flasha — Cena: 5zł  
<:Miecz:1374791139462352906> Miecz 6 — Cena: 3zł  
<:Shulker:1374795916531335271> Shulker s2 — Cena: 7zł  
<:Shulker:1374795916531335271> Shulker totemów — Cena: 6zł  
""",
    1373267159576481842: """
🛒 Oferta itemów na sprzedaż  

<:Klata:1374793644246306866> Set 25 — Cena: 30zł  
<:Miecz:1374791139462352906> Miecz 25 — Cena: 25zł  
<:Kilof:1374795407493959751> Kilof 25 — Cena: 10zł  
💸 1mln$ — Cena: 18zł  
""",
    1373268875407396914: """
🛒 Oferta itemów na sprzedaż  

💵 4,5k$ — Cena: 1zł  
💸 50k$ — Cena: 12zł  
💸 550k$ — Cena: 130zł  
<:ANA2:1374799017359314944> Anarchiczny set 2 — Cena: 28zł  
<:Klata:1374793644246306866> Anarchiczny set 1 — Cena: 9zł  

⚔️ MIECZE:  
<:Miecz:1374791139462352906> Anarchiczny miecz — Cena: 3zł  

🎉 EVENTÓWKI:  
<:MieczZajeczy:1375486003891929088> Zajęczy miecz — Cena: 65zł  
<:Totem:1374788635211206757> Totem ułaskawienia — Cena: 630zł  
<:Excalibur:1374785662191927416> Excalibur — Cena: 370zł  
""",
    1373270295556788285: """
🛒 Oferta itemów na sprzedaż  

💵 50k$ — Cena: 1zł  
💸 1mln$ — Cena: 33zł  

🎉 EVENTÓWKI:  
<:Excalibur:1374785662191927416> Excalibur — Cena: 111zł  
<:Totem:1374788635211206757> Totem ułaskawienia — Cena: 270zł  
<:Sakiewka:1374799829120716892> Sakiewka — Cena: 50zł  
""",
    1378641563868991548: """
BOX ⮕ LF  
💸 85k = 1mln
""",
    1373273108093337640: """
🛒 Oferta itemów na sprzedaż  

💸 10mld$ — Cena: 2zł  
<:Miecz:1374791139462352906> Miecz 35 — Cena: 65zł  
<:Klata:1374793644246306866> Set 35 — Cena: 90zł  
""",
    1374380939970347019: """
🛒 Oferta itemów na sprzedaż 
 
💵 15k$ — Cena: 1zł  
<:Buda:1375488639496093828> Buda — Cena: 30zł  
<:LoveSwap:1375490111801790464> Love swap — Cena: 100zł  
<:KlataMeduzy:1375487632531918875> Klata meduzy — Cena: 140zł  
"""
}

def parse_offer_text_to_fields(text):
    lines = text.strip().splitlines()
    fields = []
    if lines:
        header = lines[0].strip()
        description_lines = lines[1:]
        fields.append(("Oferta", header, False))
        for line in description_lines:
            line = line.strip()
            if line:
                if "— Cena:" in line:
                    name, price = line.split("— Cena:", maxsplit=1)
                    name = name.strip()
                    price = price.strip()
                    fields.append((name, price, True))
                else:
                    fields.append(("\u200b", line, False))
        fields.append(("\u200b", "\u200b", False))
    return fields

class TicketView(discord.ui.View):
    def __init__(self, channel_id):
        super().__init__()
        guild_id = bot.guilds[0].id if bot.guilds else 0
        url = f"https://discord.com/channels/{guild_id}/{channel_id}"
        self.add_item(discord.ui.Button(label="Otwórz ticket 🎫", url=url, style=discord.ButtonStyle.link))

@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user}!")
    
    for channel_id, offer_text in CHANNEL_MESSAGES.items():
        channel = bot.get_channel(channel_id)
        if channel:
            try:
                fields = parse_offer_text_to_fields(offer_text)
                embed = discord.Embed(
                    title="🛒 Oferta itemów na sprzedaż",
                    color=discord.Color.blurple(),
                    timestamp=datetime.utcnow()
                )
                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)
                embed.set_footer(text=f"Wysłano przez {bot.user.name}", icon_url=bot.user.avatar.url)

                view = TicketView(TICKET_CHANNEL_ID)
                await channel.send(embed=embed, view=view)
                print(f"Wysłano ofertę na kanał {channel_id}")
            except Exception as e:
                print(f"Błąd przy wysyłaniu do {channel_id}: {e}")
        else:
            print(f"Nie znaleziono kanału o ID {channel_id}")

    print("Wszystkie wiadomości zostały wysłane.")
    await bot.close()

if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_TOKEN")
    if not TOKEN:
        print("Proszę ustawić zmienną środowiskową DISCORD_TOKEN z tokenem bota.")
    else:
        bot.run(TOKEN)
