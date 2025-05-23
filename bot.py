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

# --- ID-y i konfiguracje ---
ROLE_ID = 1373275307150278686
TICKET_CATEGORY_ID = 1373277957446959135
LOG_CHANNEL_ID = 1374479815914291240
REVIEW_CHANNEL_ID = 1375528888586731762

# Przechowuje ID użytkowników, którzy mogą wystawić ocenę (czyli mają zrealizowany ticket)
allowed_to_review = set()

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

# --- BUTTONY i SELECTY ---

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

        await ticket_channel.send(
            f"{interaction.user.mention}, witaj! Wybierz z poniższego menu co chcesz kupić.\n📄 **ID Ticketa:** `{ticket_id}`",
            view=MenuView(interaction.user, ticket_channel)
        )

        await interaction.response.send_message("✅ Ticket został utworzony!", ephemeral=True)

        # Opcjonalne automatyczne zamknięcie po 1h (można usunąć jeśli nie potrzebne)
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
        # Dodaj użytkownika do listy allowed_to_review (może ocenić)
        allowed_to_review.add(self.user_id)

        review_channel = interaction.guild.get_channel(REVIEW_CHANNEL_ID)
        if not review_channel:
            await interaction.response.send_message("❌ Kanał ocen nie został znaleziony.", ephemeral=True)
            return

        embed = discord.Embed(
            title="📥 Zamówienie zrealizowane",
            description=f"Użytkownik **{self.user_name}** może teraz wystawić ocenę.",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        await review_channel.send(embed=embed)

        await interaction.response.send_message("✅ Zamówienie oznaczone jako zrealizowane.\nUżytkownik może teraz wystawić ocenę.", ephemeral=True)
        await interaction.message.delete()

class ReviewSelect(Select):
    def __init__(self, user_name, order_desc, date_str):
        options = [
            discord.SelectOption(label="⭐", description="Ocena 1", value="1"),
            discord.SelectOption(label="⭐⭐", description="Ocena 2", value="2"),
            discord.SelectOption(label="⭐⭐⭐", description="Ocena 3", value="3"),
            discord.SelectOption(label="⭐⭐⭐⭐", description="Ocena 4", value="4"),
            discord.SelectOption(label="⭐⭐⭐⭐⭐", description="Ocena 5", value="5"),
        ]
        super().__init__(placeholder="Wybierz ocenę", options=options, min_values=1, max_values=1)
        self.user_name = user_name
        self.order_desc = order_desc
        self.date_str = date_str

    async def callback(self, interaction: discord.Interaction):
        rating = self.values[0]
        review_channel = interaction.guild.get_channel(REVIEW_CHANNEL_ID)
        if not review_channel:
            await interaction.response.send_message("❌ Kanał ocen nie został znaleziony.", ephemeral=True)
            return

        embed = discord.Embed(
            title="📝 Nowa ocena zamówienia",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Użytkownik", value=self.user_name, inline=False)
        embed.add_field(name="Data zamówienia", value=self.date_str, inline=False)
        embed.add_field(name="Zamówienie", value=self.order_desc, inline=False)
        embed.add_field(name="Ocena", value=f"{rating} / 5", inline=False)

        await review_channel.send(embed=embed)
        await interaction.response.send_message(f"✅ Dziękujemy za ocenę {rating}!", ephemeral=True)

        # Usuń użytkownika z allowed_to_review, by wymagać kolejnego zrealizowanego ticketu na kolejną ocenę
        allowed_to_review.discard(interaction.user.id)

class ReviewView(View):
    def __init__(self, user_name, order_desc, date_str):
        super().__init__(timeout=60)
        self.add_item(ReviewSelect(user_name, order_desc, date_str))

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

        self.clear_items()
        self.add_item(self.server_select)
        self.add_item(self.mode_select)
        self.add_item(CloseTicketButton(self.channel, self.member.id))
        await interaction.response.edit_message(view=self)

    async def mode_callback(self, interaction: discord.Interaction):
        self.selected_mode = interaction.data['values'][0]
        items = SERVER_OPTIONS[self.selected_server][self.selected_mode]

        self.items_select = Select(
            placeholder="Wybierz itemy",
            options=[discord.SelectOption(label=item) for item in items],
            custom_id="items_select",
            min_values=1,
            max_values=len(items)
        )
        self.items_select.callback = self.items_callback

        self.clear_items()
        self.add_item(self.server_select)
        self.add_item(self.mode_select)
        self.add_item(self.items_select)
        self.add_item(CloseTicketButton(self.channel, self.member.id))
        await interaction.response.edit_message(view=self)

    async def items_callback(self, interaction: discord.Interaction):
        self.selected_items = interaction.data['values']
        order_desc = ', '.join(self.selected_items)
        date_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        embed = discord.Embed(
            title="🛒 Podsumowanie zamówienia",
            description=f"**Serwer:** {self.selected_server}\n**Tryb:** {self.selected_mode}\n**Itemy:** {order_desc}",
            color=discord.Color.gold(),
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"Ticket ID: {self.channel.id}")
        await self.channel.send(embed=embed)

        # Wyślij wiadomość do kanału logów z przyciskiem "Zrealizowane"
        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            done_button = MarkDoneButton(interaction.user.name, interaction.user.id, date_str, order_desc)
            view = View()
            view.add_item(done_button)
            await log_channel.send(
                content=f"Zamówienie od {interaction.user.mention} ({interaction.user.id})",
                embed=embed,
                view=view
            )

        await interaction.response.send_message("✅ Zamówienie wysłane! Poczekaj na realizację.", ephemeral=True)

# --- KOMENDY ---

@bot.command(name="verify")
async def verify(ctx):
    role = ctx.guild.get_role(ROLE_ID)
    if not role:
        await ctx.reply("❌ Rola weryfikacyjna nie została znaleziona.")
        return
    await ctx.author.add_roles(role)
    await ctx.reply("✅ Zweryfikowano pomyślnie!")

@bot.command(name="open_ticket")
async def open_ticket(ctx):
    guild = ctx.guild
    category = guild.get_channel(TICKET_CATEGORY_ID)
    if not isinstance(category, discord.CategoryChannel):
        await ctx.reply("❌ Nie znaleziono kategorii dla ticketów.")
        return

    channel_name = f"ticket-{ctx.author.name}".lower()
    if discord.utils.get(guild.channels, name=channel_name):
        await ctx.reply("❗ Masz już otwarty ticket.")
        return

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }

    ticket_channel = await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)
    ticket_id = ticket_channel.id

    await ticket_channel.send(
        f"{ctx.author.mention}, witaj! Wybierz z poniższego menu co chcesz kupić.\n📄 **ID Ticketa:** `{ticket_id}`",
        view=MenuView(ctx.author, ticket_channel)
    )
    await ctx.reply("✅ Ticket został utworzony!")

@bot.command(name="ocena")
async def ocena(ctx):
    user_id = ctx.author.id
    if user_id not in allowed_to_review:
        await ctx.reply("❌ Nie możesz teraz wystawić oceny. Poczekaj, aż Twój ticket zostanie zrealizowany.", mention_author=True)
        return

    # Tu trzeba by realnie powiązać zamówienie i datę z użytkownikiem, ale na razie daję przykładowe dane:
    order_desc = "Przykładowe zamówienie"
    date_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    view = ReviewView(ctx.author.name, order_desc, date_str)
    await ctx.send("Wybierz ocenę dla swojego zamówienia:", view=view)

# --- EVENTY ---

@bot.event
async def on_ready():
    print(f"Bot zalogowany jako {bot.user}")

# --- URUCHOMIENIE BOTA ---

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
bot.run(TOKEN)
