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
ADMIN_PANEL_CHANNEL_ID = 1374781085895884820
OCENY_CHANNEL_ID = 1375528888586731762  # Kanał ocen (wstaw swoje ID)

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

# Słownik do zapamiętywania ocen użytkowników - {user_id: rating}
user_ratings = {}

@bot.event
async def on_ready():
    print(f"✅ Zalogowano jako {bot.user}")

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

        # Automatyczne usunięcie ticketu po 1h (3600 sekund)
        await asyncio.sleep(3600)
        if ticket_channel and ticket_channel in guild.text_channels:
            await ticket_channel.delete(reason="Automatyczne zamknięcie ticketu po 1h")
            # Usuń ocenę, jeśli istnieje
            if interaction.user.id in user_ratings:
                del user_ratings[interaction.user.id]

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
        # Usuń ocenę użytkownika po zamknięciu ticketu
        if self.author_id in user_ratings:
            del user_ratings[self.author_id]

class RealizeButton(Button):
    def __init__(self, user):
        super().__init__(label="✅ Zrealizuj", style=discord.ButtonStyle.success)
        self.user = user

    async def callback(self, interaction: discord.Interaction):
        if self.user.id in user_ratings:
            await interaction.response.send_message("❗ Ten użytkownik już wystawił ocenę za ostatni ticket.", ephemeral=True)
            return

        try:
            await self.user.send("⭐ Wystaw ocenę za zrealizowany ticket:", view=RatingView(self.user))
            await interaction.response.send_message("📨 Wysłano wiadomość z oceną do użytkownika.", ephemeral=True)
            # Usuń przycisk z wiadomości logów po kliknięciu
            await interaction.message.delete()
        except discord.Forbidden:
            await interaction.response.send_message("❌ Nie udało się wysłać wiadomości do użytkownika (brak DM).", ephemeral=True)

class RatingView(View):
    def __init__(self, user):
        super().__init__(timeout=120)
        self.user = user

        options = [discord.SelectOption(label=f"{i} ⭐", value=str(i)) for i in range(1, 6)]
        self.select = Select(placeholder="Wybierz ocenę", options=options)
        self.select.callback = self.on_rating_select
        self.add_item(self.select)

    async def on_rating_select(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("❌ Nie możesz ocenić tego ticketu.", ephemeral=True)
            return

        rating = int(interaction.data["values"][0])
        user_ratings[self.user.id] = rating

        oceny_channel = interaction.client.get_channel(OCENY_CHANNEL_ID)
        if oceny_channel:
            embed = discord.Embed(
                title="🌟 Nowa ocena ticketu",
                description=f"**Użytkownik:** {self.user.mention}\n"
                            f"**Ocena:** {rating} ⭐",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            await oceny_channel.send(embed=embed)

        await interaction.response.send_message("✅ Dziękujemy za ocenę!", ephemeral=True)
        self.stop()

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
        self.selected_items = []

        items = SERVER_OPTIONS.get(self.selected_server, {}).get(self.selected_mode, [])
        self.items_select = Select(
            placeholder="Wybierz itemy",
            options=[discord.SelectOption(label=item) for item in items],
            max_values=len(items),
            custom_id="items_select"
        )
        self.items_select.callback = self.item_callback

        self.clear_items()
        self.add_item(self.server_select)
        self.add_item(self.mode_select)
        self.add_item(self.items_select)
        self.add_item(CloseTicketButton(self.channel, self.member.id))
        await interaction.response.edit_message(view=self)

    async def item_callback(self, interaction: discord.Interaction):
        self.selected_items = interaction.data['values']

        # Logowanie wyborów do kanału logów
        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(
                title="🛒 Nowe zamówienie",
                description=f"**Użytkownik:** {self.member.mention}\n"
                            f"**Serwer:** {self.selected_server}\n"
                            f"**Tryb:** {self.selected_mode}\n"
                            f"**Itemy:** {', '.join(self.selected_items)}",
                color=discord.Color.blue(),
                timestamp=datetime.utcnow()
            )
            # Dodaj przycisk "Zrealizuj"
            view = View()
            view.add_item(RealizeButton(self.member))
            await log_channel.send(embed=embed, view=view)

        await interaction.response.send_message("✅ Twoje zamówienie zostało zapisane i wysłane do logów.", ephemeral=True)

        # Opcjonalnie można wyłączyć widok, żeby zapobiec ponownemu wyborowi
        self.clear_items()
        self.add_item(CloseTicketButton(self.channel, self.member.id))
        await interaction.message.edit(view=self)

# Uruchom bota
bot.run(os.getenv("TOKEN"))
