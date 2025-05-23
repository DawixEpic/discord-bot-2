import discord
from discord.ext import commands, tasks
from discord.ui import View, Select, Button
import asyncio
import os
from datetime import datetime, timezone

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

ROLE_ID = 1373275307150278686
TICKET_CATEGORY_ID = 1373277957446959135
LOG_CHANNEL_ID = 1374479815914291240
ADMIN_PANEL_CHANNEL_ID = 1374781085895884820
RATING_CHANNEL_ID = 1375528888586731762
GUILD_ID = 1373253103176122399  # Wstaw ID swojego serwera

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

rated_users = {}  # user_id -> bool (czy ocenił aktualny ticket)

@bot.event
async def on_ready():
    print(f"✅ Zalogowano jako {bot.user}")
    ticket_cleanup.start()

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
        await interaction.response.send_message(
            f"✅ Wybrałeś: **{self.selected_server}** → **{self.selected_mode}**\n🧾 Itemy: {', '.join(self.selected_items)}",
            ephemeral=True
        )

        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(
                title="📥 Nowy wybór w tickecie",
                description=f"**Użytkownik:** {interaction.user.mention}\n"
                            f"**Serwer:** {self.selected_server}\n"
                            f"**Tryb:** {self.selected_mode}\n"
                            f"**Itemy:** {', '.join(self.selected_items)}\n"
                            f"**Ticket:** {self.channel.mention}\n"
                            f"**Data:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
                color=discord.Color.orange()
            )
            view = View()
            view.add_item(RealizeButton(self.channel.id, interaction.user.id, self.selected_server, self.selected_mode, self.selected_items))
            await log_channel.send(embed=embed, view=view)

class RealizeButton(Button):
    def __init__(self, ticket_channel_id, user_id, server, mode, items):
        super().__init__(label="Zrealizuj", style=discord.ButtonStyle.success)
        self.ticket_channel_id = ticket_channel_id
        self.user_id = user_id
        self.server = server
        self.mode = mode
        self.items = items

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.guild_permissions.manage_channels is False:
            await interaction.response.send_message("❌ Tylko administratorzy mogą oznaczać realizację.", ephemeral=True)
            return

        # Zapisz, że użytkownik może teraz ocenić
        rated_users[self.user_id] = False

        await interaction.response.send_message(
            f"✅ Ticket został oznaczony jako zrealizowany. Użytkownik może teraz wystawić ocenę na kanale ocen.",
            ephemeral=True
        )

        rating_channel = interaction.guild.get_channel(RATING_CHANNEL_ID)
        if rating_channel:
            embed = discord.Embed(
                title="⭐ Wystaw ocenę",
                description=(
                    f"Użytkownik: <@{self.user_id}>\n"
                    f"Serwer: **{self.server}**\n"
                    f"Tryb: **{self.mode}**\n"
                    f"Itemy: {', '.join(self.items)}\n\n"
                    "Kliknij gwiazdkę, aby wystawić ocenę od 1 do 5.\n"
                    "Możesz ocenić tylko raz, po zrealizowanym tickecie."
                ),
                color=discord.Color.gold()
            )
            view = RatingView(self.user_id)
            await rating_channel.send(embed=embed, view=view)

class RatingView(View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id
        for i in range(1, 6):
            self.add_item(RatingButton(i, user_id))

class RatingButton(Button):
    def __init__(self, stars, user_id):
        super().__init__(label=f"{stars} ⭐", style=discord.ButtonStyle.secondary)
        self.stars = stars
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Możesz ocenić tylko swój własny ticket.", ephemeral=True)
            return

        if rated_users.get(self.user_id, True):
            await interaction.response.send_message("❌ Już oceniłeś swój ticket lub nie masz uprawnień.", ephemeral=True)
            return

        rated_users[self.user_id] = True  # zaznacz ocenę jako oddaną

        await interaction.response.send_message(f"Dziękujemy za ocenę {self.stars}⭐!", ephemeral=True)
        await interaction.message.delete()  # usuń wiadomość z oceną po oddaniu

        # Możesz dodać tu logowanie oceny np. do kanału admina

# Background task do usuwania ticketów starszych niż 1 godzina
@tasks.loop(minutes=10)
async def ticket_cleanup():
    guild = bot.get_guild(GUILD_ID)
    if guild is None:
        return
    category = guild.get_channel(TICKET_CATEGORY_ID)
    if not isinstance(category, discord.CategoryChannel):
        return
    now = datetime.now(timezone.utc)
    for channel in category.channels:
        age = (now - channel.created_at).total_seconds()
        if age > 3600:  # starsze niż 1 godzina
            try:
                await channel.delete(reason="Automatyczne usuwanie starych ticketów")
                print(f"Usunięto kanał {channel.name} (wiek {age} sekund)")
            except Exception as e:
                print(f"Błąd przy usuwaniu kanału {channel.name}: {e}")

bot.run(os.getenv("TOKEN"))
