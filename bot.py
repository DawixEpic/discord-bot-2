import discord
from discord.ext import commands
from discord.ui import View, Select, Button
import datetime

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

GUILD_ID = 1234567890
TICKET_CHANNEL_ID = 1234567890
LOG_CHANNEL_ID = 1234567890
REVIEW_CHANNEL_ID = 1375528888586731762

SERVER_OPTIONS = {
    "Survival": {
        "tryby": {
            "Easy": ["Kilof", "Miecz", "zbroja"],
            "Hard": ["Miecz+", "Zbroja+", "nie dostępne"]
        }
    },
    "SkyBlock": {
        "tryby": {
            "Classic": ["Kilof SB", "Miecz SB"],
            "OP": ["Zestaw OP", "nie dostępne"]
        }
    }
}

user_tickets = {}

class TicketView(View):
    def __init__(self, author: discord.Member):
        super().__init__(timeout=None)
        self.author = author
        self.server_select = Select(
            placeholder="Wybierz serwer",
            options=[discord.SelectOption(label=server) for server in SERVER_OPTIONS.keys()],
            custom_id="server_select"
        )
        self.server_select.callback = self.server_callback
        self.add_item(self.server_select)

    async def server_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author.id:
            return await interaction.response.send_message("To nie twój ticket.", ephemeral=True)

        server = self.server_select.values[0]
        modes = SERVER_OPTIONS[server]["tryby"].keys()

        self.clear_items()
        self.mode_select = Select(
            placeholder="Wybierz tryb",
            options=[discord.SelectOption(label=mode) for mode in modes],
            custom_id="mode_select"
        )
        self.mode_select.callback = self.mode_callback
        self.add_item(self.mode_select)
        await interaction.response.edit_message(content=f"Wybrałeś serwer: `{server}`. Teraz wybierz tryb:", view=self)

    async def mode_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author.id:
            return await interaction.response.send_message("To nie twój ticket.", ephemeral=True)

        server = self.server_select.values[0]
        mode = self.mode_select.values[0]
        items = SERVER_OPTIONS[server]["tryby"][mode]
        valid_items = [item for item in items if item.lower() != "nie dostępne"]

        if not valid_items:
            return await interaction.response.send_message("Brak dostępnych itemów w tym trybie.", ephemeral=True)

        self.clear_items()
        self.item_select = Select(
            placeholder="Wybierz itemy",
            options=[discord.SelectOption(label=item) for item in valid_items],
            custom_id="item_select",
            min_values=1,
            max_values=min(len(valid_items), 5)
        )
        self.item_select.callback = self.item_callback
        self.add_item(self.item_select)
        await interaction.response.edit_message(content=f"Wybrałeś tryb: `{mode}`. Teraz wybierz itemy:", view=self)

    async def item_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author.id:
            return await interaction.response.send_message("To nie twój ticket.", ephemeral=True)

        server = self.server_select.values[0]
        mode = self.mode_select.values[0]
        items = self.item_select.values
        order_summary = f"**Zamówienie:**\nSerwer: `{server}`\nTryb: `{mode}`\nItemy: {', '.join(f'`{item}`' for item in items)}"

        user_tickets[self.author.id]["zamówienie"] = order_summary

        self.clear_items()
        await interaction.response.edit_message(content=order_summary, view=None)

        # Logowanie zamówienia z przyciskiem "Zrealizuj"
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(title="Nowe zamówienie", description=order_summary, color=discord.Color.blue())
            embed.set_footer(text=f"Użytkownik: {self.author.display_name}")
            embed.timestamp = datetime.datetime.now()

            done_button = Button(label="Zrealizowane", style=discord.ButtonStyle.success, custom_id=f"done_{self.author.id}")
            done_view = View()
            done_view.add_item(done_button)

            await log_channel.send(embed=embed, view=done_view)

@bot.event
async def on_ready():
    print(f'Zalogowano jako {bot.user}!')

@bot.command()
async def ticket(ctx):
    if ctx.channel.id != TICKET_CHANNEL_ID:
        return

    if ctx.author.id in user_tickets:
        await ctx.send("Masz już otwarty ticket!", delete_after=5)
        return

    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False),
        ctx.author: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        ctx.guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
    }

    ticket_channel = await ctx.guild.create_text_channel(
        name=f"ticket-{ctx.author.name}",
        overwrites=overwrites,
        category=ctx.channel.category
    )

    user_tickets[ctx.author.id] = {
        "channel": ticket_channel.id,
        "zamówienie": None
    }

    view = TicketView(author=ctx.author)
    await ticket_channel.send(f"{ctx.author.mention}, wybierz serwer, tryb i itemy:", view=view)

@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type != discord.InteractionType.component:
        return

    if interaction.data["custom_id"].startswith("done_"):
        user_id = int(interaction.data["custom_id"].split("_")[1])
        ticket_data = user_tickets.get(user_id)

        if not ticket_data:
            return await interaction.response.send_message("Ticket nie został znaleziony.", ephemeral=True)

        order = ticket_data.get("zamówienie", "Brak danych")
        member = interaction.guild.get_member(user_id)

        # Usuń wiadomość z logów
        await interaction.message.delete()

        # Wyślij do kanału ocen
        review_channel = bot.get_channel(REVIEW_CHANNEL_ID)
        if review_channel and member:
            embed = discord.Embed(
                title="Oceń zamówienie",
                description=f"{order}\n\nKliknij, by ocenić (1-5 gwiazdek)",
                color=discord.Color.gold()
            )
            embed.set_footer(text=f"Użytkownik: {member.display_name}")
            embed.timestamp = datetime.datetime.now()

            rating_view = View()
            for i in range(1, 6):
                rating_view.add_item(Button(label="★" * i, style=discord.ButtonStyle.secondary, custom_id=f"rate_{user_id}_{i}"))

            await review_channel.send(embed=embed, view=rating_view)

        await interaction.response.send_message("Zamówienie oznaczone jako zrealizowane.", ephemeral=True)

    elif interaction.data["custom_id"].startswith("rate_"):
        _, user_id, rating = interaction.data["custom_id"].split("_")
        await interaction.response.send_message(f"Dziękujemy za ocenę: {rating}★!", ephemeral=True)

bot.run("TOKEN")
