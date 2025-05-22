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
TICKET_MESSAGE_CHANNEL_ID = 1373305137228939416  # Kanał, gdzie wysyłasz wiadomość z ticketem

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

# --- Komenda do wysłania wiadomości weryfikacyjnej ---
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
    print(f"Wysłano wiadomość weryfikacyjną, ID: {verification_message_id}")

# --- Komenda do wysłania wiadomości ticketowej ---
@bot.command()
async def ticket(ctx):
    global ticket_message_id
    embed = discord.Embed(
        title="🎟️ System ticketów",
        description="Zareaguj na 🎟️ aby otworzyć ticket i wybrać co chcesz kupić.",
        color=discord.Color.green()
    )
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("🎟️")
    ticket_message_id = msg.id
    print(f"Wysłano wiadomość ticketową, ID: {ticket_message_id}")

# --- Event dodania reakcji ---
@bot.event
async def on_raw_reaction_add(payload):
    if payload.member is None or payload.member.bot:
        return

    guild = bot.get_guild(payload.guild_id)
    if not guild:
        print("Nie znaleziono gildii.")
        return

    # Weryfikacja roli
    if payload.message_id == verification_message_id and str(payload.emoji) == "✅":
        role = guild.get_role(ROLE_ID)
        if not role:
            print(f"Brak roli o ID {ROLE_ID}")
            return
        try:
            await payload.member.add_roles(role)
            channel = guild.get_channel(payload.channel_id)
            if channel:
                await channel.send(f"{payload.member.mention}, zostałeś zweryfikowany!", delete_after=5)
        except Exception as e:
            print(f"Błąd przy nadawaniu roli: {e}")

    # Ticket system
    elif payload.message_id == ticket_message_id and str(payload.emoji) == "🎟️":
        category = guild.get_channel(TICKET_CATEGORY_ID)
        if not isinstance(category, discord.CategoryChannel):
            print(f"Brak kategorii ticketów o ID {TICKET_CATEGORY_ID}")
            return

        # Sprawdzanie czy użytkownik ma już ticket
        existing = discord.utils.get(guild.channels, name=f"ticket-{payload.member.name.lower()}")
        if existing:
            try:
                await payload.member.send("Masz już otwarty ticket!")
            except:
                pass
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            payload.member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        try:
            ticket_channel = await guild.create_text_channel(
                f"ticket-{payload.member.name.lower()}",
                category=category,
                overwrites=overwrites,
                reason="Nowy ticket"
            )
        except Exception as e:
            print(f"Błąd przy tworzeniu kanału ticketu: {e}")
            return

        try:
            await ticket_channel.send(f"{payload.member.mention}, wybierz co chcesz kupić:", view=MenuView(payload.member, ticket_channel))
        except Exception as e:
            print(f"Błąd przy wysyłaniu menu w tickecie: {e}")

        # Automatyczne zamknięcie po 1 godzinie
        async def auto_close():
            await asyncio.sleep(3600)
            try:
                await ticket_channel.delete(reason="Automatyczne zamknięcie ticketu po 1 godzinie")
            except Exception as e:
                print(f"Błąd przy automatycznym zamykaniu ticketu: {e}")

        bot.loop.create_task(auto_close())

class MenuView(View):
    def __init__(self, member, channel):
        super().__init__(timeout=None)
        self.member = member
        self.channel = channel
        self.selected_server = None
        self.selected_mode = None
        self.selected_items = []

        # Select - serwer
        self.server_select = Select(
            placeholder="Wybierz serwer",
            options=[discord.SelectOption(label=srv) for srv in SERVER_OPTIONS.keys()],
            custom_id="server_select"
        )
        self.server_select.callback = self.server_callback
        self.add_item(self.server_select)

        # Przyciski
        self.close_button = Button(label="Zamknij ticket", style=discord.ButtonStyle.red)
        self.close_button.callback = self.close_callback
        self.add_item(self.close_button)

    async def server_callback(self, interaction: discord.Interaction):
        if interaction.user != self.member:
            await interaction.response.send_message("To nie twój ticket!", ephemeral=True)
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

        await interaction.response.edit_message(view=self)

    async def mode_callback(self, interaction: discord.Interaction):
        if interaction.user != self.member:
            await interaction.response.send_message("To nie twój ticket!", ephemeral=True)
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

        await interaction.response.edit_message(view=self)

    async def item_callback(self, interaction: discord.Interaction):
        if interaction.user != self.member:
            await interaction.response.send_message("To nie twój ticket!", ephemeral=True)
            return

        self.selected_items = interaction.data['values']

        await interaction.response.send_message(
            f"Wybrałeś: Serwer: **{self.selected_server}**, Tryb: **{self.selected_mode}**, Itemy: **{', '.join(self.selected_items)}**",
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

    async def close_callback(self, interaction: discord.Interaction):
        if interaction.user != self.member:
            await interaction.response.send_message("To nie twój ticket!", ephemeral=True)
            return
        await interaction.response.send_message("Ticket zostanie zamknięty za 3 sekundy...", ephemeral=True)
        await asyncio.sleep(3)
        try:
            await self.channel.delete(reason=f"Ticket zamknięty przez {interaction.user}")
        except Exception as e:
            print(f"Błąd przy zamykaniu ticketu: {e}")

@bot.event
async def on_ready():
    print(f"✅ Zalogowano jako {bot.user}")

bot.run(os.getenv("DISCORD_TOKEN"))
