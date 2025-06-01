import discord
from discord.ext import commands

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# ID kanału ticketów – PODMIEŃ NA WŁAŚCIWY
TICKET_CHANNEL_ID = 123456789012345678

# Tu są oferty z przypisanymi kanałami
offers = {
    1373266589310517338: """
🛒 Oferta itemów na sprzedaż  
<:Elytra:1374797373406187580> Elytra — Cena: 12zł  
<:Buty:1374796797222064230> Buty flasha — Cena: 5zł  
<:Miecz:1374791139462352906> Miecz 6 — Cena: 3zł  

<:Shulker:1374795916531335271> Shulker s2 — Cena: 7zł  
<:Shulker:1374795916531335271> Shulker totemów — Cena: 6zł  

Kliknij przycisk poniżej, aby otworzyć ticket i dokonać zakupu!
""",
    1373267159576481842: """
🛒 Oferta itemów na sprzedaż  
<:Klata:1374793644246306866> Set 25 — Cena: 30zł  
<:Miecz:1374791139462352906> Miecz 25 — Cena: 25zł  
<:Kilof:1374795407493959751> Kilof 25 — Cena: 10zł  
💸 1mln$ — Cena: 18zł  

Kliknij przycisk poniżej, aby otworzyć ticket i dokonać zakupu!
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

Kliknij przycisk poniżej, aby otworzyć ticket i dokonać zakupu!
""",
    1373270295556788285: """
🛒 Oferta itemów na sprzedaż  
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
🛒 Oferta itemów na sprzedaż  
💸 10mld$ — Cena: 2zł  
<:Miecz:1374791139462352906> Miecz 35 — Cena: 65zł  
<:Klata:1374793644246306866> Set 35 — Cena: 90zł  

Kliknij przycisk poniżej, aby otworzyć ticket i dokonać zakupu!
""",
    1374380939970347019: """
🛒 Oferta itemów na sprzedaż  
💵 15k$ — Cena: 1zł  
<:Buda:1375488639496093828> Buda — Cena: 30zł  
<:LoveSwap:1375490111801790464> Love swap — Cena: 100zł  
<:KlataMeduzy:1375487632531918875> Klata meduzy — Cena: 140zł  

Kliknij przycisk poniżej, aby otworzyć ticket i dokonać zakupu!
"""
}

class TicketButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🛒 Otwórz ticket", style=discord.ButtonStyle.green)
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel = interaction.guild.get_channel(TICKET_CHANNEL_ID)
        if channel:
            await interaction.response.send_message(f"🔗 Kliknij, aby przejść do kanału ticketów: {channel.mention}", ephemeral=True)
        else:
            await interaction.response.send_message("Nie znaleziono kanału ticketów.", ephemeral=True)

@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user}")
    view = TicketButton()

    for channel_id, message in offers.items():
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send(content=message, view=view)

import os
bot.run("TWÓJ_TOKEN_BOTA")
