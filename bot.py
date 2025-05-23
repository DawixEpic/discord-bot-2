import discord
from discord.ext import commands
from discord.ui import View, Select, Button
import asyncio
import os
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

ROLE_ID = 1373275307150278686
TICKET_CATEGORY_ID = 1373277957446959135
LOG_CHANNEL_ID = 1374479815914291240

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

# Zlicznik ticketów, globalny (prosty sposób numeracji)
ticket_counter = 0

@bot.event
async def on_ready():
    print(f"✅ Zalogowano jako {bot.user}")

# --- Komenda wysyłająca embed z przyciskiem weryfikacji ---
@bot.command()
async def weryfikacja(ctx):
    embed = discord.Embed(
        title="✅ Weryfikacja",
        description="Kliknij przycisk poniżej aby się zweryfikować i uzyskać dostęp do serwera.",
        color=discord.Color.blue()
    )
    view = VerificationView()
    await ctx.send(embed=embed, view=view)

# --- Komenda wysyłająca embed z przyciskiem otwarcia ticketa ---
@bot.command()
async def ticket(ctx):
    embed = discord.Embed(
        title="🎟️ System ticketów",
        description="Kliknij przycisk poniżej, aby otworzyć ticket i wybrać co chcesz kupić.",
        color=discord.Color.green()
    )
    view = TicketOpenView()
    await ctx.send(embed=embed, view=view)

# --- View z przyciskiem do weryfikacji ---
class VerificationView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(VerificationButton())

class VerificationButton(Button):
    def __init__(self):
        super().__init__(label="Zweryfikuj się ✅", style=discord.ButtonStyle.success)

    async def callback(self, interaction: discord.Interaction):
        role = interaction.guild.get_role(ROLE_ID)
        if not role:
            await interaction.response.send_message("❌ Nie znaleziono roli weryfikacji.", ephemeral=True)
            return

        if role in interaction.user.roles:
            await interaction.response.send_message("Jesteś już zweryfikowany!", ephemeral=True)
            return

        try:
            await interaction.user.add_roles(role, reason="Weryfikacja przez przycisk")
            await interaction.response.send_message("✅ Pomyślnie zweryfikowano!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Wystąpił błąd podczas weryfikacji: {e}", ephemeral=True)

# --- View z przyciskiem do otwarcia ticketa ---
class TicketOpenView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(OpenTicketButton())

class OpenTicketButton(Button):
    def __init__(self):
        super().__init__(label="Otwórz ticket 🎟️", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        global ticket_counter

        guild = interaction.guild
        category = guild.get_channel(TICKET_CATEGORY_ID)
        if not category or not isinstance(category, discord.CategoryChannel):
            await interaction.response.send_message("❌ Nie znaleziono kategorii ticketów na serwerze.", ephemeral=True)
            return

        # Sprawdź czy użytkownik nie ma już otwartego ticketa
        existing_channel = discord.utils.get(guild.text_channels, name=f"ticket-{interaction.user.name.lower()}")
        if existing_channel:
            await interaction.response.send_message(f"Masz już otwarty ticket: {existing_channel.mention}", ephemeral=True)
            return

        # Zwiększ licznik ticketów o 1 i nadaj numer ticketu
        ticket_counter += 1
        channel_name = f"ticket-{interaction.user.name.lower()}-{ticket_counter}"

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }

        try:
            ticket_channel = await guild.create_text_channel(channel_name, category=category, overwrites=overwrites, reason=f"Ticket od {interaction.user}")
        except Exception as e:
            await interaction.response.send_message(f"❌ Nie udało się utworzyć kanału ticketu: {e}", ephemeral=True)
            return

        # Wyślij wiadomość powitalną i menu wyboru
        embed = discord.Embed(
            title=f"🎟️ Ticket #{ticket_counter}",
            description=f"Witaj {interaction.user.mention}!\n\nWybierz, co chcesz kupić, używając menu poniżej.",
            color=discord.Color.blurple()
        )
        view = MenuView(interaction.user, ticket_channel)
        close_button = CloseTicketButton(ticket_channel)
        view.add_item(close_button)

        await ticket_channel.send(embed=embed, view=view)
        await interaction.response.send_message(f"🎟️ Ticket utworzony: {ticket_channel.mention}", ephemeral=True)

        # Automatyczne zamknięcie po 1 godzinie (3600 sekund)
        async def auto_close():
            await asyncio.sleep(3600)
            if ticket_channel and ticket_channel in guild.text_channels:
                try:
                    await ticket_channel.delete(reason="Automatyczne zamknięcie ticketu po 1 godzinie")
                except:
                    pass

        bot.loop.create_task(auto_close())

# --- Przycisk zamknięcia ticketu ---
class CloseTicketButton(Button):
    def __init__(self, channel):
        super().__init__(label="Zamknij ticket ❌", style=discord.ButtonStyle.danger)
        self.channel = channel

    async def callback(self, interaction: discord.Interaction):
        # Sprawdź czy osoba klika w odpowiednim kanale
        if interaction.channel != self.channel:
            await interaction.response.send_message("❌ Ten przycisk działa tylko w tym tickecie.", ephemeral=True)
            return

        try:
            await interaction.response.send_message("Ticket zostanie zamknięty za 5 sekund...", ephemeral=True)
            await asyncio.sleep(5)
            await self.channel.delete(reason=f"Ticket zamknięty przez {interaction.user}")
        except Exception as e:
            await interaction.followup.send(f"❌ Błąd przy zamykaniu ticketu: {e}", ephemeral=True)

# --- View menu wyboru serwera, trybu i itemów ---
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

    async def server_callback(self, interaction: discord.Interaction):
        if interaction.user != self.member:
            await interaction.response.send_message("Nie możesz używać tego menu.", ephemeral=True)
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

        await interaction.response.edit_message(view=self)

    async def mode_callback(self, interaction: discord.Interaction):
        if interaction.user != self.member:
            await interaction.response.send_message("Nie możesz używać tego menu.", ephemeral=True)
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

        await interaction.response.edit_message(view=self)

    async def item_callback(self, interaction: discord.Interaction):
        if interaction.user != self.member:
            await interaction.response.send_message("Nie możesz używać tego menu.", ephemeral=True)
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

bot.run(os.getenv("DISCORD_TOKEN"))
