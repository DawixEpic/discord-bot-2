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

# --- KONFIGURACJA ---
ROLE_ID = 1373275307150278686
TICKET_CATEGORY_ID = 1373277957446959135
LOG_CHANNEL_ID = 1374479815914291240
RATING_CHANNEL_ID = 1375528888586731762  # kanał na oceny

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

# Przechowuje status ticketów zrealizowanych: {user_id: bool}
realized_tickets = {}

# Przechowuje oceny użytkowników: {user_id: {'speed': int, 'accept': int, 'overall': int}}
user_ratings = {}

# Przechowuje dane zamówienia dla usera: {user_id: {server, mode, items, date}}
user_order_data = {}

@bot.event
async def on_ready():
    print(f"✅ Zalogowano jako {bot.user}")

# --- KOMENDA WERYFIKACJA ---
@bot.command()
async def weryfikacja(ctx):
    embed = discord.Embed(
        title="✅ Weryfikacja",
        description="Kliknij przycisk poniżej, aby się zweryfikować i uzyskać dostęp do serwera.",
        color=discord.Color.blue()
    )
    view = View()
    view.add_item(VerifyButton())
    await ctx.send(embed=embed, view=view)

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

# --- KOMENDA TICKET ---
@bot.command()
async def ticket(ctx):
    embed = discord.Embed(
        title="🎟️ System ticketów",
        description="Kliknij poniżej, aby otworzyć ticket i wybrać co chcesz kupić.",
        color=discord.Color.green()
    )
    view = View()
    view.add_item(OpenTicketButton())
    await ctx.send(embed=embed, view=view)

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

        # Ticket automatycznie zamyka się po 1h (możesz zmienić)
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

