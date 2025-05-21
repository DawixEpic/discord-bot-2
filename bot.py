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

async def log_action(guild, message):
    log_channel = guild.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(message)

@bot.event
async def on_ready():
    print(f"✅ Zalogowano jako {bot.user}")

    channel = bot.get_channel(ADMIN_PANEL_CHANNEL_ID)
    if channel:
        embed = discord.Embed(
            title="Panel administracyjny ticketów",
            description="Użyj przycisków poniżej aby zarządzać ticketami.\n\n"
                        "- Zamknij ten ticket (usuwa kanał, działa w kanale ticketu)\n"
                        "- Pokaż listę ticketów (lista otwartych kanałów ticketów)",
            color=discord.Color.red()
        )
        view = AdminPanelView()
        await channel.send(embed=embed, view=view)
    else:
        print("❌ Nie znaleziono kanału do wysłania panelu admina.")

@bot.command()
@commands.has_permissions(administrator=True)
async def weryfikacja(ctx):
    embed = discord.Embed(
        title="✅ Weryfikacja",
        description="Kliknij ✅ aby się zweryfikować i dostać dostęp.",
        color=discord.Color.green()
    )
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("✅")
    global verification_message_id
    verification_message_id = msg.id
    await ctx.send("✅ Wiadomość weryfikacyjna została wysłana.")

@bot.command()
@commands.has_permissions(administrator=True)
async def ticket(ctx):
    embed = discord.Embed(
        title="🎟️ Napisz co chcesz kupić",
        description="Kliknij 🎟️ aby otworzyć prywatny ticket z wyborem opcji.",
        color=discord.Color.blue()
    )
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("🎟️")
    global ticket_message_id
    ticket_message_id = msg.id
    await ctx.send("✅ Wiadomość ticket została wysłana.")

@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id:
        return

    guild = bot.get_guild(payload.guild_id)
    if not guild:
        return

    member = guild.get_member(payload.user_id)
    if not member:
        return

    # Reakcja na weryfikację
    if payload.message_id == verification_message_id and str(payload.emoji) == "✅":
        role = guild.get_role(ROLE_ID)
        if role:
            await member.add_roles(role)
            print(f"Przyznano rolę {role.name} użytkownikowi {member.display_name}")
        return

    # Reakcja na otwarcie ticketu
    if payload.message_id == ticket_message_id and str(payload.emoji) == "🎟️":
        # Sprawdź czy użytkownik ma już ticket
        category = guild.get_channel(TICKET_CATEGORY_ID)
        if not category:
            print("❌ Nie znaleziono kategorii ticketów")
            return

        existing_ticket = discord.utils.get(category.channels, name=f"ticket-{member.name.lower()}")
        if existing_ticket:
            try:
                await member.send("Masz już otwarty ticket!")
            except:
                pass
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True)
        }

        channel_name = f"ticket-{member.name.lower()}"
        ticket_channel = await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)
        await ticket_channel.send(f"{member.mention}, wybierz co chcesz kupić:", view=MenuView(member, ticket_channel))

        await log_action(guild, f"Ticket utworzony przez {member} - kanał: {ticket_channel.name}")

class MenuView(View):
    def __init__(self, member, ticket_channel):
        super().__init__(timeout=None)
        self.member = member
        self.ticket_channel = ticket_channel
        self.server_selected = None
        self.mode_selected = None

        self.server_select = Select(
            placeholder="Wybierz serwer",
            options=[discord.SelectOption(label=s) for s in SERVER_OPTIONS.keys()],
            custom_id="server_select"
        )
        self.server_select.callback = self.server_select_callback

        self.mode_select = Select(
            placeholder="Wybierz tryb",
            options=[],
            custom_id="mode_select",
            disabled=True
        )
        self.mode_select.callback = self.mode_select_callback

        self.items_select = Select(
            placeholder="Wybierz item",
            options=[],
            custom_id="items_select",
            disabled=True
        )
        self.items_select.callback = self.items_select_callback

        self.add_item(self.server_select)
        self.add_item(self.mode_select)
        self.add_item(self.items_select)

    async def server_select_callback(self, interaction: discord.Interaction):
        if interaction.user != self.member:
            await interaction.response.send_message("To nie jest twój ticket!", ephemeral=True)
            return

        self.server_selected = self.server_select.values[0]
        self.mode_select.options = [discord.SelectOption(label=m) for m in SERVER_OPTIONS[self.server_selected].keys()]
        self.mode_select.disabled = False

        self.items_select.options = []
        self.items_select.disabled = True

        await interaction.response.edit_message(view=self)
        await log_action(interaction.guild, f"{self.member} wybrał serwer: {self.server_selected}")

    async def mode_select_callback(self, interaction: discord.Interaction):
        if interaction.user != self.member:
            await interaction.response.send_message("To nie jest twój ticket!", ephemeral=True)
            return

        self.mode_selected = self.mode_select.values[0]
        items = SERVER_OPTIONS[self.server_selected][self.mode_selected]
        self.items_select.options = [discord.SelectOption(label=i) for i in items]
        self.items_select.disabled = False

        await interaction.response.edit_message(view=self)
        await log_action(interaction.guild, f"{self.member} wybrał tryb: {self.mode_selected}")

    async def items_select_callback(self, interaction: discord.Interaction):
        if interaction.user != self.member:
            await interaction.response.send_message("To nie jest twój ticket!", ephemeral=True)
            return

        item = self.items_select.values[0]
        await interaction.response.send_message(f"Wybrałeś: {item}", ephemeral=True)
        await log_action(interaction.guild, f"{self.member} wybrał item: {item}")

class AdminPanelView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(label="Zamknij ticket", style=discord.ButtonStyle.red, custom_id="close_ticket"))
        self.add_item(Button(label="Lista ticketów", style=discord.ButtonStyle.grey, custom_id="list_tickets"))

    @discord.ui.button(label="Zamknij ticket", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: Button):
        channel = interaction.channel
        if not channel.name.startswith("ticket-"):
            await interaction.response.send_message("Ta komenda działa tylko w kanale ticketu.", ephemeral=True)
            return

        await channel.delete(reason=f"Ticket zamknięty przez {interaction.user}")
        await log_action(interaction.guild, f"Ticket {channel.name} został zamknięty przez {interaction.user}")
        await interaction.response.send_message("Ticket został zamknięty.", ephemeral=True)

    @discord.ui.button(label="Lista ticketów", style=discord.ButtonStyle.grey, custom_id="list_tickets")
    async def list_tickets(self, interaction: discord.Interaction, button: Button):
        category = interaction.guild.get_channel(TICKET_CATEGORY_ID)
        if not category:
            await interaction.response.send_message("Nie znaleziono kategorii ticketów.", ephemeral=True)
            return

        tickets = [c.name for c in category.channels if c.name.startswith("ticket-")]
        msg = "Lista otwartych ticketów:\n" + "\n".join(tickets) if tickets else "Brak otwartych ticketów."
        await interaction.response.send_message(msg, ephemeral=True)

bot.run(os.getenv("DISCORD_TOKEN"))  # Wstaw swój token do zmiennej środowiskowej DISCORD_TOKEN
