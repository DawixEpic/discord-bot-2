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
ADMIN_PANEL_CHANNEL_ID = 1374781085895884820  # tutaj id kanału do wysyłania panelu admina

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

OFFER_DATA = {
    1373273108093337640: [
        ("💸 10mld$", "1zł"),
        ("<:Miecz_emoji:1374791139462352906> Miecz 35", "40zł"),
        ("<:Klata_emoji:1374793644246306866> Set 35", "57zł"),
    ],
    1373270295556788285: [
        ("💵 50k$", "1zł"),
        ("💰 1mln$", "15zł"),
        ("🎉 EVENTOWKI:", ""),
        ("<:Excalibur_emoji:1374785662191927416> Excalibur", "270zł"),
        ("<:Totem_emoji:1374788635211206757> Totem ułaskawienia", "80zł"),
        ("<:Sakiewka_emoji:1374799829120716892> Sakiewka", "20zł"),
    ],
    1373268875407396914: [
        ("💸 4,5k$", "1zł"),
        ("💸 50k$", "15zł"),
        ("💸 550k$", "130zł"),
        ("<:ana2_emoji:1374799017359314944> Anarchiczny set 2", "28zł"),
        ("<:Klata_emoji:1374793644246306866> Anarchiczny set 1", "9zł"),
        ("⚔️ MIECZE:", ""),
        ("13732702955567882 Anarchiczny miecz", "3zł"),
        ("🎉 EVENTÓWKI:", ""),
        ("🐰 Zajęczy miecz", "65zł"),
        ("<:Totem_emoji:1374788635211206757> Totem ułaskawienia", "170zł"),
        ("<:Excalibur_emoji:1374785662191927416> Excalibur", "360zł"),
    ],
    1373267159576481842: [
        ("<:Klata_emoji:1374793644246306866> Set 25", "30zł"),
        ("<:Miecz_emoji:1374791139462352906> Miecz 25", "25zł"),
        ("<:Kilof_emoji:1374795407493959751> Kilof 25", "10zł"),
        ("💵 1mln$", "18zł"),
    ],
    1373266589310517338: [
        ("<:Elytra_enoji:1374797373406187580> Elytra", "12zł"),
        ("<:Buty_enoji:1374796797222064230> Buty flasha", "5zł"),
        ("<:Miecz_emoji:1374791139462352906> Miecz 6", "3zł"),
        ("💵 1k$", "1zł"),
        ("<:Shulker_enoji:1374795916531335271> Shulker s2", "7zł"),
        ("<:Shulker_enoji:1374795916531335271> Shulker totemów", "6zł"),
    ],
    1374380939970347019: [
        ("💸 15k$", "1zł"),
        ("🌟 Buddha", "30zł"),
        ("💖 Love swap", "100zł"),
        ("🐉 Klata meduzy", "140zł"),
    ],
}


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


@bot.command()
@commands.has_permissions(administrator=True)
async def oferta(ctx):
    for channel_id, items in OFFER_DATA.items():
        try:
            channel = await bot.fetch_channel(channel_id)
            description = ""
            for name, price in items:
                if price:
                    description += f"**{name}** — *Cena:* `{price}`\n"
                else:
                    description += f"**{name}**\n"

            embed = discord.Embed(
                title="🛒 Oferta itemów na sprzedaż",
                description=description + "\n**Kliknij przycisk poniżej, aby otworzyć ticket.**",
                color=discord.Color.gold()
            )
            view = TicketButtonView()
            await channel.send(embed=embed, view=view)
            print(f"✅ Wysłano ofertę do kanału {channel.name}")
        except Exception as e:
            print(f"❌ Błąd przy wysyłaniu oferty do kanału {channel_id}: {e}")


class AdminPanelView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Zamknij ticket", style=discord.ButtonStyle.danger)
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.channel.category_id == TICKET_CATEGORY_ID:
            await interaction.channel.delete()
        else:
            await interaction.response.send_message("To nie jest kanał ticketu.", ephemeral=True)

    @discord.ui.button(label="Pokaż listę ticketów", style=discord.ButtonStyle.secondary)
    async def show_tickets(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        tickets = []
        category = discord.utils.get(guild.categories, id=TICKET_CATEGORY_ID)
        if category:
            for channel in category.channels:
                tickets.append(channel.name)
            if tickets:
                await interaction.response.send_message(f"Otwartych ticketów: {', '.join(tickets)}", ephemeral=True)
            else:
                await interaction.response.send_message("Brak otwartych ticketów.", ephemeral=True)
        else:
            await interaction.response.send_message("Nie znaleziono kategorii ticketów.", ephemeral=True)


class TicketButtonView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Otwórz ticket", style=discord.ButtonStyle.primary, emoji="🎟️")
    async def open_ticket_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await create_ticket(interaction.user, interaction.guild, interaction.channel)


async def create_ticket(user, guild, origin_channel):
    # Sprawdź, czy użytkownik ma już ticket
    category = guild.get_channel(TICKET_CATEGORY_ID)
    existing_ticket = discord.utils.get(category.channels, name=f"ticket-{user.name.lower()}")
    if existing_ticket:
        await origin_channel.send(f"{user.mention}, masz już otwarty ticket!", delete_after=10)
        return

    # Utwórz kanał ticketu
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }

    ticket_channel = await category.create_text_channel(f"ticket-{user.name}", overwrites=overwrites)
    await origin_channel.send(f"{user.mention}, ticket został utworzony: {ticket_channel.mention}", delete_after=10)

    print("Ticket utworzony, wysyłam MenuView (za 1 sekundę)...")
    await asyncio.sleep(1)  # opóźnienie dla Discorda

    # Wyślij widok MenuView w kanale ticketu
    await ticket_channel.send("Wybierz serwer i tryb:", view=MenuView())


