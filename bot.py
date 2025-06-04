import discord
from discord.ext import commands
from datetime import datetime

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- KONFIGURACJA ---
GUILD_ID = 1373253103176122399
ROLE_ID = 1373275307150278686
VERIFY_CHANNEL_ID = 1373258480382771270
TICKET_CHANNEL_ID = 1373305137228939416
TICKET_CATEGORY_ID = 1373277957446959135
LOG_CHANNEL_ID = 1374479815914291240
ADMIN_ROLE_ID = 1373275898375176232
RATING_CHANNEL_ID = 1375528888586731762

SERVER_OPTIONS = {
    "𝐂𝐑𝐀𝐅𝐓𝐏𝐋𝐀𝐘": {
        "𝐆𝐈𝐋𝐃𝐈𝐄": ["Elytra", "Buty flasha", "Miecz 6", "💰 Kasa", "Shulker s2", "Shulker totemów"],
        "𝐁𝐎𝐗𝐏𝐕𝐏": ["Set 25", "Miecz 25", "Kilof 25", "💰 Kasa"]
    },
    "𝐀𝐍𝐀𝐑𝐂𝐇𝐈𝐀": {
        "𝐋𝐈𝐅𝐄𝐒𝐓𝐄𝐀𝐋": ["💰 Kasa", "Anarchiczny set 2", "Anarchiczny set 1", "Anarchiczny miecz", "Zajęczy miecz", "Totem ułaskawienia", "Excalibur"],
        "𝐁𝐎𝐗𝐏𝐕𝐏": ["💰 Kasa", "Excalibur", "Totem ułaskawienia", "Sakiewka"]
    },
    "𝐑𝐀𝐏𝐘": {
        "𝐋𝐈𝐅𝐄𝐒𝐓𝐄𝐀𝐋": ["nie dostępne", "nie dostępne", "nie dostępne"],
        "𝐁𝐎𝐗𝐏𝐕𝐏": ["💰 Kasa", "Miecz 35", "Set 35"]
    },
    "𝐏𝐘𝐊𝐌𝐂": {
        "𝐋𝐈𝐅𝐄𝐒𝐓𝐄𝐀𝐋": ["💰 Kasa", "Buda", "Love swap", "Klata meduzy"],
        "𝐁𝐎𝐗𝐏𝐕𝐏": ["nie dostępne", "nie dostępne", "nie dostępne"]
    }
}

# --- WERYFIKACJA ---
class WeryfikacjaButton(discord.ui.View):
    @discord.ui.button(label="Zweryfikuj się ✅", style=discord.ButtonStyle.success, custom_id="verify_button")
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(ROLE_ID)
        if role in interaction.user.roles:
            await interaction.response.send_message("🔔 Już masz tę rolę!", ephemeral=True)
        else:
            try:
                await interaction.user.add_roles(role)
                await interaction.response.send_message("✅ Zostałeś zweryfikowany!", ephemeral=True)
            except discord.Forbidden:
                await interaction.response.send_message("❌ Nie mam uprawnień, aby nadać Ci rolę.", ephemeral=True)

# --- PRZYCISK "ZREALIZUJ" W LOGACH ---
class RealizujView(discord.ui.View):
    def __init__(self, user, items):
        super().__init__(timeout=None)
        self.user = user
        self.items = items

    @discord.ui.button(label="Zrealizuj ✅", style=discord.ButtonStyle.success)
    async def finish(self, interaction: discord.Interaction, button: discord.ui.Button):
        admin_role = interaction.guild.get_role(ADMIN_ROLE_ID)
        if admin_role not in interaction.user.roles:
            return await interaction.response.send_message("⛔ Tylko administrator może oznaczyć jako zrealizowane.", ephemeral=True)

        await interaction.message.delete()
        rating_channel = interaction.guild.get_channel(RATING_CHANNEL_ID)
        if rating_channel:
            embed = discord.Embed(title="📝 Oceń realizację", color=discord.Color.orange())
            embed.add_field(name="Użytkownik", value=self.user.mention, inline=False)
            embed.add_field(name="Data", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), inline=True)
            embed.add_field(name="Zamówienie", value=", ".join(self.items), inline=False)
            embed.set_footer(text="Wybierz ocenę klikając w menu poniżej:")
            await rating_channel.send(embed=embed, view=RatingView(self.user))
        await interaction.response.send_message("✅ Oznaczono jako zrealizowane.", ephemeral=True)

