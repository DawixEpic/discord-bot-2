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

# -------------------------------
# GLOBALNE DICTIONARY na stany
# -------------------------------

# user_id: bool czy może ocenić (po zrealizowanym tickecie)
user_can_review = {}

# user_id: dane ostatniego zamówienia (str)
user_orders = {}

# ---------------------------------
# PRZYCISKI I MENU OCENY
# ---------------------------------

class ReviewSelect(Select):
    def __init__(self, user_id):
        options = [
            discord.SelectOption(label="⭐️", description="Ocena 1 - Bardzo słabo"),
            discord.SelectOption(label="⭐⭐️", description="Ocena 2 - Słabo"),
            discord.SelectOption(label="⭐⭐⭐️", description="Ocena 3 - Średnio"),
            discord.SelectOption(label="⭐⭐⭐⭐️", description="Ocena 4 - Dobrze"),
            discord.SelectOption(label="⭐⭐⭐⭐⭐️", description="Ocena 5 - Bardzo dobrze"),
        ]
        super().__init__(placeholder="Wybierz ocenę", min_values=1, max_values=1, options=options)
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ To menu nie jest dla Ciebie.", ephemeral=True)
            return

        rating = self.values[0]
        # Pobierz dane zamówienia użytkownika
        order_desc = user_orders.get(self.user_id, "Brak danych zamówienia")
        date_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        user_name = interaction.user.name

        # Wyślij ocenę do kanału ocen
        review_channel = interaction.guild.get_channel(REVIEW_CHANNEL_ID)
        if not review_channel:
            await interaction.response.send_message("❌ Kanał ocen nie został znaleziony.", ephemeral=True)
            return

        embed = discord.Embed(
            title="📝 Nowa ocena zamówienia",
            description=f"Ocena: {rating}",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Użytkownik", value=user_name, inline=False)
        embed.add_field(name="Data zamówienia", value=date_str, inline=False)
        embed.add_field(name="Zamówienie", value=order_desc, inline=False)

        await review_channel.send(embed=embed)
        await interaction.response.send_message("✅ Dziękujemy za wystawienie oceny!", ephemeral=True)

        # Ustaw że użytkownik już ocenił (nie może ocenić ponownie, dopóki nie zrealizuje kolejnego ticketa)
        user_can_review[self.user_id] = False
        # Opcjonalnie usuń dane zamówienia
        user_orders.pop(self.user_id, None)

        # Usuń menu po ocenie
        await interaction.message.edit(view=None)

class ReviewView(View):
    def __init__(self, user_id):
        super().__init__(timeout=300)
        self.add_item(ReviewSelect(user_id))

    async def on_timeout(self):
        # Po czasie usuń menu oceny
        for child in self.children:
            child.disabled = True
        # Musisz mieć dostęp do message, żeby edytować (tu nie mamy, więc to minimalny przykład)
        # Możesz to rozwiązać np. zapisując message w konstruktorze
        # pass

# ---------------------------------
# TWÓJ KOD Z BUTTONAMI I MENU
# ---------------------------------

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
    def __init__(self, user_name, date_str, order_desc, user_id):
        super().__init__(label="✔️ Zrealizowane", style=discord.ButtonStyle.success)
        self.user_name = user_name
        self.date_str = date_str
        self.order_desc = order_desc
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        # Wysyłamy embed z informacją o zrealizowanym zamówieniu do kanału logów
        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if not log_channel:
            await interaction.response.send_message("❌ Kanał logów nie został znaleziony.", ephemeral=True)
            return

        embed = discord.Embed(
            title="✅ Zamówienie zrealizowane",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Użytkownik", value=self.user_name, inline=False)
        embed.add_field(name="Data zamówienia", value=self.date_str, inline=False)
        embed.add_field(name="Zamówienie", value=self.order_desc, inline=False)

        # Wyślij embed z przyciskiem do oznaczenia oceny
        view = ReviewRequestView(self.user_id, self.user_name, self.date_str, self.order_desc)
        await log_channel.send(embed=embed, view=view)

        # Ustaw, że użytkownik może teraz ocenić
        user_can_review[self.user_id] = True
        user_orders[self.user_id] = self.order_desc

        await interaction.response.send_message("✅ Zamówienie oznaczone jako zrealizowane.", ephemeral=True)

class ReviewRequestButton(Button):
    def __init__(self, user_id, user_name, date_str, order_desc):
        super().__init__(label="📝 Poproś o ocenę", style=discord.ButtonStyle.primary)
        self.user_id = user_id
        self.user_name = user_name
        self.date_str = date_str
        self.order_desc = order_desc

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Tylko użytkownik zamówienia może wystawić ocenę.", ephemeral=True)
            return

        # Wyślij do użytkownika menu oceny
        view = ReviewView(self.user_id)
        await interaction.response.send_message("Wystaw swoją ocenę:", view=view, ephemeral=True)

class ReviewRequestView(View):
    def __init__(self, user_id, user_name, date_str, order_desc):
        super().__init__(timeout=600)
        self.add_item(ReviewRequestButton(user_id, user_name, date_str, order_desc))

# -----------------------------------
# MENU WIELOPOZIOMOWE - Serwer → Tryb → Itemy
# -----------------------------------

class ItemSelect(Select):
    def __init__(self, user, server, mode):
        options = [discord.SelectOption(label=item) for item in SERVER_OPTIONS[server][mode]]
        super().__init__(placeholder="Wybierz item", min_values=1, max_values=1, options=options)
        self.user = user
        self.server = server
        self.mode = mode

    async def callback(self, interaction: discord.Interaction):
        # Zakończenie wyboru - podsumowanie i przycisk do zrealizowania
        item = self.values[0]
        desc = f"Serwer: {self.server}\nTryb: {self.mode}\nItem: {item}"

        # Zapisz dane do user_orders aby potem wykorzystać do oceny
        user_orders[self.user.id] = desc

        embed = discord.Embed(title="Podsumowanie zamówienia", description=desc, color=discord.Color.gold())
        view = View()
        view.add_item(CloseTicketButton(interaction.channel, self.user.id))
        view.add_item(MarkDoneButton(self.user.name, datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), desc, self.user.id))

        await interaction.response.edit_message(embed=embed, view=view)

class ModeSelect(Select):
    def __init__(self, user, server):
        options = [discord.SelectOption(label=mode) for mode in SERVER_OPTIONS[server].keys()]
        super().__init__(placeholder="Wybierz tryb", min_values=1, max_values=1, options=options)
        self.user = user
        self.server = server

    async def callback(self, interaction: discord.Interaction):
        mode = self.values[0]
        view = View()
        view.add_item(ItemSelect(self.user, self.server, mode))
        await interaction.response.edit_message(content=f"Wybrano tryb: {mode}\nTeraz wybierz item:", view=view)

class ServerSelect(Select):
    def __init__(self, user):
        options = [discord.SelectOption(label=server) for server in SERVER_OPTIONS.keys()]
        super().__init__(placeholder="Wybierz serwer", min_values=1, max_values=1, options=options)
        self.user = user

    async def callback(self, interaction: discord.Interaction):
        server = self.values[0]
        view = View()
        view.add_item(ModeSelect(self.user, server))
        await interaction.response.edit_message(content=f"Wybrano serwer: {server}\nTeraz wybierz tryb:", view=view)

class MenuView(View):
    def __init__(self, user, channel):
        super().__init__(timeout=None)
        self.user = user
        self.channel = channel
        self.add_item(ServerSelect(user))

# ---------------------------------
# KOMENDY I EVENTY
# ---------------------------------

@bot.event
async def on_ready():
    print(f"Bot zalogowany jako {bot.user}")

@bot.command()
@commands.has_permissions(administrator=True)
async def panel(ctx):
    """Wyświetla panel weryfikacji i otwarcia ticketu"""
    embed = discord.Embed(title="Panel", description="Weryfikacja i otwarcie ticketu", color=discord.Color.blurple())
    view = View()
    view.add_item(VerifyButton())
    view.add_item(OpenTicketButton())
    await ctx.send(embed=embed, view=view)

bot.run(os.getenv("TOKEN"))
