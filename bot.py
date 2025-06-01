import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# ID kanałów
EMBED_CHANNEL_ID = 1378641563868991548  # Kanał, gdzie ma się pojawić wiadomość
TICKET_CHANNEL_ID = 1373305137228939416  # Kanał ticketów

class GoToTicketView(discord.ui.View):
    def __init__(self, guild_id):
        super().__init__()
        self.add_item(discord.ui.Button(
            label="🎫 Przejdź do ticketów",
            style=discord.ButtonStyle.link,
            url=f"https://discord.com/channels/{guild_id}/{TICKET_CHANNEL_ID}"
        ))

@bot.event
async def on_ready():
    print(f"✅ Zalogowano jako {bot.user}")
    
    # Pobranie kanału, do którego wysyłamy wiadomość
    channel = bot.get_channel(EMBED_CHANNEL_ID)
    if channel is None:
        print("❌ Nie znaleziono kanału.")
        return

    guild_id = channel.guild.id
    view = GoToTicketView(guild_id)

    embed = discord.Embed(
        title=" BOX ⮕ LF",
        description="💸 **85k = 1mln**",
        color=discord.Color.blue()
    )

    await channel.send(embed=embed, view=view)
    print("📨 Wiadomość została wysłana.")

bot.run(os.getenv("DISCORD_TOKEN"))
