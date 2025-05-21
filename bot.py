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
                description=description + "\n**Kliknij przycisk poniżej, aby otworzyć ticket i dokonać zakupu!**",
                color=discord.Color.blurple()
            )

            button = Button(
                label="📝 Otwórz Ticket",
                style=discord.ButtonStyle.link,
                url=f"https://discord.com/channels/{ctx.guild.id}/{TICKET_CHANNEL_ID}"
            )
            view = View()
            view.add_item(button)

            await channel.send(embed=embed, view=view)
        except Exception as e:
            print(f"❌ Błąd podczas wysyłania oferty do kanału {channel_id}: {e}")



@bot.event
async def on_raw_reaction_add(payload):
    if payload.message_id == verification_message_id and str(payload.emoji) == "✅":
        guild = bot.get_guild(payload.guild_id)
        if guild is None:
            return
        member = guild.get_member(payload.user_id)
        if member is None or member.bot:
            return

        role = guild.get_role(ROLE_ID)
        if role:
            await member.add_roles(role)
            print(f"Dodano rolę {role.name} użytkownikowi {member}.")


    if payload.message_id == ticket_message_id and str(payload.emoji) == "🎟️":
        guild = bot.get_guild(payload.guild_id)
        if guild is None:
            return
        member = guild.get_member(payload.user_id)
        if member is None or member.bot:
            return

        # Sprawdź, czy użytkownik już ma ticket w tej kategorii
        category = guild.get_channel(TICKET_CATEGORY_ID)
        if category is None:
            print("❌ Nie znaleziono kategorii ticketów.")
            return

        existing_ticket = None
        for channel in category.channels:
            if channel.permissions_for(member).read_messages:
                existing_ticket = channel
                break
        if existing_ticket:
            try:
                await member.send(f"Masz już otwarty ticket: {existing_ticket.mention}")
            except Exception:
                pass
            return

        # Tworzenie kanału ticketu
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }
        channel_name = f"ticket-{member.name}"
        ticket_channel = await guild.create_text_channel(channel_name, overwrites=overwrites, category=category)
        await ticket_channel.send(f"Witaj {member.mention}! Opisz tutaj, co chcesz kupić.")

        # Wyświetl wybór serwera i trybu
        await ticket_channel.send("Wybierz serwer i tryb:", view=MenuView())



class MenuView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.selected_server = None
        self.selected_mode = None
        self.selected_items = []

        self.server_select = Select(
            placeholder="Wybierz serwer",
            options=[discord.SelectOption(label=server) for server in SERVER_OPTIONS.keys()],
            custom_id="server_select"
        )
        self.server_select.callback = self.server_callback
        self.add_item(self.server_select)

        self.mode_select = Select(
            placeholder="Najpierw wybierz serwer",
            options=[],
            custom_id="mode_select",
            disabled=True
        )
        self.mode_select.callback = self.mode_callback
        self.add_item(self.mode_select)

        self.item_select = Select(
            placeholder="Najpierw wybierz tryb",
            options=[],
            custom_id="item_select",
            disabled=True,
            max_values=25
        )
        self.item_select.callback = self.item_callback
        self.add_item(self.item_select)

    async def server_callback(self, interaction: discord.Interaction):
        self.selected_server = interaction.data['values'][0]
        modes = SERVER_OPTIONS[self.selected_server]
        self.mode_select.options = [discord.SelectOption(label=mode) for mode in modes.keys()]
        self.mode_select.placeholder = "Wybierz tryb"
        self.mode_select.disabled = False

        self.item_select.options = []
        self.item_select.disabled = True
        self.selected_mode = None
        self.selected_items = []

        await interaction.response.edit_message(view=self)

    async def mode_callback(self, interaction: discord.Interaction):
        self.selected_mode = interaction.data['values'][0]
        items = SERVER_OPTIONS[self.selected_server][self.selected_mode]
        self.item_select.options = [discord.SelectOption(label=item) for item in items]
        self.item_select.placeholder = "Wybierz itemy"
        self.item_select.disabled = False
        self.selected_items = []

        await interaction.response.edit_message(view=self)

    async def item_callback(self, interaction: discord.Interaction):
        self.selected_items = interaction.data['values']

        await interaction.response.send_message(
            f"Wybrałeś: Serwer: {self.selected_server}, Tryb: {self.selected_mode}, Itemy: {', '.join(self.selected_items)}",
            ephemeral=True
        )

        # Logowanie wyboru do kanału logów
        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            user = interaction.user
            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            log_message = (
                f"🛒 **Nowy zakup / wybór**\n"
                f"Użytkownik: {user} (ID: {user.id})\n"
                f"Czas: {now}\n"
                f"Serwer: {self.selected_server}\n"
                f"Tryb: {self.selected_mode}\n"
                f"Itemy: {', '.join(self.selected_items)}"
            )
            await log_channel.send(log_message)


class AdminPanelView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(label="Zamknij ten ticket", style=discord.ButtonStyle.red, custom_id="close_ticket"))
        self.add_item(Button(label="Lista ticketów", style=discord.ButtonStyle.green, custom_id="list_tickets"))

    @discord.ui.button(label="Zamknij ten ticket", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket_button(self, button: Button, interaction: discord.Interaction):
        channel = interaction.channel
        if channel.category_id == TICKET_CATEGORY_ID:
            await channel.delete()
        else:
            await interaction.response.send_message("Ta komenda działa tylko w kanałach ticketów.", ephemeral=True)

    @discord.ui.button(label="Lista ticketów", style=discord.ButtonStyle.green, custom_id="list_tickets")
    async def list_tickets_button(self, button: Button, interaction: discord.Interaction):
        category = interaction.guild.get_channel(TICKET_CATEGORY_ID)
        tickets = [ch for ch in category.channels]
        if tickets:
            msg = "Otwartych ticketów:\n" + "\n".join(f"- {t.mention}" for t in tickets)
        else:
            msg = "Brak otwartych ticketów."
        await interaction.response.send_message(msg, ephemeral=True)


bot.run(os.getenv("TOKEN"))
