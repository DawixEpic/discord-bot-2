import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.members = True
intents.message_content = True  # Dodane, bo pojawiło się ostrzeżenie o braku

bot = commands.Bot(command_prefix="!", intents=intents)

# 🔧 KONFIGURACJA
GUILD_ID = 1373253103176122399
ROLE_ID = 1373275307150278686
VERIFY_CHANNEL_ID = 1373258480382771270
TICKET_CHANNEL_ID = 1373305137228939416
TICKET_CATEGORY_ID = 1373277957446959135
LOG_CHANNEL_ID = 1374479815914291240

ADMIN_ROLE_ID = 1373275898375176232  # ← Zmień na prawidłowe ID roli admina
REALIZED_ROLE_ID = 1374099985288921088  # ← Podmień na ID roli przyznawanej po realizacji

SERVER_OPTIONS = {
    "𝐂𝐑𝐀𝐅𝐓𝐏𝐋𝐀𝐘": {
        "𝐆𝐈𝐋𝐃𝐈𝐄": [" Elytra", "Buty flasha", "Miecz 6", "1k$", "Shulker s2", "Shulker totemów"],
        "𝐁𝐎𝐗𝐏𝐕𝐏": ["Set 25", "Miecz 25", " Kilof 25", "1mln$"]
    },
    "𝐀𝐍𝐀𝐑𝐂𝐇𝐈𝐀": {
        "𝐋𝐈𝐅𝐄𝐒𝐓𝐄𝐀𝐋": ["4,5k$", "50k$", "550k$", "Anarchiczny set 2", "Anarchiczny set 1", "Anarchiczny miecz", "Zajęczy miecz", "Totem ułaskawienia", "Excalibur"],
        "𝐁𝐎𝐗𝐏𝐕𝐏": ["50k$", "1mln$", "Excalibur", "Totem ułaskawienia", "Sakiewka"]
    },
    "𝐑𝐀𝐏𝐘": {
        "𝐋𝐈𝐅𝐄𝐒𝐓𝐄𝐀𝐋": ["nie dostępne", "nie dostępne", "nie dostępne"],
        "𝐁𝐎𝐗𝐏𝐕𝐏": ["10mld$", "Miecz 35", "Set 35"]
    },
    "𝐏𝐘𝐊𝐌𝐂": {
        "𝐋𝐈𝐅𝐄𝐒𝐓𝐄𝐀𝐋": ["15k$", "Buda", "Love swap", "Klata meduzy"],
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
                await interaction.response.send_message("✅ Zostałeś zweryfikowany! Rola została nadana.", ephemeral=True)
            except discord.Forbidden:
                await interaction.response.send_message("❌ Nie mam uprawnień, aby nadać Ci rolę.", ephemeral=True)

class CloseButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="❌ Zamknij ticket", style=discord.ButtonStyle.danger)
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        admin_role = interaction.guild.get_role(ADMIN_ROLE_ID)
        if admin_role in interaction.user.roles:
            await interaction.channel.delete(reason="Ticket zamknięty przez admina.")
        else:
            await interaction.response.send_message("❌ Tylko administrator może zamknąć ten ticket.", ephemeral=True)

class RealizeOrderButton(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=None)
        self.user_id = user_id

    @discord.ui.button(label="✅ Zrealizowane", style=discord.ButtonStyle.success)
    async def realize(self, interaction: discord.Interaction, button: discord.ui.Button):
        admin_role = interaction.guild.get_role(ADMIN_ROLE_ID)
        if admin_role not in interaction.user.roles:
            await interaction.response.send_message("❌ Tylko administrator może oznaczyć zamówienie jako zrealizowane.", ephemeral=True)
            return
        
        user = interaction.guild.get_member(self.user_id)
        if not user:
            await interaction.response.send_message("❌ Nie znaleziono użytkownika.", ephemeral=True)
            return
        
        role = interaction.guild.get_role(REALIZED_ROLE_ID)
        if role not in user.roles:
            try:
                await user.add_roles(role)
            except discord.Forbidden:
                await interaction.response.send_message("❌ Nie mam uprawnień, aby nadać rolę.", ephemeral=True)
                return
        
        button.disabled = True
        button.label = "Zrealizowane ✅"
        await interaction.message.edit(view=self)

        await interaction.response.send_message(f"✅ Zamówienie oznaczone jako zrealizowane. Rola {role.name} nadana użytkownikowi {user.mention}.", ephemeral=True)

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
        self.items = self.item_select.values
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
            
            await log_channel.send(embed=embed, view=RealizeOrderButton(interaction.user.id))

class TicketButton(discord.ui.View):
    @discord.ui.button(label="🎫 Utwórz ticket", style=discord.ButtonStyle.primary, custom_id="create_ticket")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        existing = discord.utils.get(guild.text_channels, name=f"ticket-{interaction.user.name.lower().replace(' ', '-')}")
        if existing:
            await interaction.response.send_message("🛑 Masz już otwarty ticket!", ephemeral=True)
            return

        category = guild.get_channel(TICKET_CATEGORY_ID)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True)
        }

        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            overwrites=overwrites,
            category=category,
            reason="Nowy ticket"
        )

        await ticket_channel.send(f"{interaction.user.mention} 🎫 Ticket został utworzony. Wybierz przedmioty z interesującego Cię serwera Minecraft:", view=PurchaseView())
        await interaction.response.send_message("✅ Ticket utworzony!", ephemeral=True)

@bot.event
async def on_ready():
    print(f"✅ Zalogowano jako {bot.user}")
    print(f"Token starts with: {os.getenv('TOKEN')[:5]}")  # debug token
    guild = bot.get_guild(GUILD_ID)

    # Czyszczenie i wysyłanie wiadomości weryfikacyjnej
    verify_channel = guild.get_channel(VERIFY_CHANNEL_ID)
    if verify_channel:
        async for msg in verify_channel.history(limit=100):
            if msg.author == bot.user:
                await msg.delete()
        embed = discord.Embed(
            title="🔒 Weryfikacja dostępu",
            description="Kliknij przycisk poniżej, aby się zweryfikować i uzyskać dostęp do systemu ticketów.",
            color=discord.Color.blue()
        )
        await verify_channel.send(embed=embed, view=WeryfikacjaButton())

    # Czyszczenie i wysyłanie wiadomości ticketowej
    ticket_channel = guild.get_channel(TICKET_CHANNEL_ID)
    if ticket_channel:
        async for msg in ticket_channel.history(limit=100):
            if msg.author == bot.user:
                await msg.delete()
        embed = discord.Embed(
            title="🎫 System ticketów",
            description="Kliknij przycisk poniżej, aby utworzyć ticket i złożyć zamówienie.",
            color=discord.Color.green()
        )
        await ticket_channel.send(embed=embed, view=TicketButton())

print("Uruchamiam bota...")  # debug start

bot.run(os.getenv("TOKEN"))

print("Bot został zatrzymany")  # debug stop
