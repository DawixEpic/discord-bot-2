import discord
from discord.ext import commands
from discord.ui import View, Button, Select
from datetime import datetime
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Twoje ID i konfiguracje
ROLE_ID = 1373275307150278686           # rola do weryfikacji
TICKET_CATEGORY_ID = 1373277957446959135  # kategoria ticketów
LOG_CHANNEL_ID = 1374479815914291240       # kanał logów

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

# Komenda do wysłania przycisków weryfikacji i ticketu
@bot.command()
async def start(ctx):
    view = MainView()
    await ctx.send("Kliknij przyciski, aby się zweryfikować lub otworzyć ticket:", view=view)

class MainView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(VerifyButton())
        self.add_item(TicketButton())

class VerifyButton(Button):
    def __init__(self):
        super().__init__(label="Weryfikacja ✅", style=discord.ButtonStyle.green, custom_id="verify_button")

    async def callback(self, interaction: discord.Interaction):
        role = interaction.guild.get_role(ROLE_ID)
        if role in interaction.user.roles:
            await interaction.response.send_message("Jesteś już zweryfikowany!", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("Weryfikacja przebiegła pomyślnie! Masz teraz dostęp do serwera.", ephemeral=True)

class TicketButton(Button):
    def __init__(self):
        super().__init__(label="Otwórz ticket 🎟️", style=discord.ButtonStyle.blurple, custom_id="ticket_button")

    async def callback(self, interaction: discord.Interaction):
        # Sprawdź, czy już ticket istnieje
        guild = interaction.guild
        category = guild.get_channel(TICKET_CATEGORY_ID)
        channel_name = f"ticket-{interaction.user.name}".lower()
        existing = discord.utils.get(guild.text_channels, name=channel_name)
        if existing:
            await interaction.response.send_message(f"Masz już otwarty ticket: {existing.mention}", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        ticket_channel = await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)
        await interaction.response.send_message(f"Ticket utworzony: {ticket_channel.mention}", ephemeral=True)
        await ticket_channel.send(f"{interaction.user.mention}, wybierz serwer, tryb i itemy w menu poniżej.", view=TicketMenuView(interaction.user))

class TicketMenuView(View):
    def __init__(self, member):
        super().__init__(timeout=None)
        self.member = member
        self.selected_server = None
        self.selected_mode = None
        self.selected_items = []

        # Select do serwera
        self.server_select = Select(
            placeholder="Wybierz serwer",
            options=[discord.SelectOption(label=server) for server in SERVER_OPTIONS.keys()],
            custom_id="server_select"
        )
        self.server_select.callback = self.server_select_callback
        self.add_item(self.server_select)

        # Przyciski i inne selecty będą dodawane dynamicznie

    async def server_select_callback(self, interaction: discord.Interaction):
        if interaction.user != self.member:
            await interaction.response.send_message("To nie jest twój ticket!", ephemeral=True)
            return

        self.selected_server = interaction.data['values'][0]
        self.selected_mode = None
        self.selected_items = []

        # Usuń poprzednie selecty oprócz server_select
        self.clear_items()
        self.add_item(self.server_select)

        # Dodaj select trybów
        modes = SERVER_OPTIONS[self.selected_server].keys()
        self.mode_select = Select(
            placeholder="Wybierz tryb",
            options=[discord.SelectOption(label=mode) for mode in modes],
            custom_id="mode_select"
        )
        self.mode_select.callback = self.mode_select_callback
        self.add_item(self.mode_select)

        # Dodaj przycisk zamknięcia ticketu
        self.close_button = Button(label="Zamknij ticket", style=discord.ButtonStyle.red)
        self.close_button.callback = self.close_ticket_callback
        self.add_item(self.close_button)

        await interaction.response.edit_message(view=self)

    async def mode_select_callback(self, interaction: discord.Interaction):
        if interaction.user != self.member:
            await interaction.response.send_message("To nie jest twój ticket!", ephemeral=True)
            return

        self.selected_mode = interaction.data['values'][0]
        self.selected_items = []

        # Usuń poprzednie selecty i przyciski
        self.clear_items()
        self.add_item(self.server_select)
        self.add_item(self.mode_select)
        self.add_item(self.close_button)

        # Dodaj select itemów (multi select)
        items = SERVER_OPTIONS[self.selected_server][self.selected_mode]
        self.item_select = Select(
            placeholder="Wybierz itemy (możesz wybrać kilka)",
            options=[discord.SelectOption(label=item) for item in items],
            custom_id="item_select",
            min_values=1,
            max_values=len(items)
        )
        self.item_select.callback = self.item_select_callback
        self.add_item(self.item_select)

        await interaction.response.edit_message(view=self)

    async def item_select_callback(self, interaction: discord.Interaction):
        if interaction.user != self.member:
            await interaction.response.send_message("To nie jest twój ticket!", ephemeral=True)
            return

        self.selected_items = interaction.data['values']

        await interaction.response.send_message(
            f"Wybrałeś:\n**Serwer:** {self.selected_server}\n**Tryb:** {self.selected_mode}\n**Itemy:** {', '.join(self.selected_items)}",
            ephemeral=True
        )

        # Logowanie do kanału logów
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
            await interaction.response.send_message("Nie możesz zamknąć czyjegoś ticketu.", ephemeral=True)
            return

        await interaction.response.send_message("Ticket zostanie zamknięty.", ephemeral=True)
        await asyncio.sleep(1)
        await self.close_ticket(interaction.channel)

    async def close_ticket(self, channel):
        await channel.delete(reason="Ticket zamknięty przez użytkownika")

bot.run(os.getenv("DISCORD_TOKEN"))
