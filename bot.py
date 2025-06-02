import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

GUILD_ID = 1373253103176122399
ROLE_ID = 1373275307150278686
VERIFY_CHANNEL_ID = 1373258480382771270
TICKET_CHANNEL_ID = 1373305137228939416
TICKET_CATEGORY_ID = 1373277957446959135
LOG_CHANNEL_ID = 1374479815914291240
ADMIN_ROLE_ID = 1373275898375176232

SERVER_OPTIONS = {
    "𝐂𝐑𝐀𝐅𝐓𝐏𝐋𝐀𝐘": {
        "𝐆𝐈𝐋𝐃𝐈𝐄": ["Elytra", "Buty flasha", "Miecz 6", "Kasa", "Shulker s2", "Shulker totemów"],
        "𝐁𝐎𝐗𝐏𝐕𝐏": ["Set 25", "Miecz 25", "Kilof 25", "Kasa"]
    },
    "𝐀𝐍𝐀𝐑𝐂𝐇𝐈𝐀": {
        "𝐋𝐈𝐅𝐄𝐒𝐓𝐄𝐀𝐋": ["Kasa", "Anarchiczny set 2", "Anarchiczny set 1", "Anarchiczny miecz", "Zajęczy miecz", "Totem ułaskawienia", "Excalibur"],
        "𝐁𝐎𝐗𝐏𝐕𝐏": ["Kasa", "Excalibur", "Totem ułaskawienia", "Sakiewka"]
    },
    "𝐑𝐀𝐏𝐘": {
        "𝐋𝐈𝐅𝐄𝐒𝐓𝐄𝐀𝐋": ["nie dostępne", "nie dostępne", "nie dostępne"],
        "𝐁𝐎𝐗𝐏𝐕𝐏": ["Kasa", "Miecz 35", "Set 35"]
    },
    "𝐏𝐘𝐊𝐌𝐂": {
        "𝐋𝐈𝐅𝐄𝐒𝐓𝐄𝐀𝐋": ["Kasa", "Buda", "Love swap", "Klata meduzy"],
        "𝐁𝐎𝐗𝐏𝐕𝐏": ["nie dostępne", "nie dostępne", "nie dostępne"]
    }
}

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

class CloseButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="❌ Zamknij ticket", style=discord.ButtonStyle.danger)
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if discord.utils.get(interaction.user.roles, id=ADMIN_ROLE_ID):
            await interaction.channel.delete(reason="Ticket zamknięty przez admina.")
        else:
            await interaction.response.send_message("❌ Tylko administrator może zamknąć ten ticket.", ephemeral=True)

class AmountModal(discord.ui.Modal, title="💵 Podaj kwotę"):
    amount = discord.ui.TextInput(label="Kwota", placeholder="Np. 50k$", required=True)

    def __init__(self, parent_view: 'PurchaseView', interaction: discord.Interaction):
        super().__init__()
        self.parent_view = parent_view
        self.interaction = interaction

    async def on_submit(self, interaction: discord.Interaction):
        self.parent_view.items.append(self.amount.value)
        await self.parent_view.finish(interaction)

