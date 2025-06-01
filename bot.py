import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

TICKET_CHANNEL_ID = 1373305137228939416  # Wstaw swój ID kanału ticketów
LOGO_URL = "https://cdn.discordapp.com/attachments/1373268875407396914/1378672704999264377/Zrzut_ekranu_2025-05-17_130038.png"

CHANNEL_MESSAGES = {
    1373266589310517338: """
<:Elytra:1374797373406187580> Elytra — Cena: 12zł  
<:Buty:1374796797222064230> Buty flasha — Cena: 5zł  
<:Miecz:1374791139462352906> Miecz 6 — Cena: 3zł  
<:Shulker:1374795916531335271> Shulker s2 — Cena: 7zł  
<:Shulker:1374795916531335271> Shulker totemów — Cena: 6zł  

Kliknij przycisk poniżej, aby otworzyć ticket i dokonać zakupu!
""",
    1373267159576481842: """
<:Klata:1374793644246306866> Set 25 — Cena: 30zł  
<:Miecz:1374791139462352906> Miecz 25 — Cena: 25zł  
<:Kilof:1374795407493959751> Kilof 25 — Cena: 10zł  
💸 1mln$ — Cena: 18zł  

Kliknij przycisk poniżej, aby otworzyć ticket i dokonać zakupu!
""",
    1373268875407396914: """
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

Kliknij przycisk poniżej, aby otworzyć ticket i dokonać zakupu!
""",
    1373270295556788285: """
💵 50k$ — Cena: 1zł  
💸 1mln$ — Cena: 33zł  

🎉 EVENTÓWKI:  
<:Excalibur:1374785662191927416> Excalibur — Cena: 111zł  
<:Totem:1374788635211206757> Totem ułaskawienia — Cena: 270zł  
<:Sakiewka:1374799829120716892> Sakiewka — Cena: 50zł  

Kliknij przycisk poniżej, aby otworzyć ticket i dokonać zakupu!
""",
    1378641563868991548: """
BOX ⮕ LF  
💸 85k = 1mln
""",
    1373273108093337640: """
💸 10mld$ — Cena: 2zł  
<:Miecz:1374791139462352906> Miecz 35 — Cena: 65zł  
<:Klata:1374793644246306866> Set 35 — Cena: 90zł  

Kliknij przycisk poniżej, aby otworzyć ticket i dokonać zakupu!
""",
    1374380939970347019: """
💵 15k$ — Cena: 1zł  
<:Buda:1375488639496093828> Buda — Cena: 30zł  
<:LoveSwap:1375490111801790464> Love swap — Cena: 100zł  
<:KlataMeduzy:1375487632531918875> Klata meduzy — Cena: 140zł  

Kliknij przycisk poniżej, aby otworzyć ticket i dokonać zakupu!
"""
}

class TicketView(discord.ui.View):
    def __init__(self, channel_id):
        super().__init__()
        guild_id = None
        if bot.guilds:
            guild_id = bot.guilds[0].id
        else:
            guild_id = 0
        url = f"https://discord.com/channels/{guild_id}/{channel_id}"
        self.add_item(discord.ui.Button(label="Otwórz ticket", url=url))

@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user}!")

    for channel_id, message_text in CHANNEL_MESSAGES.items():
        channel = bot.get_channel(channel_id)
        if channel:
            # Usuń wszystkie poprzednie wiadomości bota w tym kanale
            try:
                async for msg in channel.history(limit=100):
                    if msg.author == bot.user:
                        await msg.delete()
            except Exception as e:
                print(f"Błąd podczas usuwania wiadomości w kanale {channel_id}: {e}")

            try:
                embed = discord.Embed(
                    title="Oferta",
                    description=message_text,
                    color=discord.Color.blue()
                )
                embed.set_thumbnail(url=LOGO_URL)

                view = TicketView(TICKET_CHANNEL_ID)

                await channel.send(embed=embed, view=view)
                print(f"Wysłano wiadomość na kanał {channel_id}")
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
