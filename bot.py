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

    def __init__(self, parent_view: 'PurchaseView'):
        super().__init__()
        self.parent_view = parent_view

    async def on_submit(self, interaction: discord.Interaction):
        self.parent_view.items.append(self.amount.value)
        await self.parent_view.finish(interaction)

class SellModal(discord.ui.Modal, title="📝 Co chcesz sprzedać?"):
    description_input = discord.ui.TextInput(label="Opis", placeholder="Np. Diamentowy miecz +5", required=True, style=discord.TextStyle.paragraph)

    def __init__(self, parent_view: 'SellView'):
        super().__init__()
        self.parent_view = parent_view

    async def on_submit(self, interaction: discord.Interaction):
        self.parent_view.description = self.description_input.value
        await self.parent_view.finish(interaction)

class PurchaseView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.server = None
        self.mode = None
        self.items = []

        self.server_select = discord.ui.Select(
            placeholder="Wybierz serwer...",
            options=[discord.SelectOption(label=server) for server in SERVER_OPTIONS.keys()]
        )
        self.server_select.callback = self.server_selected
        self.add_item(self.server_select)

    async def server_selected(self, interaction: discord.Interaction):
        self.server = self.server_select.values[0]
        self.clear_items()

        modes = SERVER_OPTIONS[self.server].keys()
        self.mode_select = discord.ui.Select(
            placeholder="Wybierz tryb...",
            options=[discord.SelectOption(label=mode) for mode in modes]
        )
        self.mode_select.callback = self.mode_selected
        self.add_item(self.mode_select)

        await interaction.response.edit_message(content=f"Serwer: `{self.server}`\nWybierz tryb:", view=self)

    async def mode_selected(self, interaction: discord.Interaction):
        self.mode = self.mode_select.values[0]
        self.clear_items()

        items = SERVER_OPTIONS[self.server][self.mode]
        self.item_select = discord.ui.Select(
            placeholder="Wybierz itemy...",
            options=[discord.SelectOption(label=item) for item in items],
            min_values=1,
            max_values=len(items)
        )
        self.item_select.callback = self.item_selected
        self.add_item(self.item_select)

        await interaction.response.edit_message(content=f"Serwer: `{self.server}`\nTryb: `{self.mode}`\nWybierz itemy:", view=self)

    async def item_selected(self, interaction: discord.Interaction):
        selected = self.item_select.values
        if "💰 Kasa" in selected:
            self.items.extend(i for i in selected if i != "💰 Kasa")
            await interaction.response.send_modal(AmountModal(self))
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
            embed.add_field(name="Użytkownik", value=f"{interaction.user.mention} ({interaction.user})", inline=False)
            embed.add_field(name="Serwer", value=self.server, inline=True)
            embed.add_field(name="Tryb", value=self.mode, inline=True)
            embed.add_field(name="Itemy", value=", ".join(self.items), inline=False)
            embed.set_footer(text=f"Data: {interaction.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            await log_channel.send(embed=embed)

class SellView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.server = None
        self.mode = None
        self.description = None

        self.server_select = discord.ui.Select(
            placeholder="Wybierz serwer...",
            options=[discord.SelectOption(label=server) for server in SERVER_OPTIONS.keys()]
        )
        self.server_select.callback = self.server_selected
        self.add_item(self.server_select)

    async def server_selected(self, interaction: discord.Interaction):
        self.server = self.server_select.values[0]
        self.clear_items()

        modes = SERVER_OPTIONS[self.server].keys()
        self.mode_select = discord.ui.Select(
            placeholder="Wybierz tryb...",
            options=[discord.SelectOption(label=mode) for mode in modes]
        )
        self.mode_select.callback = self.mode_selected
        self.add_item(self.mode_select)

        await interaction.response.edit_message(content=f"Serwer: `{self.server}`\nWybierz tryb:", view=self)

    async def mode_selected(self, interaction: discord.Interaction):
        self.mode = self.mode_select.values[0]
        self.clear_items()

        await interaction.response.send_modal(SellModal(self))

    async def finish(self, interaction: discord.Interaction):
        self.clear_items()
        await interaction.response.edit_message(
            content=f"Serwer: `{self.server}`\nTryb: `{self.mode}`\nSprzedaż: `{self.description}`\n\n✅ Dziękujemy za zgłoszenie!",
            view=CloseButton()
        )
        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(title="📢 Nowa oferta sprzedaży w tickecie", color=discord.Color.blue())
            embed.add_field(name="Użytkownik", value=f"{interaction.user.mention} ({interaction.user})", inline=False)
            embed.add_field(name="Serwer", value=self.server, inline=True)
            embed.add_field(name="Tryb", value=self.mode, inline=True)
            embed.add_field(name="Opis", value=self.description, inline=False)
            embed.set_footer(text=f"Data: {interaction.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            await log_channel.send(embed=embed)

class MainMenuView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(label="Zweryfikuj się ✅", style=discord.ButtonStyle.success, custom_id="verify_button"))

        self.main_select = discord.ui.Select(
            placeholder="Co chcesz zrobić?",
            options=[
                discord.SelectOption(label="Kup", description="Złóż zamówienie na zakup", emoji="🛒"),
                discord.SelectOption(label="Sprzedaj", description="Dodaj ofertę sprzedaży", emoji="📢")
            ]
        )
        self.main_select.callback = self.main_selected
        self.add_item(self.main_select)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # tylko na odpowiednim serwerze
        return interaction.guild and interaction.guild.id == GUILD_ID

    async def main_selected(self, interaction: discord.Interaction):
        choice = self.main_select.values[0]
        if choice == "Kup":
            await interaction.response.edit_message(content="Wybierz serwer, tryb i itemy do zakupu:", view=PurchaseView())
        elif choice == "Sprzedaj":
            await interaction.response.edit_message(content="Wybierz serwer i tryb do sprzedaży:", view=SellView())

@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user}!")

@bot.command()
@commands.has_permissions(administrator=True)
async def send_verify(ctx):
    if ctx.channel.id != VERIFY_CHANNEL_ID:
        await ctx.send(f"Ta komenda może być użyta tylko na kanale weryfikacji <#{VERIFY_CHANNEL_ID}>")
        return
    view = MainMenuView()
    await ctx.send("Kliknij przycisk, aby się zweryfikować i/lub wybierz co chcesz zrobić:", view=view)

@bot.event
async def on_interaction(interaction: discord.Interaction):
    # obsługa przycisku weryfikacji
    if interaction.type == discord.InteractionType.component and interaction.data.get("custom_id") == "verify_button":
        role = interaction.guild.get_role(ROLE_ID)
        if role in interaction.user.roles:
            await interaction.response.send_message("🔔 Już masz tę rolę!", ephemeral=True)
        else:
            try:
                await interaction.user.add_roles(role)
                await interaction.response.send_message("✅ Zostałeś zweryfikowany!", ephemeral=True)
            except discord.Forbidden:
                await interaction.response.send_message("❌ Nie mam uprawnień, aby nadać Ci rolę.", ephemeral=True)

bot.run(os.getenv("DISCORD_TOKEN"))