# --- SYSTEM OCEN ---
class RatingView(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=None)
        self.user = user
        self.voted_users = set()

    @discord.ui.select(
        placeholder="⭐ Wybierz ocenę",
        options=[
            discord.SelectOption(label="⭐", value="1"),
            discord.SelectOption(label="⭐⭐", value="2"),
            discord.SelectOption(label="⭐⭐⭐", value="3"),
            discord.SelectOption(label="⭐⭐⭐⭐", value="4"),
            discord.SelectOption(label="⭐⭐⭐⭐⭐", value="5"),
        ],
        custom_id="rating_select"
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        if interaction.user.id in self.voted_users:
            return await interaction.response.send_message("⛔ Już oddałeś ocenę.", ephemeral=True)
        self.voted_users.add(interaction.user.id)

        rating_channel = interaction.guild.get_channel(RATING_CHANNEL_ID)
        embed = discord.Embed(title="🌟 Nowa ocena", color=discord.Color.green())
        embed.add_field(name="Użytkownik oceniający", value=interaction.user.mention, inline=False)
        embed.add_field(name="Oceniono użytkownika", value=self.user.mention, inline=False)
        embed.add_field(name="Ocena", value=f"{select.values[0]} ⭐", inline=False)
        embed.add_field(name="Data", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), inline=False)
        await rating_channel.send(embed=embed)

        await interaction.message.delete()
        await interaction.response.send_message(f"Dziękujemy za ocenę: {select.values[0]} ⭐", ephemeral=True)

# --- ZAMYKANIE TICKETA ---
class CloseButton(discord.ui.View):
    @discord.ui.button(label="❌ Zamknij ticket", style=discord.ButtonStyle.danger)
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        admin_role = interaction.guild.get_role(ADMIN_ROLE_ID)
        if admin_role in interaction.user.roles:
            await interaction.channel.delete(reason="Ticket zamknięty przez admina.")
        else:
            await interaction.response.send_message("❌ Tylko administrator może zamknąć ten ticket.", ephemeral=True)

# --- MODALE ---
class AmountModal(discord.ui.Modal, title="💵 Podaj kwotę"):
    amount = discord.ui.TextInput(label="Kwota", placeholder="Np. 50k$", required=True)

    def __init__(self, parent_view):
        super().__init__()
        self.parent_view = parent_view

    async def on_submit(self, interaction: discord.Interaction):
        self.parent_view.items.append(f"💰 {self.amount.value}")
        await self.parent_view.finish(interaction)

class SellModal(discord.ui.Modal, title="📝 Opisz, co chcesz sprzedać"):
    description = discord.ui.TextInput(label="Opis", style=discord.TextStyle.paragraph, required=True)

    def __init__(self, parent_view):
        super().__init__()
        self.parent_view = parent_view

    async def on_submit(self, interaction: discord.Interaction):
        self.parent_view.items = [self.description.value]  # W trybie sprzedaży tylko opis
        await self.parent_view.finish(interaction)

# --- WIDOKI ---

