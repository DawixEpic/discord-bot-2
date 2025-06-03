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
        if not discord.utils.get(interaction.user.roles, id=ADMIN_ROLE_ID):
            return await interaction.response.send_message("⛔ Tylko administrator może oznaczyć jako zrealizowane.", ephemeral=True)

        await interaction.message.delete()
        rating_channel = interaction.guild.get_channel(RATING_CHANNEL_ID)
        if rating_channel:
            embed = discord.Embed(title="📝 Oceń realizację", color=discord.Color.orange())
            embed.add_field(name="Użytkownik", value=self.user.mention, inline=False)
            embed.add_field(name="Data", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), inline=True)
            embed.add_field(name="Zamówienie", value=", ".join(self.items), inline=False)
            embed.set_footer(text="Wybierz ocenę klikając w menu poniżej:")
            await rating_channel.send(embed=embed, view=RatingView(self.user, interaction.channel))

# --- SYSTEM OCEN ---
class RatingView(discord.ui.View):
    def __init__(self, user, ticket_channel):
        super().__init__(timeout=None)
        self.user = user
        self.ticket_channel = ticket_channel
        self.voted_users = set()

    @discord.ui.select(placeholder="⭐ Wybierz ocenę", options=[
        discord.SelectOption(label="⭐", value="1"),
        discord.SelectOption(label="⭐⭐", value="2"),
        discord.SelectOption(label="⭐⭐⭐", value="3"),
        discord.SelectOption(label="⭐⭐⭐⭐", value="4"),
        discord.SelectOption(label="⭐⭐⭐⭐⭐", value="5"),
    ])
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

# --- PRZYCISK DO ZAMKNIĘCIA TICKETA ---
class CloseButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="❌ Zamknij ticket", style=discord.ButtonStyle.danger)
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if discord.utils.get(interaction.user.roles, id=ADMIN_ROLE_ID):
            await interaction.channel.delete(reason="Ticket zamknięty przez admina.")
        else:
            await interaction.response.send_message("❌ Tylko administrator może zamknąć ten ticket.", ephemeral=True)

# --- MODAL NA KWOTĘ ---
class AmountModal(discord.ui.Modal, title="💵 Podaj kwotę"):
    amount = discord.ui.TextInput(label="Kwota", placeholder="Np. 50k$", required=True)

    def __init__(self, parent_view):
        super().__init__()
        self.parent_view = parent_view

    async def on_submit(self, interaction: discord.Interaction):
        self.parent_view.items.append(f"💰 {self.amount.value}")
        await self.parent_view.finish(interaction)

# --- MODAL NA OPIS SPRZEDAŻY ---
class SellModal(discord.ui.Modal, title="📝 Opisz, co chcesz sprzedać"):
    description = discord.ui.TextInput(label="Opis", style=discord.TextStyle.paragraph, placeholder="Napisz, co chcesz sprzedać...", required=True)

    def __init__(self, parent_view):
        super().__init__()
        self.parent_view = parent_view

    async def on_submit(self, interaction: discord.Interaction):
        self.parent_view.items.append(self.description.value)
        await self.parent_view.finish(interaction)

# --- WIDOK WYBORU KUPNA/SPRZEDAŻY ---
class BuySellView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(placeholder="Wybierz opcję", options=[
        discord.SelectOption(label="Kup", description="Złóż zamówienie na zakup", value="buy"),
        discord.SelectOption(label="Sprzedaj", description="Wystaw ofertę sprzedaży", value="sell")
    ])
    async def buy_sell_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        if select.values[0] == "buy":
            await interaction.response.send_message("Wybierz serwer:", view=ServerSelectView(buy=True), ephemeral=True)
        else:
            await interaction.response.send_message("Wybierz serwer do sprzedaży:", view=ServerSelectView(buy=False), ephemeral=True)

# --- WIDOK WYBORU SERWERA ---
class ServerSelectView(discord.ui.View):
    def __init__(self, buy: bool):
        super().__init__(timeout=180)
        self.buy = buy
        options = [discord.SelectOption(label=server, value=server) for server in SERVER_OPTIONS.keys()]
        self.server_select = discord.ui.Select(placeholder="Wybierz serwer", options=options, custom_id="server_select")
        self.server_select.callback = self.server_selected
        self.add_item(self.server_select)

    async def server_selected(self, interaction: discord.Interaction):
        server = self.server_select.values[0]
        if self.buy:
            await interaction.response.send_message("Wybierz tryb:", view=ModeSelectView(server, buy=True), ephemeral=True)
        else:
            await interaction.response.send_message("Wybierz tryb sprzedaży:", view=ModeSelectView(server, buy=False), ephemeral=True)

# --- WIDOK WYBORU TRYBU ---
class ModeSelectView(discord.ui.View):
    def __init__(self, server, buy: bool):
        super().__init__(timeout=180)
        self.server = server
        self.buy = buy
        options = [discord.SelectOption(label=mode, value=mode) for mode in SERVER_OPTIONS[server].keys()]
        self.mode_select = discord.ui.Select(placeholder="Wybierz tryb", options=options)
        self.mode_select.callback = self.mode_selected
        self.add_item(self.mode_select)

    async def mode_selected(self, interaction: discord.Interaction):
        mode = self.mode_select.values[0]
        if self.buy:
            await interaction.response.send_message("Wybierz item:", view=ItemSelectView(self.server, mode, buy=True), ephemeral=True)
        else:
            # W przypadku sprzedaży – modal z opisem
            view = SellOrderFinalizer(interaction.user, self.server, mode)
            await interaction.response.send_modal(SellModal(view))