class MenuView(View):
    def __init__(self):
        super().__init__(timeout=None)

        self.selected_server = None
        self.selected_mode = None
        self.selected_items = []

        # Select serwera - enabled od razu
        self.server_select = Select(
            placeholder="Wybierz serwer...",
            options=[discord.SelectOption(label=key) for key in SERVER_OPTIONS.keys()]
        )
        self.server_select.callback = self.server_selected
        self.add_item(self.server_select)

        # Select trybu - disabled na start
        self.mode_select = Select(
            placeholder="Wybierz tryb...",
            options=[],
            disabled=True
        )
        self.mode_select.callback = self.mode_selected
        self.add_item(self.mode_select)

        # Select itemów - disabled na start
        self.items_select = Select(
            placeholder="Wybierz itemy (możesz wybrać wiele)...",
            options=[],
            disabled=True,
            min_values=1,
            max_values=5
        )
        self.items_select.callback = self.items_selected
        self.add_item(self.items_select)

    async def server_selected(self, interaction: discord.Interaction):
        self.selected_server = self.server_select.values[0]
        print(f"Wybrano serwer: {self.selected_server}")

        # Ustaw opcje trybu wg serwera
        modes = SERVER_OPTIONS.get(self.selected_server, {})
        mode_options = [discord.SelectOption(label=mode) for mode in modes.keys()]

        self.mode_select.options = mode_options
        self.mode_select.disabled = False

        # Resetuj tryb i itemy
        self.selected_mode = None
        self.selected_items = []
        self.items_select.options = []
        self.items_select.disabled = True

        await interaction.response.edit_message(view=self)

    async def mode_selected(self, interaction: discord.Interaction):
        self.selected_mode = self.mode_select.values[0]
        print(f"Wybrano tryb: {self.selected_mode}")

        # Ustaw itemy wg serwera i trybu
        items = SERVER_OPTIONS[self.selected_server].get(self.selected_mode, [])
        item_options = [discord.SelectOption(label=item) for item in items]

        self.items_select.options = item_options
        self.items_select.disabled = False
        self.selected_items = []

        await interaction.response.edit_message(view=self)

    async def items_selected(self, interaction: discord.Interaction):
        self.selected_items = self.items_select.values
        print(f"Wybrane itemy: {self.selected_items}")

        # Tutaj możesz zapisać do logów kto co wybrał i kiedy
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            user = interaction.user
            log_msg = (f"📝 **Log ticket:**\n"
                       f"Użytkownik: {user} (ID: {user.id})\n"
                       f"Czas: {now}\n"
                       f"Serwer: {self.selected_server}\n"
                       f"Tryb: {self.selected_mode}\n"
                       f"Itemy: {', '.join(self.selected_items)}")
            await log_channel.send(log_msg)

        await interaction.response.send_message("Wybrano opcje i zapisano do logów!", ephemeral=True)

# Event do weryfikacji
@bot.event
async def on_raw_reaction_add(payload):
    if payload.message_id == verification_message_id:
        guild = bot.get_guild(payload.guild_id)
        if not guild:
            return
        member = guild.get_member(payload.user_id)
        if not member or member.bot:
            return
        if str(payload.emoji) == "✅":
            role = guild.get_role(ROLE_ID)
            if role and role not in member.roles:
                await member.add_roles(role)
                print(f"Dodano rolę {role.name} użytkownikowi {member.name}")

    if payload.message_id == ticket_message_id:
        guild = bot.get_guild(payload.guild_id)
        if not guild:
            return
        member = guild.get_member(payload.user_id)
        if not member or member.bot:
            return
        if str(payload.emoji) == "🎟️":
            print(f"{member} kliknął reakcję 🎟️, tworzenie ticketu...")
            channel = guild.get_channel(TICKET_CHANNEL_ID)
            if not channel:
                print("Nie znaleziono kanału ticket.")
                return
            await create_ticket(member, guild, channel)


# Komenda testowa do sprawdzenia widoku MenuView
@bot.command()
async def testview(ctx):
    await ctx.send("Test MenuView:", view=MenuView())


# Uruchom bota
TOKEN = os.getenv("BOT_TOKEN")
bot.run(TOKEN)
