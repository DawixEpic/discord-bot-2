import discord
from discord.ext import commands
from discord.ui import View, Button, Select
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
RATING_CHANNEL_ID = 1375528888586731762  # kanał ocen publicznych

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

# Słownik do przechowywania danych zamówienia czekających na ocenę (user_id -> data)
pending_ratings = {}

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
                            f"**Itemy:** {', '.join(self.selected_items)}",
                color=discord.Color.gold(),
                timestamp=datetime.utcnow()
            )
            # Dodaj przycisk zrealizowane do wiadomości w logach
            view = RealizedButtonView(interaction.user, self.selected_server, self.selected_mode, self.selected_items)
            await log_channel.send(embed=embed, view=view)

class RealizedButton(Button):
    def __init__(self, user, server, mode, items):
        super().__init__(label="Zrealizowane", style=discord.ButtonStyle.success)
        self.user = user
        self.server = server
        self.mode = mode
        self.items = items

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("❌ Nie masz uprawnień do oznaczenia jako zrealizowane.", ephemeral=True)
            return
        
        # Dodaj dane do pending_ratings, aby użytkownik mógł ocenić
        pending_ratings[self.user.id] = {
            "server": self.server,
            "mode": self.mode,
            "items": self.items,
            "date": datetime.utcnow()
        }
        await interaction.response.send_message(f"✅ Zamówienie użytkownika {self.user.display_name} zostało oznaczone jako zrealizowane. Użytkownik może teraz wystawić ocenę.", ephemeral=True)
        # Możemy też wysłać do użytkownika DM z prośbą o ocenę
        try:
            dm = await self.user.create_dm()
            await dm.send(
                f"Cześć {self.user.display_name}! Twoje zamówienie na serwerze **{self.server}** zostało oznaczone jako zrealizowane.\n"
                f"Proszę oceń swoje doświadczenie, wybierając ocenę od 1 do 5 poniżej.",
                view=RatingView(self.user.id)
            )
        except:
            # Jeśli DM nie można wysłać (np. użytkownik ma DM zablokowane), po prostu ignorujemy
            pass

        # Usuń przycisk zrealizowane z tej wiadomości
        await interaction.message.edit(view=None)

class RealizedButtonView(View):
    def __init__(self, user, server, mode, items):
        super().__init__(timeout=None)
        self.add_item(RealizedButton(user, server, mode, items))

class RatingButton(Button):
    def __init__(self, label, rating, user_id):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.rating = rating
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Nie możesz ocenić czyjegoś zamówienia.", ephemeral=True)
            return

        rating_data = pending_ratings.pop(self.user_id, None)
        if not rating_data:
            await interaction.response.send_message("❌ Twoje zamówienie nie jest już dostępne do oceny.", ephemeral=True)
            return

        embed = discord.Embed(
            title="⭐ Nowa ocena zamówienia",
            color=discord.Color.blurple(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Użytkownik", value=interaction.user.mention, inline=True)
        embed.add_field(name="Ocena", value=f"{self.rating} / 5", inline=True)
        embed.add_field(name="Serwer", value=rating_data["server"], inline=False)
        embed.add_field(name="Tryb", value=rating_data["mode"], inline=False)
        embed.add_field(name="Itemy", value=", ".join(rating_data["items"]), inline=False)
        embed.add_field(name="Data zamówienia", value=rating_data["date"].strftime("%Y-%m-%d %H:%M:%S UTC"), inline=False)

        rating_channel = bot.get_channel(RATING_CHANNEL_ID)
        if rating_channel:
            await rating_channel.send(embed=embed)

        await interaction.response.send_message("Dziękujemy za Twoją ocenę! :)", ephemeral=True)
        await interaction.message.delete()

class RatingView(View):
    def __init__(self, user_id):
        super().__init__(timeout=300)  # 5 min na ocenę
        for i in range(1, 6):
            self.add_item(RatingButton(str(i), i, user_id))

@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f"❌ Wystąpił błąd: {error}")

bot.run(os.getenv("TOKEN"))
