import discord
from discord.ext import commands
from discord.ui import View, Button, Select, SelectOption
from datetime import datetime
import os

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# IDs do zmiany na Twoje
ROLE_ID = 1373275307150278686
TICKET_CATEGORY_ID = 1373277957446959135
LOG_CHANNEL_ID = 1374479815914291240
EVAL_CHANNEL_ID = 1375528888586731762  # Kanał na oceny (jeśli chcesz potem dodawać)

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

# --- WERYFIKACJA ---

class VerifyView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Zweryfikuj się", style=discord.ButtonStyle.success, custom_id="verify_button")
    async def verify_button(self, button: Button, interaction: discord.Interaction):
        role = interaction.guild.get_role(ROLE_ID)
        if not role:
            await interaction.response.send_message("Nie znaleziono roli do weryfikacji.", ephemeral=True)
            return
        if role in interaction.user.roles:
            await interaction.response.send_message("Jesteś już zweryfikowany!", ephemeral=True)
            return
        await interaction.user.add_roles(role)
        await interaction.response.send_message("Zostałeś zweryfikowany!", ephemeral=True)

# --- TICKET OPEN ---

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Otwórz ticket", style=discord.ButtonStyle.primary, custom_id="open_ticket_button")
    async def open_ticket(self, button: Button, interaction: discord.Interaction):
        guild = interaction.guild
        category = guild.get_channel(TICKET_CATEGORY_ID)
        if category is None or not isinstance(category, discord.CategoryChannel):
            await interaction.response.send_message("Nie znaleziono kategorii ticketów.", ephemeral=True)
            return

        existing = discord.utils.get(guild.text_channels, name=f"ticket-{interaction.user.name.lower()}")
        if existing:
            await interaction.response.send_message(f"Masz już otwarty ticket: {existing.mention}", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        channel = await guild.create_text_channel(f"ticket-{interaction.user.name}".lower(), category=category, overwrites=overwrites)

        # Wyślij pierwsze menu wyboru serwera do ticketu
        await channel.send(f"{interaction.user.mention}, wybierz serwer z menu poniżej:", view=ServerSelectView(interaction.user))

        await interaction.response.send_message(f"Ticket został utworzony: {channel.mention}", ephemeral=True)

# --- SELECTY ---

class ServerSelect(Select):
    def __init__(self, user):
        options = [SelectOption(label=server) for server in SERVER_OPTIONS.keys()]
        super().__init__(placeholder="Wybierz serwer", min_values=1, max_values=1, options=options)
        self.user = user

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.user:
            await interaction.response.send_message("To nie jest Twój ticket.", ephemeral=True)
            return
        server = self.values[0]
        # Przechodzimy do wyboru trybu
        await interaction.response.edit_message(content=f"{interaction.user.mention}, wybrałeś serwer: **{server}**. Teraz wybierz tryb:", view=ModeSelectView(self.user, server))

class ModeSelect(Select):
    def __init__(self, user, server):
        options = [SelectOption(label=mode) for mode in SERVER_OPTIONS[server].keys()]
        super().__init__(placeholder="Wybierz tryb", min_values=1, max_values=1, options=options)
        self.user = user
        self.server = server

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.user:
            await interaction.response.send_message("To nie jest Twój ticket.", ephemeral=True)
            return
        mode = self.values[0]
        # Przechodzimy do wyboru itemów
        await interaction.response.edit_message(content=f"{interaction.user.mention}, wybrałeś tryb: **{mode}**. Teraz wybierz itemy:", view=ItemSelectView(self.user, self.server, mode))

class ItemSelect(Select):
    def __init__(self, user, server, mode):
        options = [SelectOption(label=item) for item in SERVER_OPTIONS[server][mode]]
        # max_values ustaw na dowolną liczbę (możesz zmienić na max 1, jeśli chcesz 1 item)
        super().__init__(placeholder="Wybierz itemy (możesz wybrać więcej niż 1)", min_values=1, max_values=len(options), options=options)
        self.user = user
        self.server = server
        self.mode = mode

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.user:
            await interaction.response.send_message("To nie jest Twój ticket.", ephemeral=True)
            return
        items = self.values
        # Podsumowanie wyboru
        summary = (f"{interaction.user.mention} wybrał:\n"
                   f"**Serwer:** {self.server}\n"
                   f"**Tryb:** {self.mode}\n"
                   f"**Itemy:** {', '.join(items)}")
        
        await interaction.response.edit_message(content=summary, view=None)

        # Wyślij embed do kanału logów
        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(title="Nowy ticket - wybór użytkownika",
                                  description=summary,
                                  color=discord.Color.blue(),
                                  timestamp=datetime.utcnow())
            embed.set_footer(text=f"ID użytkownika: {interaction.user.id}")
            await log_channel.send(embed=embed)

class ServerSelectView(View):
    def __init__(self, user):
        super().__init__(timeout=None)
        self.add_item(ServerSelect(user))

class ModeSelectView(View):
    def __init__(self, user, server):
        super().__init__(timeout=None)
        self.add_item(ModeSelect(user, server))

class ItemSelectView(View):
    def __init__(self, user, server, mode):
        super().__init__(timeout=None)
        self.add_item(ItemSelect(user, server, mode))

# --- KOMENDY ---

@bot.command()
async def weryfikacja(ctx):
    embed = discord.Embed(
        title="Weryfikacja",
        description="Kliknij przycisk, aby się zweryfikować i uzyskać dostęp do serwera.",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed, view=VerifyView())

@bot.command()
async def ticket(ctx):
    embed = discord.Embed(
        title="System Ticketów",
        description="Kliknij przycisk, aby otworzyć ticket.",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed, view=TicketView())

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)

# --- START BOTA ---

if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_TOKEN") or "TWÓJ_TOKEN_TUTAJ"
    bot.run(TOKEN)
