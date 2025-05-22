import discord
from discord.ext import commands
from discord.ui import View, Select, Button
from datetime import datetime

intents = discord.Intents.all()
bot = discord.Bot(intents=intents)

GUILD_ID = 123456789012345678
TICKET_CATEGORY_ID = 123456789012345678
SUPPORT_ROLE_ID = 123456789012345678
LOG_CHANNEL_ID = 123456789012345678

SERVER_OPTIONS = {
    "Serwer A": {
        "Tryb 1": ["Item 1", "Item 2"],
        "Tryb 2": ["Item 3", "Item 4"]
    },
    "Serwer B": {
        "Tryb 3": ["Item 5", "Item 6"]
    }
}


class MenuView(View):
    def __init__(self):
        super().__init__(timeout=None)

        self.server_select = Select(
            placeholder="Wybierz serwer",
            options=[discord.SelectOption(label=server) for server in SERVER_OPTIONS]
        )
        self.server_select.callback = self.server_callback
        self.add_item(self.server_select)

        self.mode_select = Select(placeholder="Wybierz tryb", options=[], disabled=True)
        self.mode_select.callback = self.mode_callback
        self.add_item(self.mode_select)

        self.item_select = Select(placeholder="Wybierz item", options=[], disabled=True)
        self.item_select.callback = self.item_callback
        self.add_item(self.item_select)

    async def server_callback(self, interaction: discord.Interaction):
        server = self.server_select.values[0]
        self.mode_select.options = [discord.SelectOption(label=mode) for mode in SERVER_OPTIONS[server]]
        self.mode_select.disabled = False
        self.item_select.options = []
        self.item_select.disabled = True
        await interaction.response.edit_message(view=self)

    async def mode_callback(self, interaction: discord.Interaction):
        server = self.server_select.values[0]
        mode = self.mode_select.values[0]
        self.item_select.options = [discord.SelectOption(label=item) for item in SERVER_OPTIONS[server][mode]]
        self.item_select.disabled = False
        await interaction.response.edit_message(view=self)

    async def item_callback(self, interaction: discord.Interaction):
        server = self.server_select.values[0]
        mode = self.mode_select.values[0]
        item = self.item_select.values[0]

        await interaction.response.send_message(f"🎮 `{server}` → 🕹️ `{mode}` → 📦 `{item}`", ephemeral=True)

        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(title="📝 Wybór w tickecie", color=discord.Color.green())
            embed.add_field(name="Użytkownik", value=interaction.user.mention, inline=False)
            embed.add_field(name="Serwer", value=server)
            embed.add_field(name="Tryb", value=mode)
            embed.add_field(name="Item", value=item)
            embed.timestamp = datetime.now()
            await log_channel.send(embed=embed)


@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user}")


@bot.slash_command(name="ticket", description="Utwórz nowy ticket")
async def ticket(ctx: discord.ApplicationContext):
    guild = ctx.guild
    category = discord.utils.get(guild.categories, id=TICKET_CATEGORY_ID)

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        guild.get_role(SUPPORT_ROLE_ID): discord.PermissionOverwrite(read_messages=True, send_messages=True),
    }

    ticket_channel = await guild.create_text_channel(f"ticket-{ctx.author.name}", overwrites=overwrites, category=category)

    await ticket_channel.send(f"{ctx.author.mention}, dziękujemy za utworzenie ticketa!", view=MenuView())

    close_btn = Button(label="Zamknij ticket", style=discord.ButtonStyle.danger)

    async def close_callback(interaction: discord.Interaction):
        await ticket_channel.delete()_
