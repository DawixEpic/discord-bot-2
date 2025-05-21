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

verification_message_id = None
ticket_message_id = None

SERVER_OPTIONS = {
    "𝐂𝐑𝐀𝐅𝐓𝐏𝐋𝐀𝐘": {
        "𝐆𝐈𝐋𝐃𝐈𝐄": ["Elytra", "Buty flasha", "Miecz 6", "Shulker S2", "Shulker totemów", "1k$"],
        "𝐁𝐎𝐗𝐏𝐕𝐏": ["Set 25", "Miecz 25", "Kilof 25", "10k$"]
    },
    "𝐀𝐍𝐀𝐑𝐂𝐇𝐈𝐀": {
        "𝐋𝐈𝐅𝐄𝐒𝐓𝐄𝐀𝐋": ["Set anarchczny 2", "Set anarchiczny 1", "Miecze anarchcznye", "Excalibur", "Totem ułskawienia", "4,5k$", "50k$", "550k$"],
        "𝐁𝐎𝐗𝐏𝐕𝐏": ["Excalibur", "Totem ułaskawienia", "Sakiewka", "50k$", "1mln"]
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

OFFER_DATA = {
    1373273108093337640: [
        ("💸 10mld$", "1zł"),
        ("🗡️ Miecz 35", "40zł"),
        ("🛡️ Set 35", "57zł"),
    ],
    1373270295556788285: [
        ("💵 50k$", "1zł"),
        ("💰 1mln$", "15zł"),
        ("🎉 EVENTOWKI:", ""),
        ("⚔️ Excalibur", "270zł"),
        ("🌀 Totem ułaskawienia", "80zł"),
        ("🎒 Sakiewka", "20zł"),
    ],
    1373268875407396914: [
        ("💸 4,5k$", "1zł"),
        ("💸 50k$", "15zł"),
        ("💸 550k$", "130zł"),
        ("🛡️ Anarchiczny set 2", "28zł"),
        ("🛡️ Anarchiczny set 1", "9zł"),
        ("⚔️ MIECZE:", ""),
        ("🗡️ Anarchiczny miecz", "3zł"),
        ("🎉 EVENTÓWKI:", ""),
        ("🐰 Zajęczy miecz", "65zł"),
        ("🌀 Totem ułaskawienia", "170zł"),
        ("🪙 Excalibur", "360zł"),
    ],
    1373267159576481842: [
        ("🛡️ Set 25", "30zł"),
        ("🗡️ Miecz 25", "25zł"),
        ("⛏️ Kilof 25", "10zł"),
        ("💰 1mln$", "18zł"),
    ],
    1373266589310517338: [
        ("🪽 Elytra", "12zł"),
        ("👟 Buty flasha", "5zł"),
        ("🗡️ Miecz 6", "3zł"),
        ("💵 1k$", "1zł"),
        ("📦 Shulker s2", "7zł"),
        ("📦 Shulker totemów", "6zł"),
    ],
    1374380939970347019: [
        ("💸 15k$", "1zł"),
        ("🌟 Budda", "30zł"),
        ("💖 Love swap", "100zł"),
        ("🐉 Klata meduzy", "140zł"),
    ],
}


@bot.event
async def on_ready():
    print(f"✅ Zalogowano jako {bot.user}")


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
            print(f"❌ Błąd podczas wysyłania oferty na kanał {channel_id}: {e}")

    await ctx.send("✅ Oferty zostały wysłane na wszystkie kanały.")


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

        # Usunięto czyszczenie reakcji, aby reakcja nie znikała

    elif payload.message_id == ticket_message_id and str(payload.emoji) == "🎟️":
        category = guild.get_channel(TICKET_CATEGORY_ID)
        if not isinstance(category, discord.CategoryChannel):
            return

        # Usunięto czyszczenie reakcji, aby reakcja nie znikała

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

        # Automatyczne zamknięcie po 1h
        await asyncio.sleep(3600)
        if ticket_channel and ticket_channel in guild.text_channels:
            await ticket_channel.delete(reason="Automatyczne zamknięcie ticketu po 1 godzinie")


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

        await interaction.response.edit_message(content=None, view=self)

    async def mode_callback(self, interaction: discord.Interaction):
        self.selected_mode = interaction.data['values'][0]
        self.selected_items = []

        items = SERVER_OPTIONS[self.selected_server][self.selected_mode]
        self.item_select = Select(
            placeholder="Wybierz item(y) (możesz zaznaczyć wiele)",
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

        await interaction.response.edit_message(content=None, view=self)

    async def item_callback(self, interaction: discord.Interaction):
        self.selected_items = interaction.data['values']

        summary = (
            f"**Serwer:** `{self.selected_server}`\n"
            f"**Tryb:** `{self.selected_mode}`\n"
            f"**Wybrane itemy:** {', '.join(self.selected_items)}"
        )

        await interaction.response.edit_message(content=summary, view=self)

        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = (
                f"📋 Nowy wybór ticketu\n"
                f"Użytkownik: {interaction.user.name} ({interaction.user.id})\n"
                f"Serwer: {self.selected_server}\n"
                f"Tryb: {self.selected_mode}\n"
                f"Itemy: {', '.join(self.selected_items)}\n"
                f"Czas: {time_str}"
            )
            await log_channel.send(message)


class AdminPanelView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(label="Zamknij ten ticket", style=discord.ButtonStyle.danger, custom_id="close_ticket"))
        self.add_item(Button(label="Pokaż listę ticketów", style=discord.ButtonStyle.primary, custom_id="list_tickets"))

    @discord.ui.button(label="Zamknij ten ticket", style=discord.ButtonStyle.danger, custom_id="close_ticket")
    async def close_ticket_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        # Tylko admin z uprawnieniem manage_channels może użyć
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ Nie masz uprawnień do zamykania ticketów.", ephemeral=True)
            return

        # Zamknięcie (usuniecie) kanału ticketu
        if interaction.channel.category and interaction.channel.category.id == TICKET_CATEGORY_ID:
            await interaction.response.send_message("✅ Zamykam ticket...", ephemeral=True)
            await interaction.channel.delete(reason=f"Ticket zamknięty przez {interaction.user}")
        else:
            await interaction.response.send_message("❌ Ta komenda działa tylko w kanale ticketu.", ephemeral=True)

    @discord.ui.button(label="Pokaż listę ticketów", style=discord.ButtonStyle.primary, custom_id="list_tickets")
    async def list_tickets_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        # Tylko admin z uprawnieniem manage_channels może użyć
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ Nie masz uprawnień do zarządzania ticketami.", ephemeral=True)
            return

        guild = interaction.guild
        category = guild.get_channel(TICKET_CATEGORY_ID)
        if not category:
            await interaction.response.send_message("❌ Kategoria ticketów nie została znaleziona.", ephemeral=True)
            return

        tickets = [ch for ch in category.channels if isinstance(ch, discord.TextChannel)]
        if not tickets:
            await interaction.response.send_message("✅ Brak otwartych ticketów.", ephemeral=True)
            return

        description = "\n".join(f"- {ch.name} (ID: {ch.id})" for ch in tickets)
        embed = discord.Embed(title="Lista otwartych ticketów", description=description, color=discord.Color.blue())

        await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.command()
@commands.has_permissions(administrator=True)
async def panel(ctx):
    """Wyświetla panel admina do zarządzania ticketami."""
    embed = discord.Embed(
        title="Panel administracyjny ticketów",
        description="Użyj przycisków poniżej aby zarządzać ticketami.\n\n"
                    "- Zamknij ten ticket (usuwa kanał, działa w kanale ticketu)\n"
                    "- Pokaż listę ticketów (lista otwartych kanałów ticketów)",
        color=discord.Color.red()
    )
    view = AdminPanelView()
    await ctx.send(embed=embed, view=view)

bot.run(os.getenv('TOKEN'))
