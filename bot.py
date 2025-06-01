import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

CHANNEL_ID = 1378641563868991548  # Tam, gdzie embed ma się pojawić
TICKET_CHANNEL_ID = 1373305137228939416  # ← TU wpisz ID kanału z ticketami

class GoToTicketView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(discord.ui.Button(
            label="🎫 Przejdź do ticketów",
            style=discord.ButtonStyle.link,
            url=f"https://discord.com/channels/{{guild_id}}/{TICKET_CHANNEL_ID}"  # guild_id uzupełniany automatycznie
        ))

@bot.event
async def on_ready():
    print(f"✅ Zalogowano jako {bot.user}")
    guild = bot.get_guild(CHANNEL_ID >> 22)  # Pobiera guild_id z kanału
    channel = bot.get_channel(CHANNEL_ID)

    if channel:
        embed = discord.Embed(
            title=" BOX ⮕ LF",
            description="💸 **85k = 1mln**",
            color=discord.Color.blue()
        )
        view = GoToTicketView()
        view.children[0].url = f"https://discord.com/channels/{guild.id}/{TICKET_CHANNEL_ID}"
        await channel.send(embed=embed, view=view)
        print("📨 Embed z przyciskiem wysłany.")
    else:
        print("❌ Nie znaleziono kanału!")

bot.run(os.getenv("DISCORD_TOKEN"))
