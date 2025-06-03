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

# --- ZAMYKANIE TICKETA ---
class CloseButton(discord.ui.View):
    @discord.ui.button(label="❌ Zamknij ticket", style=discord.ButtonStyle.danger)
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if discord.utils.get(interaction.user.roles, id=ADMIN_ROLE_ID):
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
        self.parent_view.items.append(self.description.value)
        await self.parent_view.finish(interaction)

# --- WIDOKI ---
class BuySellView(discord.ui.View):
    @discord.ui.select(placeholder="Wybierz opcję", options=[
        discord.SelectOption(label="Kup", value="buy"),
        discord.SelectOption(label="Sprzedaj", value="sell"),
    ])
    async def buy_sell_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        await interaction.response.send_message("Wybierz serwer:", view=ServerSelectView(buy=(select.values[0] == "buy")), ephemeral=True)

class ServerSelectView(discord.ui.View):
    def __init__(self, buy):
        super().__init__()
        self.buy = buy
        options = [discord.SelectOption(label=s) for s in SERVER_OPTIONS.keys()]
        select = discord.ui.Select(placeholder="Wybierz serwer", options=options)
        select.callback = self.server_selected
        self.add_item(select)

    async def server_selected(self, interaction):
        server = interaction.data["values"][0]
        await interaction.response.send_message("Wybierz tryb:", view=ModeSelectView(server, self.buy), ephemeral=True)

class ModeSelectView(discord.ui.View):
    def __init__(self, server, buy):
        super().__init__()
        self.server = server
        self.buy = buy
        options = [discord.SelectOption(label=m) for m in SERVER_OPTIONS[server].keys()]
        select = discord.ui.Select(placeholder="Wybierz tryb", options=options)
        select.callback = self.mode_selected
        self.add_item(select)

    async def mode_selected(self, interaction):
        mode = interaction.data["values"][0]
        if self.buy:
            await interaction.response.send_message("Wybierz przedmiot:", view=ItemSelectView(self.server, mode), ephemeral=True)
        else:
            await interaction.response.send_modal(SellModal(self))

class ItemSelectView(discord.ui.View):
    def __init__(self, server, mode):
        super().__init__()
        self.server = server
        self.mode = mode
        self.items = []
        options = []
        for item in SERVER_OPTIONS[server][mode]:
            if item == "💰 Kasa":
                options.append(discord.SelectOption(label=item, description="Wpisz własną kwotę"))
            else:
                options.append(discord.SelectOption(label=item))
        select = discord.ui.Select(placeholder="Wybierz item", options=options)
        select.callback = self.item_selected
        self.add_item(select)

    async def item_selected(self, interaction):
        selected_item = interaction.data["values"][0]
        if selected_item == "💰 Kasa":
            await interaction.response.send_modal(AmountModal(self))
        else:
            self.items.append(selected_item)
            await self.finish(interaction)

    async def finish(self, interaction):
        # Sprawdź, czy ticket już istnieje
        guild = interaction.guild
        existing = discord.utils.get(guild.channels, topic=f"ticket-{interaction.user.id}")
        if existing:
            await interaction.response.send_message("Masz już otwarty ticket.", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.get_role(ADMIN_ROLE_ID): discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=guild.get_channel(TICKET_CATEGORY_ID),
            overwrites=overwrites,
            topic=f"ticket-{interaction.user.id}"
        )

        desc = "\n".join(self.items)
        embed = discord.Embed(title="🛒 Nowe zamówienie", color=discord.Color.blue())
        embed.add_field(name="Użytkownik", value=interaction.user.mention, inline=False)
        embed.add_field(name="Zamówienie", value=desc, inline=False)
        embed.add_field(name="Data", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), inline=True)
        await ticket_channel.send(embed=embed, view=CloseButton())
        await interaction.response.send_message(f"Ticket został utworzony: {ticket_channel.mention}", ephemeral=True)

        # Logowanie do kanału logów
        log_channel = guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(title="📥 Nowe zamówienie", color=discord.Color.green())
            log_embed.add_field(name="Użytkownik", value=interaction.user.mention, inline=False)
            log_embed.add_field(name="Zamówienie", value=desc, inline=False)
            log_embed.add_field(name="Data", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), inline=True)
            await log_channel.send(embed=log_embed, view=RealizujView(interaction.user, self.items))

# --- KOMENDA STARTOWA WYSYŁAJĄCA PRZYCISK WERYFIKACJI ---
@bot.command()
@commands.has_permissions(administrator=True)
async def wyslij_weryfikacje(ctx):
    if ctx.channel.id != VERIFY_CHANNEL_ID:
        await ctx.send(f"Ta komenda działa tylko na kanale <#{VERIFY_CHANNEL_ID}>.")
        return
    await ctx.send("Kliknij poniższy przycisk, aby się zweryfikować:", view=WeryfikacjaButton())

@bot.event
async def on_ready():
    print(f"✅ Bot zalogowany jako {bot.user}")

bot.add_view(WeryfikacjaButton())
bot.add_view(BuySellView())
bot.add_view(CloseButton())
bot.add_view(RealizujView(None, []))  # dummy, by przyciski działały po restarcie

bot.run("TWÓJ_TOKEN_TUTAJ")
