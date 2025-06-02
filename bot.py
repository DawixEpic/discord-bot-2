import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.members = True
intents.message_content = True  # na wypadek, gdybyś potrzebował treści wiadomości (np. w przyszłości)

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

class CloseButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="❌ Zamknij ticket", style=discord.ButtonStyle.danger)
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        # sprawdzenie roli admina
        if discord.utils.get(interaction.user.roles, id=ADMIN_ROLE_ID):
            await interaction.channel.delete(reason=f"Ticket zamknięty przez {interaction.user}")
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

async def create_ticket_channel(guild: discord.Guild, user: discord.Member, topic: str) -> discord.TextChannel:
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        guild.get_role(ADMIN_ROLE_ID): discord.PermissionOverwrite(read_messages=True, send_messages=True),
        # opcjonalnie bot może mieć pełne prawa w tickecie
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
    }
    category = guild.get_channel(TICKET_CATEGORY_ID)
    if category is None:
        raise ValueError("Kategoria ticketów nie istnieje!")

    channel_name = f"ticket-{user.name}".lower()
    # upewnij się, że nie ma kanału o tej nazwie
    existing = discord.utils.get(category.channels, name=channel_name)
    if existing:
        # jeśli jest, dodaj sufiks liczbowy
        i = 1
        while discord.utils.get(category.channels, name=f"{channel_name}-{i}"):
            i += 1
        channel_name = f"{channel_name}-{i}"

    channel = await category.create_text_channel(
        name=channel_name,
        overwrites=overwrites,
        topic=topic,
        reason=f"Ticket utworzony dla {user}"
    )
    return channel

class PurchaseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
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
        await interaction.response.edit_message(content="Tworzę ticket...", view=None)

        guild = interaction.guild
        user = interaction.user
        topic = f"Zakup - Serwer: {self.server}, Tryb: {self.mode}, Itemy: {', '.join(self.items)}"

        channel = await create_ticket_channel(guild, user, topic)

        embed = discord.Embed(
            title="🛒 Zamówienie",
            description=f"Serwer: `{self.server}`\nTryb: `{self.mode}`\nItemy: `{', '.join(self.items)}`",
            color=discord.Color.gold()
        )
        embed.set_footer(text=f"Użytkownik: {user} | ID: {user.id}")

        view = CloseButton()
        await channel.send(content=user.mention, embed=embed, view=view)

        # wiadomość potwierdzająca użytkownikowi
        await interaction.followup.send(f"✅ Ticket został utworzony: {channel.mention}", ephemeral=True)

        # log do kanału logów
        log_channel = guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed_log = discord.Embed(title="🛒 Nowe zamówienie", color=discord.Color.gold())
            embed_log.add_field(name="Użytkownik", value=f"{user.mention} ({user})", inline=False)
            embed_log.add_field(name="Serwer", value=self.server, inline=True)
            embed_log.add_field(name="Tryb", value=self.mode, inline=True)
            embed_log.add_field(name="Itemy", value=", ".join(self.items), inline=False)
            embed_log.set_footer(text=f"Data: {interaction.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            await log_channel.send(embed=embed_log)

class SellView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
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

        self.sell_button = discord.ui.Button(label="Podaj, co sprzedajesz", style=discord.ButtonStyle.primary)
        self.sell_button.callback = self.sell_button_clicked
        self.add_item(self.sell_button)

        await interaction.response.edit_message(content=f"Serwer: `{self.server}`\nTryb: `{self.mode}`\nKliknij poniżej i podaj, co chcesz sprzedać.", view=self)

    async def sell_button_clicked(self, interaction: discord.Interaction):
        await interaction.response.send_modal(SellModal(self))

    async def finish(self, interaction: discord.Interaction):
        self.clear_items()
        await interaction.response.edit_message(content="Tworzę ticket...", view=None)

        guild = interaction.guild
        user = interaction.user
        topic = f"Sprzedaż - Serwer: {self.server}, Tryb: {self.mode}, Opis: {self.description}"

        channel = await create_ticket_channel(guild, user, topic)

        embed = discord.Embed(
            title="📝 Oferta sprzedaży",
            description=f"Serwer: `{self.server}`\nTryb: `{self.mode}`\nCo sprzedajesz:\n{self.description}",
            color=discord.Color.red()
        )
        embed.set_footer(text=f"Użytkownik: {user} | ID: {user.id}")

        view = CloseButton()
        await channel.send(content=user.mention, embed=embed, view=view)

        # potwierdzenie dla użytkownika
        await interaction.followup.send(f"✅ Ticket został utworzony: {channel.mention}", ephemeral=True)

        # log do kanału logów
        log_channel = guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed_log = discord.Embed(title="📝 Nowa oferta sprzedaży", color=discord.Color.red())
            embed_log.add_field(name="Użytkownik", value=f"{user.mention} ({user})", inline=False)
            embed_log.add_field(name="Serwer", value=self.server, inline=True)
            embed_log.add_field(name="Tryb", value=self.mode, inline=True)
            embed_log.add_field(name="Opis", value=self.description, inline=False)
            embed_log.set_footer(text=f"Data: {interaction.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            await log_channel.send(embed=embed_log)

@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user}!")

@bot.command()
async def weryfikacja(ctx):
    if ctx.channel.id != VERIFY_CHANNEL_ID:
        return
    embed = discord.Embed(
        title="Weryfikacja",
        description="Kliknij przycisk, aby się zweryfikować i otrzymać dostęp do serwera.",
        color=discord.Color.blue()
    )
    view = discord.ui.View(timeout=None)

    async def verify_callback(interaction: discord.Interaction):
        role = interaction.guild.get_role(ROLE_ID)
        if role in interaction.user.roles:
            await interaction.response.send_message("Jesteś już zweryfikowany.", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("✅ Zweryfikowano! Otrzymałeś dostęp.", ephemeral=True)

    button = discord.ui.Button(label="Zweryfikuj się", style=discord.ButtonStyle.success)
    button.callback = verify_callback
    view.add_item(button)

    await ctx.send(embed=embed, view=view)

@bot.command()
async def ticket(ctx):
    if ctx.channel.id != TICKET_CHANNEL_ID:
        return
    embed = discord.Embed(
        title="System ticketów",
        description="Wybierz, czy chcesz kupić, czy sprzedać przedmiot.",
        color=discord.Color.green()
    )
    view = discord.ui.View(timeout=None)

    select = discord.ui.Select(
        placeholder="Wybierz opcję...",
        options=[
            discord.SelectOption(label="Kup", description="Kup przedmiot", emoji="🛒"),
            discord.SelectOption(label="Sprzedaj", description="Sprzedaj przedmiot", emoji="📝")
        ]
    )

    async def select_callback(interaction: discord.Interaction):
        if select.values[0] == "Kup":
            purchase_view = PurchaseView()
            await interaction.response.edit_message(content="Wybrałeś: Kup\nWybierz serwer:", view=purchase_view)
        else:
            sell_view = SellView()
            await interaction.response.edit_message(content="Wybrałeś: Sprzedaj\nWybierz serwer:", view=sell_view)

    select.callback = select_callback
    view.add_item(select)

    await ctx.send(embed=embed, view=view)

bot.run(os.getenv("TOKEN"))