class PurchaseView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.server = None
        self.mode = None
        self.items = []

        self.server_select = discord.ui.Select(placeholder="Wybierz serwer...", options=[
            discord.SelectOption(label=server) for server in SERVER_OPTIONS.keys()
        ])
        self.server_select.callback = self.server_selected
        self.add_item(self.server_select)

    async def server_selected(self, interaction: discord.Interaction):
        self.server = self.server_select.values[0]
        self.clear_items()
        self.mode_select = discord.ui.Select(placeholder="Wybierz tryb...", options=[
            discord.SelectOption(label=mode) for mode in SERVER_OPTIONS[self.server].keys()
        ])
        self.mode_select.callback = self.mode_selected
        self.add_item(self.mode_select)
        await interaction.response.edit_message(content=f"Serwer: `{self.server}`\nWybierz tryb:", view=self)

    async def mode_selected(self, interaction: discord.Interaction):
        self.mode = self.mode_select.values[0]
        self.clear_items()
        self.item_select = discord.ui.Select(placeholder="Wybierz itemy...", options=[
            discord.SelectOption(label=item) for item in SERVER_OPTIONS[self.server][self.mode]
        ], min_values=1, max_values=len(SERVER_OPTIONS[self.server][self.mode]))
        self.item_select.callback = self.item_selected
        self.add_item(self.item_select)
        await interaction.response.edit_message(content=f"Serwer: `{self.server}`\nTryb: `{self.mode}`\nWybierz itemy:", view=self)

    async def item_selected(self, interaction: discord.Interaction):
        selected = self.item_select.values
        if "Kasa" in selected:
            self.items.extend(i for i in selected if i != "Kasa")
            await interaction.response.send_modal(AmountModal(self, interaction))
        else:
            self.items.extend(selected)
            await self.finish(interaction)

    async def finish(self, interaction: discord.Interaction):
        self.clear_items()
        await interaction.response.edit_message(
            content=f"Serwer: `{self.server}`\nTryb: `{self.mode}`\nItemy: `{', '.join(self.items)}`\n\n✅ Dziękujemy za złożenie zamówienia!",
            view=CloseButton()
        )
        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(title="🛒 Nowe zamówienie w tickecie", color=discord.Color.gold())
            embed.add_field(name="Użytkownik", value=f"{interaction.user.mention} ({interaction.user.name})", inline=False)
            embed.add_field(name="Serwer", value=self.server, inline=True)
            embed.add_field(name="Tryb", value=self.mode, inline=True)
            embed.add_field(name="Itemy", value=", ".join(self.items), inline=False)
            embed.set_footer(text=f"Data: {interaction.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            await log_channel.send(embed=embed, view=OrderActionView(interaction.user, self.server, self.mode, self.items))

class OrderActionView(discord.ui.View):
    def __init__(self, user, server, mode, items):
        super().__init__(timeout=None)
        self.user = user
        self.server = server
        self.mode = mode
        self.items = items

    @discord.ui.button(label="✅ Zrealizuj", style=discord.ButtonStyle.success, custom_id="order_complete")
    async def complete_order(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not discord.utils.get(interaction.user.roles, id=ADMIN_ROLE_ID):
            await interaction.response.send_message("❌ Tylko administrator może wykonać tę akcję.", ephemeral=True)
            return
        await interaction.response.edit_message(content="✅ Zamówienie zostało zrealizowane.", view=None)
        ocen_channel = interaction.guild.get_channel(1375528888586731762)
        if ocen_channel:
            embed = discord.Embed(title="⭐ Nowa ocena zamówienia", color=discord.Color.green())
            embed.add_field(name="Użytkownik", value=f"{self.user.mention} ({self.user.name})", inline=False)
            embed.add_field(name="Serwer", value=self.server, inline=True)
            embed.add_field(name="Tryb", value=self.mode, inline=True)
            embed.add_field(name="Itemy", value=", ".join(self.items), inline=False)
            embed.set_footer(text=f"Data: {interaction.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            await ocen_channel.send(embed=embed)

    @discord.ui.button(label="❌ Odrzuć", style=discord.ButtonStyle.danger, custom_id="order_reject")
    async def reject_order(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not discord.utils.get(interaction.user.roles, id=ADMIN_ROLE_ID):
            await interaction.response.send_message("❌ Tylko administrator może wykonać tę akcję.", ephemeral=True)
            return
        await interaction.response.edit_message(content="❌ Zamówienie zostało odrzucone.", view=None)

class TicketButton(discord.ui.View):
    @discord.ui.button(label="🎫 Utwórz ticket", style=discord.ButtonStyle.primary, custom_id="create_ticket")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        existing = discord.utils.get(guild.channels, name=f"ticket-{interaction.user.id}")
        if existing:
            await interaction.response.send_message("Masz już otwarty ticket!", ephemeral=True)
            return
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.get_role(ADMIN_ROLE_ID): discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        channel = await guild.create_text_channel(f"ticket-{interaction.user.id}", overwrites=overwrites, category=guild.get_channel(TICKET_CATEGORY_ID))
        await channel.send(f"{interaction.user.mention}, witaj w swoim tickecie! Napisz, w czym możemy pomóc.", view=PurchaseView())
        await interaction.response.send_message(f"Ticket został utworzony: {channel.mention}", ephemeral=True)

@bot.event
async def on_ready():
    print(f"Bot zalogowany jako {bot.user}")
    bot.add_view(WeryfikacjaButton())
    bot.add_view(TicketButton())
    bot.add_view(CloseButton())
    bot.add_view(OrderActionView(None, None, None, None))  # Dodane, żeby widok się zarejestrował

# Komenda do wysłania panelu weryfikacji - możesz ją wywołać manualnie
@bot.command()
@commands.has_permissions(administrator=True)
async def send_verify(ctx):
    channel = bot.get_channel(VERIFY_CHANNEL_ID)
    if channel:
        await channel.send("Kliknij przycisk aby się zweryfikować:", view=WeryfikacjaButton())

# Komenda do wysłania panelu ticketów
@bot.command()
@commands.has_permissions(administrator=True)
async def send_ticket_panel(ctx):
    channel = bot.get_channel(TICKET_CHANNEL_ID)
    if channel:
        await channel.send("Kliknij przycisk aby utworzyć ticket:", view=TicketButton())

TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
