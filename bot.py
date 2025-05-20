import discord
from discord.ext import commands
from discord.ui import View, Select, Button
import asyncio
import os
import datetime

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

ROLE_ID = 1373275307150278686
TICKET_CATEGORY_ID = 1373277957446959135
LOG_CHANNEL_ID = 1374479815914291240  # <-- Wstaw tutaj ID swojego kanału logów

verification_message_id = None
ticket_message_id = None

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

    if payload.message_id == verification_message_id and str(payload.emoji) == "✅":
        role = guild.get_role(ROLE_ID)
        if role:
            await payload.member.add_roles(role)
            channel = guild.get_channel(payload.channel_id)
            await channel.send(f"{payload.member.mention}, zostałeś zweryfikowany!", delete_after=5)

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
        await ticket_channel.send(f"{payload.member.mention}, wybierz co chcesz kupić:", view=MenuView(payload.member, ticket_channel))

        # Automatyczne zamykanie po 1h
        await asyncio.sleep(3600)
        if ticket_channel:
            await ticket_channel.send("⏰ Ticket został automatycznie zamknięty.")
            await ticket_channel.delete()

class MenuView(View):
    def __init__(self, member, channel):
        super().__init__(timeout=None)
        self.member = member
        self.channel = channel
        self.server = None
        self.mode = None

        self.add_item(ServerSelect(self))
        self.add_item(CloseButton(channel))

class ServerSelect(Select):
    def __init__(self, menu_view):
        self.menu_view = menu_view
        options = [discord.SelectOption(label=server) for server in SERVER_OPTIONS]
        super().__init__(placeholder="🌍 Wybierz serwer", options=options)

    async def callback(self, interaction: discord.Interaction):
        self.menu_view.server = self.values[0]
        self.menu_view.clear_items()
        self.menu_view.add_item(ModeSelect(self.menu_view))
        self.menu_view.add_item(CloseButton(self.menu_view.channel))
        await interaction.response.edit_message(view=self.menu_view)

class ModeSelect(Select):
    def __init__(self, menu_view):
        self.menu_view = menu_view
        modes = SERVER_OPTIONS[menu_view.server].keys()
        options = [discord.SelectOption(label=mode) for mode in modes]
        super().__init__(placeholder="🎮 Wybierz tryb", options=options)

    async def callback(self, interaction: discord.Interaction):
        self.menu_view.mode = self.values[0]
        self.menu_view.clear_items()
        self.menu_view.add_item(ItemSelect(self.menu_view))
        self.menu_view.add_item(CloseButton(self.menu_view.channel))
        await interaction.response.edit_message(view=self.menu_view)

class ItemSelect(Select):
    def __init__(self, menu_view):
        self.menu_view = menu_view
        items = SERVER_OPTIONS[menu_view.server][menu_view.mode]
        options = [discord.SelectOption(label=item) for item in items]
        super().__init__(placeholder="📦 Wybierz itemy", options=options, min_values=1, max_values=len(items))

    async def callback(self, interaction: discord.Interaction):
        chosen = ", ".join(self.values)
        embed = discord.Embed(
            title="✅ Wybrano",
            description=f"**Serwer:** {self.menu_view.server}\n**Tryb:** {self.menu_view.mode}\n**Itemy:** {chosen}",
            color=discord.Color.green()
        )
        await interaction.response.edit_message(embed=embed, view=CloseOnly(self.menu_view.channel))

        # Logowanie wyboru do kanału logów
        log_channel = interaction.client.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            await log_channel.send(
                f"📋 **Nowy wybór ticketu**\n"
                f"Użytkownik: {interaction.user} ({interaction.user.id})\n"
                f"Serwer: `{self.menu_view.server}`\n"
                f"Tryb: `{self.menu_view.mode}`\n"
                f"Itemy: `{chosen}`\n"
                f"Czas: `{now}`"
            )

class CloseButton(Button):
    def __init__(self, channel):
        super().__init__(label="🗑️ Zamknij ticket", style=discord.ButtonStyle.danger)
        self.channel = channel

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message("✅ Ticket zostanie zamknięty...", ephemeral=True)
        await self.channel.delete()

class CloseOnly(View):
    def __init__(self, channel):
        super().__init__(timeout=None)
        self.add_item(CloseButton(channel))

bot.run(os.getenv("DISCORD_TOKEN"))
