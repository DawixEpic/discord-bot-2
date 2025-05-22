import discord
from discord.ext import commands
from discord.ui import View, Select, Button
from datetime import datetime

intents = discord.Intents.default()
intents.guilds = True
intents.guild_messages = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Konfiguracja (dostosuj do własnych potrzeb)
TICKET_CATEGORY_ID = 1373277957446959135  # ID kategorii, gdzie mają się pojawiać tickety
SUPPORT_ROLE_ID = 1373275898375176232    # ID roli supportu
LOG_CHANNEL_ID = 1374479815914291240      # ID kanału logów

SERVER_OPTIONS = {
    "Survival": {
        "Classic": ["Złoto", "Diamenty", "Netherite"],
        "Hardcore": ["Serce", "Miecz", "Zbroja"]
    },
    "SkyBlock": {
        "Solo": ["Generator", "Ziemia", "Spawner"],
        "Team": ["VIP", "Farmer", "Ekspander"]
    }
}

# Widok wyboru
class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ServerSelect())

class ServerSelect(Select):
    def __init__(self):
        options = [discord.SelectOption(label=server) for server in SERVER_OPTIONS]
        super().__init__(placeholder="Wybierz serwer...", options=options, custom_id="select_server")

    async def callback(self, interaction: discord.Interaction):
        server = self.values[0]
        await interaction.response.edit_message(view=ModeView(server))

class ModeView(View):
    def __init__(self, server):
        super().__init__(timeout=None)
        self.server = server
        modes = SERVER_OPTIONS[server]
        self.add_item(ModeSelect(server, modes))

class ModeSelect(Select):
    def __init__(self, server, modes):
        options = [discord.SelectOption(label=mode) for mode in modes]
        super().__init__(placeholder="Wybierz tryb...", options=options, custom_id="select_mode")
        self.server = server

    async def callback(self, interaction: discord.Interaction):
        mode = self.values[0]
        await interaction.response.edit_message(view=ItemView(self.server, mode))

class ItemView(View):
    def __init__(self, server, mode):
        super().__init__(timeout=None)
        self.server = server
        self.mode = mode
        items = SERVER_OPTIONS[server][mode]
        self.add_item(ItemSelect(server, mode, items))

class ItemSelect(Select):
    def __init__(self, server, mode, items):
        options = [discord.SelectOption(label=item) for item in items]
        super().__init__(placeholder="Wybierz item...", options=options, custom_id="select_item")
        self.server = server
        self.mode = mode

    async def callback(self, interaction: discord.Interaction):
        item = self.values[0]
        await create_ticket(interaction, self.server, self.mode, item)

async def create_ticket(interaction: discord.Interaction, server, mode, item):
    guild = interaction.guild
    category = guild.get_channel(TICKET_CATEGORY_ID)
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        guild.get_role(SUPPORT_ROLE_ID): discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }
    channel = await guild.create_text_channel(
        name=f"ticket-{interaction.user.name}".lower(),
        category=category,
        overwrites=overwrites
    )

    # Wiadomość w tickecie
    await channel.send(
        content=f"{interaction.user.mention}, twój ticket został utworzony.\n"
                f"**Serwer:** {server}\n**Tryb:** {mode}\n**Item:** {item}"
    )

    # Logi
    log_channel = guild.get_channel(LOG_CHANNEL_ID)
    embed = discord.Embed(
        title="📥 Nowy ticket",
        description=f"**Użytkownik:** {interaction.user.mention}\n"
                    f"**Serwer:** {server}\n**Tryb:** {mode}\n**Item:** {item}\n"
                    f"**Kanał:** {channel.mention}",
        color=discord.Color.green(),
        timestamp=datetime.utcnow()
    )
    await log_channel.send(embed=embed)

    await interaction.response.send_message(
        content=f"✅ Ticket utworzony: {channel.mention}",
        ephemeral=True
    )

@bot.command()
async def test(ctx):
    await ctx.send("Kliknij, aby utworzyć ticket:", view=TicketView())

# Rejestracja widoków persistent
@bot.event
async def on_ready():
    bot.add_view(TicketView())
    print(f"Bot zalogowany jako {bot.user}")

bot.run("YOUR_TOKEN")
