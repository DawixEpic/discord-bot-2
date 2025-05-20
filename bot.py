import discord
from discord.ext import commands
from discord.ui import View, Select, Button
import os

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# 🔧 Twoje ID
ROLE_ID = 1373275307150278686
TICKET_CATEGORY_ID = 1373277957446959135

verification_message_id = None
ticket_message_id = None

# 🔧 Serwery, tryby i itemy (edytuj jak chcesz)
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
        "𝐋𝐈𝐅𝐄𝐒𝐓𝐄𝐀𝐋": ["Budda", "Love swap", "Klata meduzy"],
        "𝐁𝐎𝐗𝐏𝐕𝐏": ["nie dostępne", "nie dostępne", "nie dostępne"]
    }
}

@bot.event
async def on_ready():
    print(f"✅ Zalogowano jako {bot.user}")

@bot.command()
@commands.has_permissions(administrator=True)
async def weryfikacja(ctx):
    embed = discord.Embed(title="✅ Weryfikacja",
                          description="Kliknij ✅ aby się zweryfikować i dostać dostęp.",
                          color=discord.Color.green())
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("✅")
    global verification_message_id
    verification_message_id = msg.id
    await ctx.send("✅ Wiadomość weryfikacyjna została wysłana.")

@bot.command()
@commands.has_permissions(administrator=True)
async def ticket(ctx):
    embed = discord.Embed(title="🎟️ Napisz co chcesz kupić",
                          description="Kliknij 🎟️ aby otworzyć prywatny ticket z wyborem opcji.",
                          color=discord.Color.blue())
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("🎟️")
    global ticket_message_id
    ticket_message_id = msg.id
    await ctx.send("✅ Wiadomość ticket została wysłana.")

@bot.event
async def on_raw_reaction_add(payload):
    if payload.member is None or payload.member.bot:
        return

    guild = bot.get_guild(payload.guild_id)

    # ✅ WERYFIKACJA
    if payload.message_id == verification_message_id and str(payload.emoji) == "✅":
        role = guild.get_role(ROLE_ID)
        if role:
            await payload.member.add_roles(role)
            channel = guild.get_channel(payload.channel_id)
            await channel.send(f"{payload.member.mention}, zostałeś zweryfikowany!", delete_after=5)

    # 🎟️ TICKET
    elif payload.message_id == ticket_message_id and str(payload.emoji) == "🎟️":
        category = guild.get_channel(TICKET_CATEGORY_ID)
        if not isinstance(category, discord.CategoryChannel):
            return

        channel_name = f"ticket-{payload.member.name}".lower()
        existing = discord.utils.get(guild.channels, name=channel_name)
        if existing:
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            payload.member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        ticket_channel = await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)
        await ticket_channel.send(f"{payload.member.mention}, wybierz z poniższego menu co chcesz kupić:")

        await send_menu(ticket_channel, payload.member)

# 🧠 Funkcja do wysyłania menu
async def send_menu(channel, member):
    view = MenuView(member)
    embed = discord.Embed(
        title="🛒 Wybierz co chcesz kupić",
        description="Wybierz serwer, tryb i itemy, które chcesz kupić.",
        color=discord.Color.gold()
    )
    await channel.send(embed=embed, view=view)

# 📦 Klasa menu wyboru
class MenuView(View):
    def __init__(self, member):
        super().__init__(timeout=None)
        self.member = member
        self.server = None
        self.mode = None

        self.select_server = Select(
            placeholder="🌍 Wybierz serwer",
            options=[discord.SelectOption(label=server) for server in SERVER_OPTIONS.keys()]
        )
        self.select_server.callback = self.server_chosen
        self.add_item(self.select_server)

    async def server_chosen(self, interaction: discord.Interaction):
        self.server = self.select_server.values[0]
        self.clear_items()

        self.select_mode = Select(
            placeholder="🎮 Wybierz tryb",
            options=[discord.SelectOption(label=mode) for mode in SERVER_OPTIONS[self.server].keys()]
        )
        self.select_mode.callback = self.mode_chosen
        self.add_item(self.select_mode)

        await interaction.response.edit_message(view=self)

    async def mode_chosen(self, interaction: discord.Interaction):
        self.mode = self.select_mode.values[0]
        self.clear_items()

        self.select_items = Select(
            placeholder="📦 Wybierz itemy",
            options=[
                discord.SelectOption(label=item) for item in SERVER_OPTIONS[self.server][self.mode]
            ],
            min_values=1,
            max_values=len(SERVER_OPTIONS[self.server][self.mode])
        )
        self.select_items.callback = self.items_chosen
        self.add_item(self.select_items)

        await interaction.response.edit_message(view=self)

    async def items_chosen(self, interaction: discord.Interaction):
        chosen_items = ", ".join(self.select_items.values)
        summary = (
            f"📄 Wybrałeś:\n"
            f"**Serwer:** {self.server}\n"
            f"**Tryb:** {self.mode}\n"
            f"**Itemy:** {chosen_items}"
        )
        embed = discord.Embed(title="✅ Wybór zapisany", description=summary, color=discord.Color.green())
        await interaction.response.edit_message(embed=embed, view=None)

bot.run(os.getenv("DISCORD_TOKEN"))