# --- WIDOK WYBORU ITEMU (DLA KUPNA) ---
class ItemSelectView(discord.ui.View):
    def __init__(self, server, mode, buy: bool):
        super().__init__(timeout=180)
        self.server = server
        self.mode = mode
        self.buy = buy
        options = []
        for item in SERVER_OPTIONS[server][mode]:
            options.append(discord.SelectOption(label=item, value=item))
        self.item_select = discord.ui.Select(placeholder="Wybierz item", options=options)
        self.item_select.callback = self.item_selected
        self.add_item(self.item_select)

    async def item_selected(self, interaction: discord.Interaction):
        item = self.item_select.values[0]
        if item == "💰 Kasa":
            modal = AmountModal(self)
            await interaction.response.send_modal(modal)
        else:
            self.items = [item]
            await self.finish(interaction)

    async def finish(self, interaction: discord.Interaction):
        # Tworzymy ticket
        guild = interaction.guild
        category = guild.get_channel(TICKET_CATEGORY_ID)
        channel = await guild.create_text_channel(f"kupno-{interaction.user.name}", category=category)
        await channel.set_permissions(interaction.user, read_messages=True, send_messages=True)
        await channel.set_permissions(guild.default_role, read_messages=False)
        await channel.set_permissions(discord.utils.get(guild.roles, id=ADMIN_ROLE_ID), read_messages=True, send_messages=True)

        embed = discord.Embed(title="🛒 Nowe zamówienie kupna", color=discord.Color.green())
        embed.add_field(name="Użytkownik", value=interaction.user.mention, inline=False)
        embed.add_field(name="Serwer", value=self.server, inline=True)
        embed.add_field(name="Tryb", value=self.mode, inline=True)
        embed.add_field(name="Oferta", value="\n".join(self.items), inline=False)
        await channel.send(embed=embed, view=CloseButton())

        # Logowanie
        log_channel = guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed_log = discord.Embed(title="Nowe zamówienie kupna", color=discord.Color.green())
            embed_log.add_field(name="Użytkownik", value=interaction.user.mention, inline=False)
            embed_log.add_field(name="Serwer", value=self.server, inline=True)
            embed_log.add_field(name="Tryb", value=self.mode, inline=True)
            embed_log.add_field(name="Oferta", value="\n".join(self.items), inline=False)
            await log_channel.send(embed=embed_log, view=RealizujView(interaction.user, self.items))

        await interaction.response.send_message("✅ Twoje zamówienie zostało wysłane!", ephemeral=True)

# --- FINALIZATOR SPRZEDAŻY ---
class SellOrderFinalizer:
    def __init__(self, user, server, mode):
        self.user = user
        self.server = server
        self.mode = mode
        self.items = []

    async def finish(self, interaction: discord.Interaction):
        # Tworzymy ticket sprzedaży
        guild = interaction.guild
        category = guild.get_channel(TICKET_CATEGORY_ID)
        channel = await guild.create_text_channel(f"sprzedaz-{self.user.name}", category=category)
        await channel.set_permissions(self.user, read_messages=True, send_messages=True)
        await channel.set_permissions(guild.default_role, read_messages=False)
        await channel.set_permissions(discord.utils.get(guild.roles, id=ADMIN_ROLE_ID), read_messages=True, send_messages=True)

        embed = discord.Embed(title="🛒 Nowa oferta sprzedaży", color=discord.Color.blue())
        embed.add_field(name="Użytkownik", value=self.user.mention, inline=False)
        embed.add_field(name="Serwer", value=self.server, inline=True)
        embed.add_field(name="Tryb", value=self.mode, inline=True)
        embed.add_field(name="Oferta", value="\n".join(self.items), inline=False)
        await channel.send(embed=embed, view=CloseButton())

        # Logowanie
        log_channel = guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed_log = discord.Embed(title="Nowa oferta sprzedaży", color=discord.Color.blue())
            embed_log.add_field(name="Użytkownik", value=self.user.mention, inline=False)
            embed_log.add_field(name="Serwer", value=self.server, inline=True)
            embed_log.add_field(name="Tryb", value=self.mode, inline=True)
            embed_log.add_field(name="Oferta", value="\n".join(self.items), inline=False)
            await log_channel.send(embed=embed_log, view=RealizujView(self.user, self.items))

        await interaction.response.send_message("✅ Twoja oferta została wysłana!", ephemeral=True)

# --- KOMENDA STARTOWA ---
@bot.command()
@commands.guild_only()
async def start(ctx):
    if ctx.channel.id != VERIFY_CHANNEL_ID:
        await ctx.send("❌ Komendę można użyć tylko na kanale weryfikacji.")
        return
    await ctx.send("Kliknij przycisk, aby się zweryfikować:", view=WeryfikacjaButton())

# --- EVENT ON_READY ---
@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user}!")
    guild = bot.get_guild(GUILD_ID)
    verify_channel = guild.get_channel(VERIFY_CHANNEL_ID)
    # Wysyłamy wiadomość weryfikacyjną tylko raz na starcie (odkomentuj, jeśli chcesz)
    # await verify_channel.send("Kliknij przycisk, aby się zweryfikować:", view=WeryfikacjaButton())

# --- KOMENDA WYŚWIETLAJĄCA MENU BUY/SELL ---
@bot.command()
@commands.guild_only()
async def oferta(ctx):
    await ctx.send("Wybierz opcję:", view=BuySellView())

bot.run("TWÓJ_TOKEN_TUTAJ")
