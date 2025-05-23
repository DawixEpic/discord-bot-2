import discord
from discord.ext import commands
from discord.ui import View, Button, Select
from datetime import datetime
import os
import asyncio

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
        self.add_item(Button(label="Zweryfikuj się", style=discord.ButtonStyle.success, custom_id="verify_button"))

    @discord.ui.button(label="Zweryfikuj się", style=discord.ButtonStyle.success, custom_id="verify_button")
    async def verify_button(self, button: Button, interaction: discord.Interaction):
        role = interaction.guild.get_role(ROLE_ID)
        if role in interaction.user.roles:
            await interaction.response.send_message("Jesteś już zweryfikowany!", ephemeral=True)
            return
        await interaction.user.add_roles(role)
        await interaction.response.send_message("Zostałeś zweryfikowany!", ephemeral=True)

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(label="Otwórz ticket", style=discord.ButtonStyle.primary, custom_id="open_ticket_button"))

    @discord.ui.button(label="Otwórz ticket", style=discord.ButtonStyle.primary, custom_id="open_ticket_button")
    async def open_ticket(self, button: Button, interaction: discord.Interaction):
        guild = interaction.guild
        category = guild.get_channel(TICKET_CATEGORY_ID)
        if category is None or not isinstance(category, discord.CategoryChannel):
            await interaction.response.send_message("Nie znaleziono kategorii ticketów.", ephemeral=True)
            return

        # Sprawdź czy użytkownik już ma ticket
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

        # Wyślij menu wyboru w nowym tickecie
        await channel.send(f"{interaction.user.mention}, wybierz opcje z menu poniżej.", view=TicketMenuView(interaction.user))

        await interaction.response.send_message(f"Ticket został utworzony: {channel.mention}", ephemeral=True)

class TicketMenuView(View):
    def __init__(self, user):
        super().__init__(timeout=None)
        self.user = user
        self.selected_server = None
        self.selected_mode = None
        self.selected_items = []

        self.server_select = Select(
            placeholder="Wybierz serwer",
            options=[discord.SelectOption(label=srv) for srv in SERVER_OPTIONS.keys()],
            custom_id="select_server"
        )
        self.server_select.callback = self.server_selected
        self.add_item(self.server_select)

    async def server_selected(self, interaction: discord.Interaction):
        if interaction.user != self.user:
            await interaction.response.send_message("To nie Twój ticket!", ephemeral=True)
            return
        self.selected_server = interaction.data['values'][0]
        self.selected_mode = None
        self.selected_items = []

        modes = SERVER_OPTIONS[self.selected_server]
        self.mode_select = Select(
            placeholder="Wybierz tryb",
            options=[discord.SelectOption(label=mode) for mode in modes.keys()],
            custom_id="select_mode"
        )
        self.mode_select.callback = self.mode_selected

        self.clear_items()
        self.add_item(self.server_select)
        self.add_item(self.mode_select)
        await interaction.response.edit_message(view=self)

    async def mode_selected(self, interaction: discord.Interaction):
        if interaction.user != self.user:
            await interaction.response.send_message("To nie Twój ticket!", ephemeral=True)
            return
        self.selected_mode = interaction.data['values'][0]
        self.selected_items = []

        items = SERVER_OPTIONS[self.selected_server][self.selected_mode]
        self.item_select = Select(
            placeholder="Wybierz itemy",
            options=[discord.SelectOption(label=item) for item in items],
            custom_id="select_items",
            min_values=1,
            max_values=len(items),
            disabled=False
        )
        self.item_select.callback = self.items_selected

        self.clear_items()
        self.add_item(self.server_select)
        self.add_item(self.mode_select)
        self.add_item(self.item_select)
        await interaction.response.edit_message(view=self)

    async def items_selected(self, interaction: discord.Interaction):
        if interaction.user != self.user:
            await interaction.response.send_message("To nie Twój ticket!", ephemeral=True)
            return
        self.selected_items = interaction.data['values']

        # Wyślij podsumowanie wyboru i zaloguj w kanale logów
        desc = (f"**Użytkownik:** {interaction.user.mention}\n"
                f"**Serwer:** {self.selected_server}\n"
                f"**Tryb:** {self.selected_mode}\n"
                f"**Itemy:** {', '.join(self.selected_items)}")

        await interaction.response.send_message(f"Wybrałeś:\n{desc}", ephemeral=True)

        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(title="Nowy wybór w tickecie", description=desc, color=discord.Color.gold(), timestamp=datetime.utcnow())
            await log_channel.send(embed=embed)

@bot.command()
async def weryfikacja(ctx):
    embed = discord.Embed(
        title="Weryfikacja",
        description="Kliknij przycisk, aby się zweryfikować i uzyskać dostęp do serwera.",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed, view=VerifyView())

@bot.command()
async def ticket(ctx):
    embed = discord.Embed(
        title="System Ticketów",
        description="Kliknij przycisk, aby otworzyć ticket i wybrać serwer, tryb oraz itemy.",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed, view=TicketView())

bot.run(os.getenv("DISCORD_TOKEN"))