# --- MENU WYBORU SERWER -> TRYB -> ITEMY ---
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
        await interaction.response.edit_message(content=None, view=self)

    async def mode_callback(self, interaction: discord.Interaction):
        self.selected_mode = interaction.data['values'][0]
        self.selected_items = []

        items = SERVER_OPTIONS[self.selected_server][self.selected_mode]
        self.item_select = Select(
            placeholder="Wybierz itemy",
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
        self.add_item(CloseTicketButton(self.channel, self.member.id))
        await interaction.response.edit_message(content=None, view=self)

    async def item_callback(self, interaction: discord.Interaction):
        self.selected_items = interaction.data['values']

        # Zapisz dane zamówienia
        user_order_data[self.member.id] = {
            "server": self.selected_server,
            "mode": self.selected_mode,
            "items": self.selected_items,
            "date": datetime.utcnow()
        }

        # Zaloguj wybór w kanale LOGÓW z przyciskiem ZREALIZUJ
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
            view = RealizeButtonView(interaction.user.id)
            await log_channel.send(embed=embed, view=view)

        await interaction.response.send_message(
            f"✅ Wybrałeś: **{self.selected_server}** → **{self.selected_mode}**\n🧾 Itemy: {', '.join(self.selected_items)}",
            ephemeral=True
        )

# --- PRZYCISK ZREALIZUJ (w kanale logów) ---
class RealizeButton(Button):
    def __init__(self, user_id):
        super().__init__(label="✅ Zrealizuj", style=discord.ButtonStyle.success)
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        # Tylko admin może zrealizować
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("❌ Nie masz uprawnień do tej akcji.", ephemeral=True)
            return

        # Zapamiętaj, że ticket zrealizowany
        realized_tickets[self.user_id] = True

        await interaction.response.send_message("✅ Ticket oznaczony jako zrealizowany.", ephemeral=True)

        # Wyślij wiadomość z prośbą o ocenę do kanału oceny
        rating_channel = interaction.guild.get_channel(RATING_CHANNEL_ID)
        if rating_channel:
            # Tworzymy embed z podstawowymi danymi i pustymi ocenami
            order = user_order_data.get(self.user_id, None)
            if order:
                embed = discord.Embed(
                    title="📝 Proszę oceń swój ticket",
                    description=(f"**Użytkownik:** <@{self.user_id}>\n"
                                 f"**Serwer:** {order['server']}\n"
                                 f"**Tryb:** {order['mode']}\n"
                                 f"**Itemy:** {', '.join(order['items'])}\n"
                                 f"**Data:** {order['date'].strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
                                 "Kliknij gwiazdkę aby ocenić:\n"
                                 "• Szybkość dostawy\n"
                                 "• Przyjęcie zamówienia\n"
                                 "• Ocena ogólna"),
                    color=discord.Color.blue()
                )
                view = RatingView(self.user_id)
                await rating_channel.send(embed=embed, view=view)
            else:
                await interaction.followup.send("❌ Brak danych zamówienia dla tego użytkownika.", ephemeral=True)

# --- SYSTEM OCENIANIA ---
class RatingView(View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id

        # Przechowujemy w view jakie oceny zostały oddane
        if self.user_id not in user_ratings:
            user_ratings[self.user_id] = {'speed': None, 'accept': None, 'overall': None}

        self.speed_btn = RatingButton("speed", "Szybkość dostawy")
        self.accept_btn = RatingButton("accept", "Przyjęcie zamówienia")
        self.overall_btn = RatingButton("overall", "Ocena ogólna")

        self.add_item(self.speed_btn)
        self.add_item(self.accept_btn)
        self.add_item(self.overall_btn)

    async def update_message(self, interaction: discord.Interaction):
        # Aktualizuj embed z ocenami
        embed = interaction.message.embeds[0]

        ratings = user_ratings[self.user_id]

        description = (f"**Użytkownik:** <@{self.user_id}>\n"
                       f"• Szybkość dostawy: {ratings['speed'] if ratings['speed'] is not None else '❔'}\n"
                       f"• Przyjęcie zamówienia: {ratings['accept'] if ratings['accept'] is not None else '❔'}\n"
                       f"• Ocena ogólna: {ratings['overall'] if ratings['overall'] is not None else '❔'}")

        embed.description = description
        await interaction.message.edit(embed=embed, view=self)

class RatingButton(Button):
    def __init__(self, category, label):
        super().__init__(label=label, style=discord.ButtonStyle.secondary, custom_id=category)
        self.category = category
        self.stars = [1, 2, 3, 4, 5]

    async def callback(self, interaction: discord.Interaction):
        user_id = int(self.custom_id.split("_")[0]) if "_" in self.custom_id else interaction.message.id  # nie używamy tego tu
        view: RatingView = self.view

        # Sprawdź czy użytkownik może ocenić
        if interaction.user.id != view.user_id:
            await interaction.response.send_message("❌ Możesz ocenić tylko swój własny ticket.", ephemeral=True)
            return

        # Jeśli już ocenił ten aspekt, odrzuć
        if user_ratings[view.user_id][self.category] is not None:
            await interaction.response.send_message(f"❗ Już oceniłeś {self.label}.", ephemeral=True)
            return

        # Zapisz ocenę (przyjmujemy ocenę = 5 bo to kliknięcie, dla uproszczenia)
        # Możemy rozszerzyć na przyciski z 1-5 gwiazdkami osobno, ale teraz uproszczenie:
        # Dodajmy szybkie pytanie o ocenę (1-5) lub pojedynczy przycisk - tu rozbudujemy na prosty wybór
        await interaction.response.send_message(f"Proszę wpisz ocenę (1-5) dla {self.label}:", ephemeral=True)

        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel and m.content.isdigit() and 1 <= int(m.content) <= 5

        try:
            msg = await bot.wait_for('message', check=check, timeout=30)
            rating = int(msg.content)
            user_ratings[view.user_id][self.category] = rating
            await interaction.followup.send(f"Dziękujemy za ocenę {rating} dla {self.label}!", ephemeral=True)
        except asyncio.TimeoutError:
            await interaction.followup.send("❌ Przekroczono czas na podanie oceny.", ephemeral=True)
            return

        await view.update_message(interaction)

bot.run(os.getenv("DISCORD_TOKEN"))
