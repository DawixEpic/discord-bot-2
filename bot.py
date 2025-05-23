import discord
from discord.ext import commands
from discord.ui import View, Select, Button
import asyncio
import os
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

ROLE_ID = 1373275307150278686
TICKET_CATEGORY_ID = 1373277957446959135
LOG_CHANNEL_ID = 1374479815914291240
TICKET_CHANNEL_ID = 1373305137228939416
ADMIN_PANEL_CHANNEL_ID = 1374781085895884820

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
        "𝐋𝐈𝐅𝐄𝐒𝐓𝐄𝐀𝐋": ["Buddha", "Love swap", "Klata meduzy"],
        "𝐁𝐎𝐗𝐏𝐕𝐏": ["nie dostępne", "nie dostępne", "nie dostępne"]
    }
}

@bot.event
async def on_ready():
    print(f"✅ Zalogowano jako {bot.user}")

@bot.command()
async def ticket(ctx):
    global ticket_message_id
    embed = discord.Embed(
        title="🎟️ System ticketów",
        description="Reaguj na 🎟️ aby otworzyć ticket i wybrać co chcesz kupić.",
        color=discord.Color.green()
    )
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("🎟️")
    ticket_message_id = msg.id

@bot.command()
async def weryfikacja(ctx):
    global verification_message_id
    embed = discord.Embed(
        title="✅ Weryfikacja",
        description="Kliknij ✅ aby się zweryfikować i uzyskać dostęp do serwera.",
        color=discord.Color.blue()
    )
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("✅")
    verification_message_id = msg.id

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

        # Automatyczne zamknięcie po godzinie (opcjonalne, możesz usunąć jeśli chcesz)
        async def auto_close():
            await asyncio.sleep(3600)
            if ticket_channel and ticket_channel in guild.text_channels:
                await archive_and_close(ticket_channel, f"Automatyczne zamknięcie ticketu po 1 godzinie")
        bot.loop.create_task(auto_close())

class MenuView(View):
    def __init__(self, member, channel):
        super().__init__(timeout=None)
        self.member = member
        self.channel = channel
        self.selected_server = None
        self.selected_mode = None
        self.selected_items = []

        self.server_select = Select(
            placeholder="Wybierz serwer",
            options=[discord.SelectOption(label=srv) for srv in SERVER_OPTIONS.keys()],
            custom_id="server_select"
        )
        self.server_select.callback = self.server_callback
        self.add_item(self.server_select)

        # Dodajemy przycisk do zamknięcia ticketa
        self.close_button = Button(label="Zamknij ticket", style=discord.ButtonStyle.red, custom_id="close_ticket")
        self.close_button.callback = self.close_ticket_callback
        self.add_item(self.close_button)

    async def server_callback(self, interaction: discord.Interaction):
        if interaction.user != self.member:
            await interaction.response.send_message("Nie możesz korzystać z tego menu.", ephemeral=True)
            return

        self.selected_server = interaction.data['values'][0]
        self.selected_mode = None
        self.selected_items = []

        modes = SERVER_OPTIONS.get(self.selected_server, {})
        self.mode_select = Select(
            placeholder="Wybierz tryb",
            options=[discord.SelectOption(label=mode) for mode in modes.keys()],
            custom_id="mode_select"
        )
        self.mode_select.callback = self.mode_callback

        self.clear_items()
        self.add_item(self.server_select)
        self.add_item(self.mode_select)
        self.add_item(self.close_button)

        await interaction.response.edit_message(content=None, view=self)

    async def mode_callback(self, interaction: discord.Interaction):
        if interaction.user != self.member:
            await interaction.response.send_message("Nie możesz korzystać z tego menu.", ephemeral=True)
            return

        self.selected_mode = interaction.data['values'][0]
        self.selected_items = []

        items = SERVER_OPTIONS[self.selected_server][self.selected_mode]
        self.item_select = Select(
            placeholder="Wybierz item(y)",
            options=[discord.SelectOption(label=item) for item in items],
            custom_id="item_select",
            min_values=1,
            max_values=len(items)
        )
        self.item_select.callback = self.item_callback

        self.clear_items()
        self.add_item(self.server_select)
        self.add_item(self.mode_select)
        self.add_item(self.item_select)
        self.add_item(self.close_button)

        await interaction.response.edit_message(content=None, view=self)

    async def item_callback(self, interaction: discord.Interaction):
        if interaction.user != self.member:
            await interaction.response.send_message("Nie możesz korzystać z tego menu.", ephemeral=True)
            return

        self.selected_items = interaction.data['values']
        await interaction.response.send_message(
            f"Wybrałeś: Serwer: {self.selected_server}, Tryb: {self.selected_mode}, Itemy: {', '.join(self.selected_items)}",
            ephemeral=True
        )

        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(
                title="📥 Nowy wybór w tickecie",
                description=f"**Użytkownik:** {interaction.user.mention}\n"
                            f"**Serwer:** {self.selected_server}\n"
                            f"**Tryb:** {self.selected_mode}\n"
                            f"**Itemy:** {', '.join(self.selected_items)}",
                color=discord.Color.gold(),
                timestamp=datetime.utcnow()
            )
            await log_channel.send(embed=embed)

    async def close_ticket_callback(self, interaction: discord.Interaction):
        if interaction.user != self.member:
            await interaction.response.send_message("Nie możesz zamknąć cudzego ticketu.", ephemeral=True)
            return
        # Potwierdzenie zamknięcia - prosty widok z przyciskami
        view = ConfirmCloseView(self.channel, self.member)
        await interaction.response.send_message("Czy na pewno chcesz zamknąć ticket?", view=view, ephemeral=True)

class ConfirmCloseView(View):
    def __init__(self, channel, member):
        super().__init__(timeout=60)
        self.channel = channel
        self.member = member

    @discord.ui.button(label="Tak, zamknij", style=discord.ButtonStyle.red)
    async def confirm(self, button: Button, interaction: discord.Interaction):
        if interaction.user != self.member:
            await interaction.response.send_message("Nie możesz zamknąć cudzego ticketu.", ephemeral=True)
            return
        await interaction.response.defer()
        await archive_and_close(self.channel, f"Ticket zamknięty przez {interaction.user}")
        await interaction.followup.send("Ticket został zamknięty.", ephemeral=True)
        self.stop()

    @discord.ui.button(label="Anuluj", style=discord.ButtonStyle.grey)
    async def cancel(self, button: Button, interaction: discord.Interaction):
        if interaction.user != self.member:
            await interaction.response.send_message("Nie możesz anulować.", ephemeral=True)
            return
        await interaction.response.send_message("Zamknięcie ticketu anulowane.", ephemeral=True)
        self.stop()

async def archive_and_close(channel: discord.TextChannel, reason: str):
    # Pobieranie wszystkich wiadomości
    messages = []
    async for msg in channel.history(limit=None, oldest_first=True):
        timestamp = msg.created_at.strftime("%Y-%m-%d %H:%M:%S")
        author = msg.author.name
        content = msg.content
        messages.append(f"[{timestamp}] {author}: {content}")

    # Tworzenie pliku tekstowego
    filename = f"ticket-{channel.name}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(messages))

    guild = channel.guild
    log_channel = guild.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        # Wysyłanie pliku do kanału logów
        await log_channel.send(f"📁 Archiwum ticketu `{channel.name}`. Powód: {reason}", file=discord.File(filename))

    # Usuwanie pliku lokalnie
    os.remove(filename)

    # Usuwanie kanału ticketu
    await channel.delete(reason=reason)

bot.run(os.getenv("DISCORD_TOKEN"))
