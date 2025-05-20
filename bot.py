import discord
from discord.ext import commands
from discord import ui
import os

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# 🔧 Ustawienia – podaj swoje ID
ROLE_ID = 1373275307150278686
TICKET_CATEGORY_ID = 1373277957446959135

verification_message_id = None
ticket_message_id = None

# 💡 Tu definiujesz serwery, tryby i itemy (łatwe do zmiany!)
server_data = {
    "Survival": {
        "Easy": ["Diament", "Zbroja", "Kilof"],
        "Hardcore": ["Netherite", "Złote Jabłko"]
    },
    "SkyBlock": {
        "Classic": ["Generator", "Fly", "VIP"],
        "PvP": ["Miecz", "Zbroja", "Elytra"]
    }
}

user_choices = {}  # user_id: {server, mode, items}

# ============ WERYFIKACJA ============
@bot.command()
@commands.has_permissions(administrator=True)
async def weryfikacja(ctx):
    embed = discord.Embed(title="✅ Weryfikacja", description="Kliknij ✅ aby się zweryfikować.", color=discord.Color.green())
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("✅")
    global verification_message_id
    verification_message_id = msg.id

# ============ TICKET (START) ============
@bot.command()
@commands.has_permissions(administrator=True)
async def ticket(ctx):
    embed = discord.Embed(title="🎟️ System Ticketów", description="Kliknij przycisk poniżej, aby rozpocząć zakup.", color=discord.Color.blue())
    view = ServerSelect()
    msg = await ctx.send(embed=embed, view=view)
    global ticket_message_id
    ticket_message_id = msg.id

# ============ MENU WYBORU ============
class ServerSelect(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        options = [discord.SelectOption(label=server, value=server) for server in server_data]
        self.add_item(ServerDropdown(options))

class ServerDropdown(ui.Select):
    def __init__(self, options):
        super().__init__(placeholder="Wybierz serwer", options=options)

    async def callback(self, interaction: discord.Interaction):
        user_choices[interaction.user.id] = {"server": self.values[0]}
        await interaction.response.edit_message(content="✅ Wybrałeś serwer: " + self.values[0], view=ModeSelect(self.values[0]))

class ModeSelect(ui.View):
    def __init__(self, server):
        super().__init__(timeout=None)
        options = [discord.SelectOption(label=mode, value=mode) for mode in server_data[server]]
        self.add_item(ModeDropdown(server, options))

class ModeDropdown(ui.Select):
    def __init__(self, server, options):
        self.server = server
        super().__init__(placeholder="Wybierz tryb", options=options)

    async def callback(self, interaction: discord.Interaction):
        user_choices[interaction.user.id]["mode"] = self.values[0]
        await interaction.response.edit_message(content="✅ Wybrałeś tryb: " + self.values[0], view=ItemSelect(self.server, self.values[0]))

class ItemSelect(ui.View):
    def __init__(self, server, mode):
        super().__init__(timeout=None)
        options = [discord.SelectOption(label=item, value=item) for item in server_data[server][mode]]
        self.add_item(ItemDropdown(options))

class ItemDropdown(ui.Select):
    def __init__(self, options):
        super().__init__(placeholder="Wybierz itemy", options=options, min_values=1, max_values=len(options))

    async def callback(self, interaction: discord.Interaction):
        user_choices[interaction.user.id]["items"] = self.values
        await interaction.response.send_message("✅ Wybór zakończony. Tworzę ticket...", ephemeral=True)

        guild = interaction.guild
        category = guild.get_channel(TICKET_CATEGORY_ID)

        channel_name = f"ticket-{interaction.user.name}".lower()
        existing = discord.utils.get(guild.channels, name=channel_name)
        if existing:
            await interaction.followup.send("❌ Masz już otwarty ticket!", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        channel = await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)
        data = user_choices[interaction.user.id]
        await channel.send(f"{interaction.user.mention} otworzył ticket!\n**Serwer:** {data['server']}\n**Tryb:** {data['mode']}\n**Itemy:** {', '.join(data['items'])}")

# ============ WERYFIKACJA EVENT ============
@bot.event
async def on_raw_reaction_add(payload):
    if payload.member is None or payload.member.bot:
        return

    guild = bot.get_guild(payload.guild_id)

    if payload.message_id == verification_message_id and str(payload.emoji) == "✅":
        role = guild.get_role(ROLE_ID)
        if role:
            await payload.member.add_roles(role)
            channel = guild.get_channel(payload.channel_id)
            await channel.send(f"{payload.member.mention}, zostałeś zweryfikowany!", delete_after=5)

bot.run(os.getenv("DISCORD_TOKEN"))
