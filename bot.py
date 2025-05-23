import discord
from discord.ext import commands
from discord.ui import View, Select, Button, Modal, TextInput
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
ADMIN_PANEL_CHANNEL_ID = 1374781085895884820
RATING_CHANNEL_ID = 1375528888586731762  # Kanał na oceny

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

# Store ticket states (ticket_channel.id: {user_id, realized(bool)})
open_tickets = {}

@bot.event
async def on_ready():
    print(f"✅ Zalogowano jako {bot.user}")

@bot.command()
async def weryfikacja(ctx):
    embed = discord.Embed(
        title="✅ Weryfikacja",
        description="Kliknij przycisk poniżej, aby się zweryfikować i uzyskać dostęp do serwera.",
        color=discord.Color.blue()
    )
    view = View()
    view.add_item(VerifyButton())
    await ctx.send(embed=embed, view=view)

class VerifyButton(Button):
    def __init__(self):
        super().__init__(label="✅ Zweryfikuj", style=discord.ButtonStyle.success)

    async def callback(self, interaction: discord.Interaction):
        role = interaction.guild.get_role(ROLE_ID)
        if role:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("✅ Zweryfikowano pomyślnie!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Rola nie została znaleziona.", ephemeral=True)

@bot.command()
async def ticket(ctx):
    embed = discord.Embed(
        title="🎟️ System ticketów",
        description="Kliknij poniżej, aby otworzyć ticket i wybrać co chcesz kupić.",
        color=discord.Color.green()
    )
    view = View()
    view.add_item(OpenTicketButton())
    await ctx.send(embed=embed, view=view)

class OpenTicketButton(Button):
    def __init__(self):
        super().__init__(label="🎟️ Otwórz ticket", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        category = guild.get_channel(TICKET_CATEGORY_ID)
        if not isinstance(category, discord.CategoryChannel):
            await interaction.response.send_message("❌ Nie znaleziono kategorii dla ticketów.", ephemeral=True)
            return

        channel_name = f"ticket-{interaction.user.name}".lower()
        if discord.utils.get(guild.channels, name=channel_name):
            await interaction.response.send_message("❗ Masz już otwarty ticket.", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        ticket_channel = await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)
        ticket_id = ticket_channel.id
        open_tickets[ticket_channel.id] = {"user_id": interaction.user.id, "realized": False}

        await ticket_channel.send(
            f"{interaction.user.mention}, witaj! Wybierz z poniższego menu co chcesz kupić.\n📄 **ID Ticketa:** `{ticket_id}`",
            view=MenuView(interaction.user, ticket_channel)
        )

        await interaction.response.send_message("✅ Ticket został utworzony!", ephemeral=True)

        # Opcjonalne auto zamknięcie po godzinie (można zmienić lub usunąć)
        # await asyncio.sleep(3600)
        # if ticket_channel and ticket_channel in guild.text_channels:
        #     await ticket_channel.delete(reason="Automatyczne zamknięcie ticketu po 1h")

class CloseTicketButton(Button):
    def __init__(self, channel, author_id):
        super().__init__(label="❌ Zamknij ticket", style=discord.ButtonStyle.danger)
        self.channel = channel
        self.author_id = author_id

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id and not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ Nie masz uprawnień do zamknięcia tego ticketu.", ephemeral=True)
            return

        await interaction.response.send_message("✅ Ticket zostanie zamknięty za 5 sekund...", ephemeral=True)
        await asyncio.sleep(5)
        await self.channel.delete(reason="Zamknięty przez użytkownika")

class RealizeTicketButton(Button):
    def __init__(self, channel):
        super().__init__(label="✅ Zrealizuj ticket", style=discord.ButtonStyle.success)
        self.channel = channel

    async def callback(self, interaction: discord.Interaction):
        # Sprawdzenie uprawnień admina
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ Nie masz uprawnień do zrealizowania ticketu.", ephemeral=True)
            return

        # Oznacz ticket jako zrealizowany
        if self.channel.id in open_tickets:
            open_tickets[self.channel.id]["realized"] = True
            user_id = open_tickets[self.channel.id]["user_id"]
            user = interaction.guild.get_member(user_id)
            if user:
                try:
                    await user.send(
                        f"Twój ticket na serwerze {interaction.guild.name} został oznaczony jako **zrealizowany**.\n"
                        f"Prosimy o wystawienie oceny na kanale <#{RATING_CHANNEL_ID}>.\n"
                        "Oceń w trzech kategoriach (1-5 gwiazdek): Szybkość dostawy, Przyjęcie zamówienia, Ogólna ocena.\n"
                        "Odpowiedz w wiadomości w formacie:\n"
                        "`!ocena <szybkosc> <przyjecie> <ogolna>`\n"
                        "np. `!ocena 5 4 5`"
                    )
                except discord.Forbidden:
                    await interaction.response.send_message("❌ Nie mogłem wysłać wiadomości do użytkownika (DM zablokowane?).", ephemeral=True)
                    return
            await interaction.response.send_message("✅ Ticket oznaczony jako zrealizowany. Użytkownik otrzymał instrukcje oceny.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Ten ticket nie jest w systemie lub już zrealizowany.", ephemeral=True)

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
        self.add_item(CloseTicketButton(channel, member.id))
        self.add_item(RealizeTicketButton(channel))

    async def server_callback(self, interaction: discord.Interaction):
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
        self.add_item(CloseTicketButton(self.channel, self.member.id))
        self.add_item(RealizeTicketButton(self.channel))
        await interaction.response.edit_message(content=None, view=self)

    async def mode_callback(self, interaction: discord.Interaction):
        self.selected_mode = interaction.data['values'][0]
        self.selected_items = []

        items = SERVER_OPTIONS[self.selected_server][self.selected_mode]
        self.item_select = Select(
            placeholder="Wybierz itemy",
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
        self.add_item(CloseTicketButton(self.channel, self.member.id))
        self.add_item(RealizeTicketButton(self.channel))
        await interaction.response.edit_message(content=None, view=self)

    async def item_callback(self, interaction: discord.Interaction):
        self.selected_items = interaction.data['values']
        await interaction.response.send_message(
            f"✅ Wybrałeś: **{self.selected_server}** → **{self.selected_mode}**\n🧾 Itemy: {', '.join(self.selected_items)}",
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

# Komenda do wystawiania ocen w formacie: !ocena 5 4 5
@bot.command()
async def ocena(ctx, szybkosc: int, przyjecie: int, ogolna: int):
    if ctx.channel.id != RATING_CHANNEL_ID:
        await ctx.send(f"❌ Oceny można wystawiać tylko na kanale <#{RATING_CHANNEL_ID}>.")
        return
    if not (1 <= szybkosc <= 5 and 1 <= przyjecie <= 5 and 1 <= ogolna <= 5):
        await ctx.send("❌ Oceny muszą być w zakresie 1-5.")
        return

    embed = discord.Embed(
        title="⭐ Nowa ocena od użytkownika",
        description=f"**Użytkownik:** {ctx.author.mention}\n"
                    f"**Szybkość dostawy:** {szybkosc} ⭐\n"
                    f"**Przyjęcie zamówienia:** {przyjecie} ⭐\n"
                    f"**Ogólna ocena:** {ogolna} ⭐",
        color=discord.Color.green(),
        timestamp=datetime.utcnow()
    )
    await ctx.send(embed=embed)

bot.run(os.getenv("DISCORD_TOKEN"))
