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
        # Sprawdzenie uprawnień administratora
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
            await rating_channel.send(embed=embed, view=RatingView(self.user, interaction.channel))
        await interaction.response.send_message("✅ Oznaczono jako zrealizowane.", ephemeral=True)

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
        select = discord.ui.Select(placeholder="Wybierz serwer", options=options, custom_id="server_select")
        select.callback = self.server_selected
        self.add_item(select)

    async def server_selected(self, interaction: discord.Interaction):
        server = interaction.data['values'][0]
        if self.buy:
            await interaction.response.send_message(f"Wybierz tryb na serwerze **{server}**:", view=ModeSelectView(server, buy=True), ephemeral=True)
        else:
            await interaction.response.send_modal(SellModal(self))

    async def finish(self, interaction: discord.Interaction):
        # Wysyła ticket po wybraniu opcji kupna/sprzedaży
        channel = interaction.guild.get_channel(TICKET_CHANNEL_ID)
        if not channel:
            await interaction.response.send_message("Nie mogę znaleźć kanału ticketów.", ephemeral=True)
            return
        ticket_category = interaction.guild.get_channel(TICKET_CATEGORY_ID)
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.get_role(ADMIN_ROLE_ID): discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }
        ticket_name = f"ticket-{interaction.user.name.lower()}"

        ticket = await interaction.guild.create_text_channel(ticket_name, category=ticket_category, overwrites=overwrites)
        embed = discord.Embed(title="🎫 Ticket", description="Dziękujemy za zgłoszenie!", color=discord.Color.blue())
        embed.add_field(name="Użytkownik", value=interaction.user.mention)
        embed.add_field(name="Zamówienie", value=", ".join(self.items) if hasattr(self, 'items') else "Brak danych")
        await ticket.send(embed=embed, view=CloseButton())

        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            view = RealizujView(interaction.user, self.items if hasattr(self, 'items') else [])
            embed = discord.Embed(title="Nowy ticket", color=discord.Color.green())
            embed.add_field(name="Użytkownik", value=interaction.user.mention)
            embed.add_field(name="Zamówienie", value=", ".join(self.items) if hasattr(self, 'items') else "Brak danych")
            embed.add_field(name="Kanał", value=ticket.mention)
            await log_channel.send(embed=embed, view=view)

        await interaction.response.send_message(f"Twój ticket został utworzony: {ticket.mention}", ephemeral=True)

class ModeSelectView(discord.ui.View):
    def __init__(self, server, buy):
        super().__init__()
        self.server = server
        self.buy = buy
        options = [discord.SelectOption(label=m) for m in SERVER_OPTIONS[server].keys()]
        select = discord.ui.Select(placeholder="Wybierz tryb", options=options, custom_id="mode_select")
        select.callback = self.mode_selected
        self.add_item(select)

    async def mode_selected(self, interaction: discord.Interaction):
        mode = interaction.data['values'][0]
        if self.buy:
            await interaction.response.send_message(f"Wybierz przedmioty:", view=ItemSelectView(self.server, mode), ephemeral=True)
        else:
            await interaction.response.send_message("W trybie sprzedaży wybierz serwer i wpisz opis.", ephemeral=True)

class ItemSelectView(discord.ui.View):
    def __init__(self, server, mode):
        super().__init__()
        self.server = server
        self.mode = mode
        self.items = []
        options = []
        for item in SERVER_OPTIONS[server][mode]:
            options.append(discord.SelectOption(label=item))
        select = discord.ui.Select(placeholder="Wybierz itemy", options=options, min_values=1, max_values=len(options), custom_id="item_select")
        select.callback = self.items_selected
        self.add_item(select)

    async def items_selected(self, interaction: discord.Interaction):
        selected = interaction.data['values']
        if "💰 Kasa" in selected:
            # Jeśli wybrano "💰 Kasa", pokaż modal do wpisania kwoty
            self.items = [i for i in selected if i != "💰 Kasa"]
            modal = AmountModal(self)
            await interaction.response.send_modal(modal)
        else:
            self.items = selected
            await self.finish(interaction)

    async def finish(self, interaction: discord.Interaction):
        # Wywołanie metody tworzącej ticket i logi
        parent_view = self
        channel = interaction.guild.get_channel(TICKET_CHANNEL_ID)
        if not channel:
            await interaction.response.send_message("Nie mogę znaleźć kanału ticketów.", ephemeral=True)
            return
        ticket_category = interaction.guild.get_channel(TICKET_CATEGORY_ID)
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.get_role(ADMIN_ROLE_ID): discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }
        ticket_name = f"ticket-{interaction.user.name.lower()}"
        ticket = await interaction.guild.create_text_channel(ticket_name, category=ticket_category, overwrites=overwrites)
        embed = discord.Embed(title="🎫 Ticket", description="Dziękujemy za zgłoszenie!", color=discord.Color.blue())
        embed.add_field(name="Użytkownik", value=interaction.user.mention)
        embed.add_field(name="Zamówienie", value=", ".join(self.items) if self.items else "Brak danych")
        await ticket.send(embed=embed, view=CloseButton())

        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            view = RealizujView(interaction.user, self.items)
            embed = discord.Embed(title="Nowy ticket", color=discord.Color.green())
            embed.add_field(name="Użytkownik", value=interaction.user.mention)
            embed.add_field(name="Zamówienie", value=", ".join(self.items))
            embed.add_field(name="Kanał", value=ticket.mention)
            await log_channel.send(embed=embed, view=view)

        await interaction.response.send_message(f"Twój ticket został utworzony: {ticket.mention}", ephemeral=True)

@bot.event
async def on_ready():
    print(f"Bot zalogowany jako {bot.user}!")

@bot.command()
@commands.has_permissions(administrator=True)
async def startverify(ctx):
    view = WeryfikacjaButton()
    await ctx.send("Kliknij, aby się zweryfikować:", view=view)

@bot.command()
@commands.has_permissions(administrator=True)
async def startticket(ctx):
    view = BuySellView()
    await ctx.send("Wybierz czy chcesz kupić lub sprzedać:", view=view)

bot.run("TWÓJ_TOKEN_TUTAJ")
