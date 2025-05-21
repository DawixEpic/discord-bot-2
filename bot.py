import discord
from discord.ext import commands
from discord.ui import View, Select, Button
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

ROLE_ID = 1373275307150278686
TICKET_CATEGORY_ID = 1373277957446959135
LOG_CHANNEL_ID = 123456789012345678
TICKET_CHANNEL_ID = 1373305137228939416

verification_message_id = None
ticket_message_id = None

SERVER_OPTIONS = {
    "𝓑𝓪𝓲𝓮𝓳𝓸𝓲𝓮𝓻": {
        "𝓑𝓪𝓵𝓮𝓲": ["Elytra", "Buty flasha", "Miecz 6", "Shulker S2", "Shulker totemów", "1k$"],
        "𝓑𝓮𝓹𝓳𝓵": ["Set 25", "Miecz 25", "Kilof 25", "10k$"]
    },
    "𝒐𝒶𝓂𝒶𝓁𝓅𝒶": {
        "𝒒𝓇𝓎𝓛𝓂𝓅𝓁": ["Set anarchczny 2", "Set anarchiczny 1", "Miecze anarchcznye", "Excalibur", "Totem ułskawienia", "4,5k$", "50k$", "550k$"],
        "𝓑𝓮𝓹𝓳𝓵": ["Excalibur", "Totem ułskawienia", "Sakiewka", "50k$", "1mln"]
    },
    "𝒑𝓆𝓏𝓀": {
        "𝒒𝓇𝓎𝓛𝓂𝓅𝓁": ["nie dostępne", "nie dostępne", "nie dostępne"],
        "𝓑𝓮𝓹𝓳𝓵": ["Set 35", "Miecz 35", "Kilof 35", "10mld$", "50mld$", "100mld$"]
    },
    "𝓏𝓈𝓖𝓆": {
        "𝒒𝓇𝓎𝓛𝓂𝓅𝓁": ["Budda", "Love swap", "Klata meduzy"],
        "𝓑𝓮𝓹𝓳𝓵": ["nie dostępne", "nie dostępne", "nie dostępne"]
    }
}

class TicketData:
    def __init__(self):
        self.server = None
        self.mode = None
        self.items = []

user_ticket_data = {}

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
        ("🌀 Totem ulaskawienia", "170zł"),
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
            try:
                await log_channel.send(
                    f"📩 {interaction.user.mention} wybrał: **{self.selected_server}** / **{self.selected_mode}** / **{', '.join(self.selected_items)}**"
                )
            except Exception as e:
                print(f"Błąd podczas wysyłania loga: {e}")
        else:
            print("Nie znaleziono kanału logów lub brak dostępu.")


bot.run(os.getenv("TOKEN"))
