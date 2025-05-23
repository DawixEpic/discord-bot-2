import discord
from discord.ext import commands
from discord.ui import View, Select, Button
import asyncio
import os
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

ROLE_ID = 1373275307150278686
TICKET_CATEGORY_ID = 1373277957446959135
LOG_CHANNEL_ID = 1374479815914291240
REVIEW_CHANNEL_ID = 1375528888586731762

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

# Słownik przechowujący czy użytkownik może wystawić ocenę
user_review_status = {}

class VerifyButton(Button):
    def __init__(self):
        super().__init__(label="✅ Zweryfikuj", style=discord.ButtonStyle.success)

    async def callback(self, interaction: discord.Interaction):
        role = interaction.guild.get_role(ROLE_ID)
        if role:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("✅ Zweryfikowano pomyślnie!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Rola nie została znaleziona.", ephemeral=True)

class OpenTicketButton(Button):
    def __init__(self):
        super().__init__(label="🎟️ Otwórz ticket", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        # Sprawdzamy czy użytkownik może otworzyć nowy ticket
        if user_review_status.get(interaction.user.id, True) is False:
            await interaction.response.send_message(
                "❌ Nie możesz otworzyć nowego ticketu, dopóki nie wystawisz oceny za poprzedni zrealizowany ticket.",
                ephemeral=True
            )
            return

        guild = interaction.guild
        category = guild.get_channel(TICKET_CATEGORY_ID)
        if not isinstance(category, discord.CategoryChannel):
            await interaction.response.send_message("❌ Nie znaleziono kategorii dla ticketów.", ephemeral=True)
            return

        channel_name = f"ticket-{interaction.user.name}".lower()
        if discord.utils.get(guild.channels, name=channel_name):
            await interaction.response.send_message("❗ Masz już otwarty ticket.", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        ticket_channel = await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)
        ticket_id = ticket_channel.id

        # Po utworzeniu ticketu blokujemy możliwość oceny (bo ticket jest otwarty)
        user_review_status[interaction.user.id] = False

        await ticket_channel.send(
            f"{interaction.user.mention}, witaj! Wybierz z poniższego menu co chcesz kupić.\n📄 **ID Ticketa:** `{ticket_id}`",
            view=MenuView(interaction.user, ticket_channel)
        )

        await interaction.response.send_message("✅ Ticket został utworzony!", ephemeral=True)

        await asyncio.sleep(3600)
        if ticket_channel and ticket_channel in guild.text_channels:
            await ticket_channel.delete(reason="Automatyczne zamknięcie ticketu po 1h")

class CloseTicketButton(Button):
    def __init__(self, channel, author_id):
        super().__init__(label="❌ Zamknij ticket", style=discord.ButtonStyle.danger)
        self.channel = channel
        self.author_id = author_id

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id and not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ Nie masz uprawnień do zamknięcia tego ticketu.", ephemeral=True)
            return

        await interaction.response.send_message("✅ Ticket zostanie zamknięty za 5 sekund...", ephemeral=True)
        await asyncio.sleep(5)
        await self.channel.delete(reason="Zamknięty przez użytkownika")

class MarkDoneButton(Button):
    def __init__(self, user_name, user_id, date_str, order_desc):
        super().__init__(label="✔️ Zrealizowane", style=discord.ButtonStyle.success)
        self.user_name = user_name
        self.user_id = user_id
        self.date_str = date_str
        self.order_desc = order_desc

    async def callback(self, interaction: discord.Interaction):
        # Wysyłamy embed z oceną do kanału ocen
        review_channel = interaction.guild.get_channel(REVIEW_CHANNEL_ID)
        if not review_channel:
            await interaction.response.send_message("❌ Kanał ocen nie został znaleziony.", ephemeral=True)
            return

        embed = discord.Embed(
            title="📝 Nowa ocena zamówienia",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Użytkownik", value=self.user_name, inline=False)
        embed.add_field(name="Data zamówienia", value=self.date_str, inline=False)
        embed.add_field(name="Zamówienie", value=self.order_desc, inline=False)

        await review_channel.send(embed=embed)
        user_review_status[self.user_id] = True  # Odblokuj możliwość wystawienia oceny

        await interaction.message.delete()
        await interaction.response.send_message("✅ Zamówienie oznaczone jako zrealizowane. Możesz teraz wystawić ocenę.", ephemeral=True)

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
        self.add_item(CloseTicketButton(channel, member.id))

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

        # Usuwamy stare selecty poza close ticketem i dodajemy tryb
        self.clear_items()
        self.add_item(self.server_select)
        self.add_item(self.mode_select)
        self.add_item(CloseTicketButton(self.channel, self.member.id))

        await interaction.response.edit_message(view=self)

    async def mode_callback(self, interaction: discord.Interaction):
        self.selected_mode = interaction.data['values'][0]
        items = SERVER_OPTIONS[self.selected_server][self.selected_mode]

        self.item_select = Select(
            placeholder="Wybierz itemy",
            options=[discord.SelectOption(label=item) for item in items],
            max_values=len(items),
            custom_id="item_select"
        )
        self.item_select.callback = self.item_callback

        self.clear_items()
        self.add_item(self.server_select)
        self.add_item(self.mode_select)
        self.add_item(self.item_select)
        self.add_item(CloseTicketButton(self.channel, self.member.id))

        await interaction.response.edit_message(view=self)

    async def item_callback(self, interaction: discord.Interaction):
        self.selected_items = interaction.data['values']
        description = f"Serwer: {self.selected_server}\nTryb: {self.selected_mode}\nItemy: {', '.join(self.selected_items)}"

        embed = discord.Embed(
            title=f"Nowe zamówienie od {self.member.display_name}",
            description=description,
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"User ID: {self.member.id}")

        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if not log_channel:
            await interaction.response.send_message("❌ Kanał logów nie został znaleziony.", ephemeral=True)
            return

        view = View()
        view.add_item(MarkDoneButton(self.member.display_name, self.member.id, datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), description))

        await log_channel.send(embed=embed, view=view)

        await interaction.response.send_message("✅ Zamówienie zostało wysłane do realizacji.", ephemeral=True)
        # Usuwamy menu w tickecie po złożeniu zamówienia, żeby nie było wielokrotnych zamówień
        self.clear_items()
        self.add_item(CloseTicketButton(self.channel, self.member.id))
        await interaction.message.edit(view=self)

@bot.command()
async def ocena(ctx, *, text: str):
    if user_review_status.get(ctx.author.id, True) is False:
        await ctx.send("❌ Nie możesz jeszcze wystawić oceny. Poczekaj, aż ticket zostanie zrealizowany.")
        return
    
    review_channel = ctx.guild.get_channel(REVIEW_CHANNEL_ID)
    if not review_channel:
        await ctx.send("❌ Kanał ocen nie jest dostępny.")
        return

    embed = discord.Embed(
        title="📝 Ocena użytkownika",
        description=text,
        color=discord.Color.blue(),
        timestamp=datetime.utcnow()
    )
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    await review_channel.send(embed=embed)

    # Po ocenie blokujemy możliwość kolejnej oceny do momentu zrealizowania następnego ticketa
    user_review_status[ctx.author.id] = False

    await ctx.send("✅ Dziękujemy za ocenę!")

@bot.event
async def on_ready():
    print(f'Bot zalogowany jako {bot.user}!')

@bot.command()
async def start(ctx):
    # Komenda do wysłania wiadomości z weryfikacją i otwarciem ticketu
    verify_button = VerifyButton()
    ticket_button = OpenTicketButton()
    view = View()
    view.add_item(verify_button)
    view.add_item(ticket_button)
    await ctx.send("Kliknij przycisk, aby się zweryfikować lub otworzyć ticket.", view=view)

bot.run(os.getenv('TOKEN'))
