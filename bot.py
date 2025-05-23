import discord
from discord.ext import commands
from discord.ui import View, Button, Select
from datetime import datetime
import os

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

ROLE_ID = 1373275307150278686
TICKET_CATEGORY_ID = 1373277957446959135
LOG_CHANNEL_ID = 1374479815914291240

SERVER_OPTIONS = {
    "𝐂𝐑𝐀𝐅𝐓𝐏𝐋𝐀𝐘": {
        "𝐆𝐈𝐋𝐃𝐈𝐄": ["Elytra", "Buty flasha", "Miecz 6", "Shulker S2", "Shulker totemów", "1k$"],
        "𝐁𝐎𝐗𝐏𝐕𝐏": ["Set 25", "Miecz 25", "Kilof 25", "10k$"]
    },
    "𝐀𝐍𝐀𝐑𝐂𝐇𝐈𝐀": {
        "𝐋𝐈𝐅𝐄𝐒𝐓𝐄𝐀𝐋": ["Set anarchczny 2", "Set anarchiczny 1", "Miecze anarchcznye", "Excalibur", "Totem ułskawienia", "4,5k$", "50k$", "550k$"],
        "𝐁𝐎𝐗𝐏𝐕𝐏": ["Excalibur", "Totem ułskawienia", "Sakiewka", "50k$", "1mln"]
    },
    "𝐑𝐀𝐏𝐘": {
        "𝐋𝐈𝐅𝐄𝐒𝐓𝐄𝐀𝐋": ["nie dostępne", "nie dostępne", "nie dostępne"],
        "𝐁𝐎𝐗𝐏𝐕𝐏": ["Set 35", "Miecz 35", "Kilof 35", "10mld$", "50mld$", "100mld$"]
    },
    "𝐏𝐘𝐊𝐌𝐂": {
        "𝐋𝐈𝐅𝐄𝐒𝐓𝐄𝐀𝐋": ["Buddha", "Love swap", "Klata meduzy"],
        "𝐁𝐎𝐗𝐏𝐕𝐏": ["nie dostępne", "nie dostępne", "nie dostępne"]
    }
}

class VerifyView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Zweryfikuj się", style=discord.ButtonStyle.success, custom_id="verify_button")
    async def verify_button(self, button: Button, interaction: discord.Interaction):
        role = interaction.guild.get_role(ROLE_ID)
        if not role:
            await interaction.response.send_message("Nie znaleziono roli do weryfikacji.", ephemeral=True)
            return
        if role in interaction.user.roles:
            await interaction.response.send_message("Jesteś już zweryfikowany!", ephemeral=True)
            return
        await interaction.user.add_roles(role)
        await interaction.response.send_message("Zostałeś zweryfikowany!", ephemeral=True)

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Otwórz ticket", style=discord.ButtonStyle.primary, custom_id="open_ticket_button")
    async def open_ticket(self, button: Button, interaction: discord.Interaction):
        guild = interaction.guild
        category = guild.get_channel(TICKET_CATEGORY_ID)
        if category is None or not isinstance(category, discord.CategoryChannel):
            await interaction.response.send_message("Nie znaleziono kategorii ticketów.", ephemeral=True)
            return

        existing = discord.utils.get(guild.text_channels, name=f"ticket-{interaction.user.name.lower()}")
        if existing:
            await interaction.response.send_message(f"Masz już otwarty ticket: {existing.mention}", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        channel = await guild.create_text_channel(f"ticket-{interaction.user.name}".lower(), category=category, overwrites=overwrites)

        await channel.send(f"{interaction.user.mention}, ticket otwarty! Tutaj wybierz serwer, tryb i itemy.", view=None)

        await interaction.response.send_message(f"Ticket został utworzony: {channel.mention}", ephemeral=True)

@bot.command()
async def weryfikacja(ctx):
    print("Wywołano komendę !weryfikacja")  # debug
    embed = discord.Embed(
        title="Weryfikacja",
        description="Kliknij przycisk, aby się zweryfikować i uzyskać dostęp do serwera.",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed, view=VerifyView())

@bot.command()
async def ticket(ctx):
    print("Wywołano komendę !ticket")  # debug
    embed = discord.Embed(
        title="System Ticketów",
        description="Kliknij przycisk, aby otworzyć ticket.",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed, view=TicketView())

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    print(f"Received message: {message.content}")  # debug
    await bot.process_commands(message)

if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_TOKEN") or "TWÓJ_TOKEN_TUTAJ"
    bot.run(TOKEN)
