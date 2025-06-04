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
            discord.SelectOption(label="Sprzedaj", value="sell", emoji="🛒")
        ],
        custom_id="buy_sell_select"
    )
    async def buy_sell_selected(self, interaction: discord.Interaction, select: discord.ui.Select):
        choice = select.values[0]
        if choice == "buy":
            await interaction.response.edit_message(content="Wybierz serwer:", view=ServerSelectView(self))
        else:  # Sprzedaj - otwórz modal do wpisania opisu sprzedaży
            await interaction.response.send_modal(SellModal(self))
            # Ukryj wiadomość z wyborem bo przechodzimy do modala
            await interaction.message.delete()

    async def finish(self, interaction: discord.Interaction):
        # Po finalizacji tworzymy kanał ticketu
        guild = interaction.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.get_role(ADMIN_ROLE_ID): discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        category = guild.get_channel(TICKET_CATEGORY_ID)
        channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=category,
            overwrites=overwrites,
            reason="Nowy ticket"
        )
        embed = discord.Embed(title="🎫 Ticket", color=discord.Color.blue())
        embed.add_field(name="Użytkownik", value=interaction.user.mention, inline=False)
        embed.add_field(name="Zamówienie", value="\n".join(self.items), inline=False)
        await channel.send(embed=embed, view=CloseButton())

        # Logowanie do kanału logów
        log_channel = guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed_log = discord.Embed(title="Nowe zamówienie", color=discord.Color.gold())
            embed_log.add_field(name="Użytkownik", value=interaction.user.mention, inline=False)
            embed_log.add_field(name="Data", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), inline=True)
            embed_log.add_field(name="Zamówienie", value="\n".join(self.items), inline=False)
            await log_channel.send(embed=embed_log, view=RealizujView(interaction.user, self.items))

        await interaction.followup.send("✅ Ticket został utworzony!", ephemeral=True)

class ServerSelectView(discord.ui.View):
    def __init__(self, parent_view):
        super().__init__(timeout=180)
        self.parent_view = parent_view

    @discord.ui.select(
        placeholder="Wybierz serwer",
        options=[discord.SelectOption(label=server) for server in SERVER_OPTIONS.keys()],
        custom_id="server_select"
    )
    async def server_selected(self, interaction: discord.Interaction, select: discord.ui.Select):
        server_name = select.values[0]
        self.parent_view.server_name = server_name
        await interaction.response.edit_message(content="Wybierz tryb:", view=ModeSelectView(self.parent_view, server_name))

class ModeSelectView(discord.ui.View):
    def __init__(self, parent_view, server_name):
        super().__init__(timeout=180)
        self.parent_view = parent_view
        self.server_name = server_name

    @discord.ui.select(
        placeholder="Wybierz tryb",
        options=[discord.SelectOption(label=mode) for mode in SERVER_OPTIONS.get(self.server_name, {})],
        custom_id="mode_select"
    )
    async def mode_selected(self, interaction: discord.Interaction, select: discord.ui.Select):
        mode_name = select.values[0]
        self.parent_view.mode_name = mode_name
        await interaction.response.edit_message(content="Wybierz item:", view=ItemSelectView(self.parent_view, self.server_name, mode_name))

class ItemSelectView(discord.ui.View):
    def __init__(self, parent_view, server_name, mode_name):
        super().__init__(timeout=180)
        self.parent_view = parent_view
        self.server_name = server_name
        self.mode_name = mode_name

    @discord.ui.select(
        placeholder="Wybierz item",
        options=[discord.SelectOption(label=item) for item in SERVER_OPTIONS.get(self.server_name, {}).get(self.mode_name, [])],
        custom_id="item_select"
    )
    async def item_selected(self, interaction: discord.Interaction, select: discord.ui.Select):
        item = select.values[0]
        if item == "💰 Kasa":
            # Otwórz modal wpisania kwoty
            await interaction.response.send_modal(AmountModal(self.parent_view))
            # Ukryj wiadomość z wyborem itemu, bo czekamy na modal
            await interaction.message.delete()
        else:
            self.parent_view.items.append(item)
            await self.parent_view.finish(interaction)

# --- KOMENDA /verify ---
@bot.command()
@commands.has_permissions(administrator=True)
async def setupverify(ctx):
    if ctx.channel.id != VERIFY_CHANNEL_ID:
        await ctx.send(f"Ta komenda działa tylko na kanale <#{VERIFY_CHANNEL_ID}>")
        return
    embed = discord.Embed(title="Weryfikacja", description="Kliknij przycisk, aby się zweryfikować.", color=discord.Color.green())
    view = WeryfikacjaButton()
    await ctx.send(embed=embed, view=view)

# --- KOMENDA /ticket ---
@bot.command()
async def ticket(ctx):
    if ctx.channel.id != TICKET_CHANNEL_ID:
        await ctx.send(f"Proszę używać tej komendy na kanale <#{TICKET_CHANNEL_ID}>")
        return
    view = BuySellView()
    embed = discord.Embed(title="Tworzenie ticketu", description="Wybierz, czy chcesz kupić czy sprzedać.", color=discord.Color.blue())
    await ctx.send(embed=embed, view=view)

bot.run("TWÓJ_TOKEN_TUTAJ")
