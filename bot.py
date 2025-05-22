import discord
from discord.ext import commands
from discord.ui import View, Select, Button
import asyncio
import os
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

ROLE_ID = 1373275307150278686
TICKET_CATEGORY_ID = 1373277957446959135
LOG_CHANNEL_ID = 1374479815914291240
TICKET_CHANNEL_ID = 1373305137228939416
ADMIN_PANEL_CHANNEL_ID = 1374781085895884820

verification_message_id = None
ticket_message_id = None

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

@bot.event
async def on_ready():
    print(f"✅ Zalogowano jako {bot.user}")

    channel = bot.get_channel(ADMIN_PANEL_CHANNEL_ID)
    if channel:
        embed = discord.Embed(
            title="Panel administracyjny ticketów",
            description="Użyj przycisków poniżej aby zarządzać ticketami.\n\n"
                        "- Zamknij ten ticket (usuwa kanał, działa w kanale ticketu)\n"
                        "- Pokaż listę ticketów (lista otwartych kanałów ticketów)",
            color=discord.Color.red()
        )
        view = AdminPanelView()
        await channel.send(embed=embed, view=view)
    else:
        print("❌ Nie znaleziono kanału do wysłania panelu admina.")

@bot.event
async def on_raw_reaction_add(payload):
    if payload.member is None or payload.member.bot:
        return

    guild = bot.get_guild(payload.guild_id)

    if payload.message_id == verification_message_id and str(payload.emoji) == "✅":
        role = guild.get_role(ROLE_ID)
        if role:
            await payload.member.add_roles(role)
            channel = guild.get_channel(payload.channel_id)
            await channel.send(f"{payload.member.mention}, zostałeś zweryfikowany!", delete_after=5)

    elif payload.message_id == ticket_message_id and str(payload.emoji) == "🎟️":
        category = guild.get_channel(TICKET_CATEGORY_ID)
        if not isinstance(category, discord.CategoryChannel):
            return

        channel_name = f"ticket-{payload.member.name}".lower()
        existing = discord.utils.get(guild.channels, name=channel_name)
        if existing:
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            payload.member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        ticket_channel = await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)
        await ticket_channel.send(f"{payload.member.mention}, wybierz co chcesz kupić:", view=MenuView(payload.member, ticket_channel))

        await asyncio.sleep(3600)
        if ticket_channel and ticket_channel in guild.text_channels:
            await ticket_channel.delete(reason="Automatyczne zamknięcie ticketu po 1 godzinie")

class MenuView(View):
    def __init__(self, member, channel):
        super().__init__(timeout=None)
        self.member = member
        self.channel = channel
        self.selected_server = None
        self.selected_mode = None
        self.selected_items = []

        self.server_select = Select(
            placeholder="Wybierz serwer",
            options=[discord.SelectOption(label=srv) for srv in SERVER_OPTIONS.keys()],
            custom_id="server_select"
        )
        self.server_select.callback = self.server_callback
        self.add_item(self.server_select)

    async def server_callback(self, interaction: discord.Interaction):
        self.selected_server = interaction.data['values'][0]
        self.selected_mode = None
        self.selected_items = []

        modes = SERVER_OPTIONS.get(self.selected_server, {})
        self.mode_select = Select(
            placeholder="Wybierz tryb",
            options=[discord.SelectOption(label=mode) for mode in modes.keys()],
            custom_id="mode_select"
        )
        self.mode_select.callback = self.mode_callback

        self.clear_items()
        self.add_item(self.server_select)
        self.add_item(self.mode_select)

        await interaction.response.edit_message(content=None, view=self)

    async def mode_callback(self, interaction: discord.Interaction):
        self.selected_mode = interaction.data['values'][0]
        self.selected_items = []

        items = SERVER_OPTIONS[self.selected_server][self.selected_mode]
        self.item_select = Select(
            placeholder="Wybierz item(y) (możesz zaznaczyć wiele)",
            options=[discord.SelectOption(label=item) for item in items],
            custom_id="item_select",
            min_values=1,
            max_values=len(items)
        )
        self.item_select.callback = self.item_callback

        self.clear_items()
        self.add_item(self.server_select)
        self.add_item(self.mode_select)
        self.add_item(self.item_select)

        await interaction.response.edit_message(content=None, view=self)

    async def item_callback(self, interaction: discord.Interaction):
        self.selected_items = interaction.data['values']

        # Wyślij wiadomość prywatną
        await interaction.response.send_message(
            f"Wybrałeś: Serwer: {self.selected_server}, Tryb: {self.selected_mode}, Itemy: {', '.join(self.selected_items)}",
            ephemeral=True
        )

        # Loguj wybór do kanału logów
        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(
                title="📥 Nowy wybór w tickecie",
                description=f"**Użytkownik:** {interaction.user.mention}\n"
                            f"**Serwer:** {self.selected_server}\n"
                            f"**Tryb:** {self.selected_mode}\n"
                            f"**Itemy:** {', '.join(self.selected_items)}",
                color=discord.Color.gold(),
                timestamp=datetime.utcnow()
            )
            await log_channel.send(embed=embed)

class AdminPanelView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.close_button = Button(label="Zamknij ten ticket", style=discord.ButtonStyle.danger)
        self.list_button = Button(label="Pokaż listę ticketów", style=discord.ButtonStyle.secondary)

        self.close_button.callback = self.close_ticket
        self.list_button.callback = self.list_tickets

        self.add_item(self.close_button)
        self.add_item(self.list_button)

    async def close_ticket(self, interaction: discord.Interaction):
        channel = interaction.channel
        if channel.category and channel.category.id == TICKET_CATEGORY_ID:
            await channel.delete(reason=f"Ticket zamknięty przez {interaction.user}")
            await interaction.response.send_message("Ticket został zamknięty.", ephemeral=True)
        else:
            await interaction.response.send_message("Ta komenda działa tylko w kanałach ticketów.", ephemeral=True)

    async def list_tickets(self, interaction: discord.Interaction):
        guild = interaction.guild
        category = guild.get_channel(TICKET_CATEGORY_ID)
        if not category:
            await interaction.response.send_message("Kategoria ticketów nie została znaleziona.", ephemeral=True)
            return

        tickets = [ch.name for ch in category.channels]
        if not tickets:
            await interaction.response.send_message("Brak otwartych ticketów.", ephemeral=True)
        else:
            tickets_list = "\n".join(tickets)
            await interaction.response.send_message(f"Otwartych ticketów:\n{tickets_list}", ephemeral=True)

bot.run(os.getenv("DISCORD_TOKEN"))