class BuySellView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
        self.items = []  # żeby zachować zamówienie w trybie sprzedaży

    @discord.ui.select(
        placeholder="Wybierz opcję",
        options=[
            discord.SelectOption(label="Kup", value="buy", emoji="💰"),
            discord.SelectOption(label="Sprzedaj", value="sell", emoji="💸")
        ],
        custom_id="buy_sell_select"
    )
    async def buy_sell_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        choice = select.values[0]
        if choice == "buy":
            # Wyświetlamy menu wyboru serwera
            await interaction.response.send_message("Wybierz serwer:", view=ServerSelectView(self), ephemeral=True)
        else:
            # Modal do wpisania, co chcesz sprzedać
            await interaction.response.send_modal(SellModal(self))

    async def finish(self, interaction: discord.Interaction):
        # Wywoływane po wyborze lub wpisaniu szczegółów
        guild = interaction.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=guild.get_channel(TICKET_CATEGORY_ID),
            overwrites=overwrites,
            reason="Nowy ticket"
        )
        embed = discord.Embed(title="🎫 Nowy ticket", color=discord.Color.blue())
        embed.add_field(name="Użytkownik", value=interaction.user.mention, inline=False)
        embed.add_field(name="Zamówienie", value=", ".join(self.items), inline=False)
        await ticket_channel.send(embed=embed, view=CloseButton())

        # Log do kanału logów z przyciskiem zrealizuj
        log_channel = guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(embed=embed, view=RealizujView(interaction.user, self.items))

        await interaction.followup.send(f"✅ Twój ticket został utworzony: {ticket_channel.mention}", ephemeral=True)

class ServerSelectView(discord.ui.View):
    def __init__(self, parent_view):
        super().__init__(timeout=60)
        self.parent_view = parent_view
        options = [discord.SelectOption(label=server) for server in SERVER_OPTIONS.keys()]
        self.select = discord.ui.Select(placeholder="Wybierz serwer", options=options)
        self.select.callback = self.server_callback
        self.add_item(self.select)

    async def server_callback(self, interaction: discord.Interaction):
        selected_server = self.select.values[0]
        await interaction.response.edit_message(content=f"Wybierz tryb dla serwera **{selected_server}**:", view=ModeSelectView(self.parent_view, selected_server))

class ModeSelectView(discord.ui.View):
    def __init__(self, parent_view, server):
        super().__init__(timeout=60)
        self.parent_view = parent_view
        self.server = server
        modes = SERVER_OPTIONS[server].keys()
        options = [discord.SelectOption(label=mode) for mode in modes]
        self.select = discord.ui.Select(placeholder="Wybierz tryb", options=options)
        self.select.callback = self.mode_callback
        self.add_item(self.select)

    async def mode_callback(self, interaction: discord.Interaction):
        selected_mode = self.select.values[0]
        items = SERVER_OPTIONS[self.server][selected_mode]
        options = [discord.SelectOption(label=item) for item in items]
        await interaction.response.edit_message(content=f"Wybierz przedmiot / opcję dla trybu **{selected_mode}**:", view=ItemSelectView(self.parent_view, self.server, selected_mode, options))

class ItemSelectView(discord.ui.View):
    def __init__(self, parent_view, server, mode, options):
        super().__init__(timeout=180)
        self.parent_view = parent_view
        self.server = server
        self.mode = mode
        self.items = []
        self.select = discord.ui.Select(placeholder="Wybierz przedmiot (możesz wybrać kilka)", options=options, max_values=len(options))
        self.select.callback = self.item_callback
        self.add_item(self.select)

    async def item_callback(self, interaction: discord.Interaction):
        self.items = self.select.values

        if "💰 Kasa" in self.items:
            # Usuń "💰 Kasa" z listy, modal będzie pytał o kwotę
            self.items.remove("💰 Kasa")
            self.parent_view.items = self.items.copy()
            await interaction.response.send_modal(AmountModal(self.parent_view))
        else:
            self.parent_view.items = self.items
            await self.parent_view.finish(interaction)

# --- KOMENDA START ---
@bot.event
async def on_ready():
    print(f"Bot zalogowany jako {bot.user}!")
    guild = bot.get_guild(GUILD_ID)
    channel = guild.get_channel(VERIFY_CHANNEL_ID)
    await channel.purge(limit=10)
    view = WeryfikacjaButton()
    await channel.send("Kliknij przycisk, aby się zweryfikować!", view=view)

# --- URUCHOMIENIE BOTA ---
bot.run("TWÓJ_TOKEN_TUTAJ")
