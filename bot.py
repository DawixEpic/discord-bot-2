import discord
from discord.ext import commands
from discord.ui import View, Select, Button
import datetime

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

SERVER_OPTIONS = {
    "Serwer1": {
        "Tryb1": ["Item1", "Item2"],
        "Tryb2": ["Item3"]
    },
    "Serwer2": {
        "TrybA": ["ItemA", "ItemB"],
        "TrybB": ["ItemC"]
    }
}

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.server_select = discord.ui.Select(
            placeholder="Wybierz serwer",
            options=[discord.SelectOption(label=server) for server in SERVER_OPTIONS]
        )
        self.server_select.callback = self.server_selected
        self.add_item(self.server_select)

        self.mode_select = discord.ui.Select(
            placeholder="Wybierz tryb",
            options=[],
            disabled=True
        )
        self.mode_select.callback = self.mode_selected
        self.add_item(self.mode_select)

        self.item_select = discord.ui.Select(
            placeholder="Wybierz itemy",
            options=[],
            disabled=True,
            min_values=1,
            max_values=5
        )
        self.item_select.callback = self.item_selected
        self.add_item(self.item_select)

        self.close_button = Button(label="Zamknij ticket", style=discord.ButtonStyle.danger)
        self.close_button.callback = self.close_ticket
        # UWAGA: przycisk dodamy DOPIERO po wybraniu itemów

        # Pamięć wyborów
        self.selected_server = None
        self.selected_mode = None
        self.selected_items = []

    async def server_selected(self, interaction: discord.Interaction):
        self.selected_server = self.server_select.values[0]
        modes = SERVER_OPTIONS[self.selected_server].keys()

        self.mode_select.options = [discord.SelectOption(label=mode) for mode in modes]
        self.mode_select.disabled = False

        self.item_select.options = []
        self.item_select.disabled = True

        await interaction.response.edit_message(view=self)

    async def mode_selected(self, interaction: discord.Interaction):
        self.selected_mode = self.mode_select.values[0]
        items = SERVER_OPTIONS[self.selected_server][self.selected_mode]

        self.item_select.options = [discord.SelectOption(label=item) for item in items]
        self.item_select.disabled = False

        await interaction.response.edit_message(view=self)

    async def item_selected(self, interaction: discord.Interaction):
        self.selected_items = self.item_select.values

        if self.close_button not in self.children:
            self.add_item(self.close_button)

        await interaction.response.edit_message(view=self)

    async def close_ticket(self, interaction: discord.Interaction):
        nick = interaction.user.name
        data = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        co = ', '.join(self.selected_items)

        embed = discord.Embed(title="Zamówienie zakończone", color=discord.Color.green())
        embed.add_field(name="Nick", value=nick, inline=False)
        embed.add_field(name="Data", value=data, inline=False)
        embed.add_field(name="Zamówienie", value=co, inline=False)

        channel = bot.get_channel(1375528888586731762)
        if channel:
            await channel.send(embed=embed)

        await interaction.response.send_message("Zamknięto ticket. Dziękujemy!", ephemeral=True)


@bot.command()
async def ticket(ctx):
    await ctx.send("Rozpocznij zamówienie:", view=TicketView())


bot.run("YOUR_BOT_TOKEN")
