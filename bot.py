import discord
from discord.ext import commands
from discord.ui import View, Select, Button

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

SERVER_OPTIONS = {
    "Server1": {
        "Mode1": ["Item1", "Item2"],
        "Mode2": ["Item3"]
    },
    "Server2": {
        "ModeA": ["ItemA", "ItemB"],
        "ModeB": ["ItemC"]
    }
}

class TicketMenu(View):
    def __init__(self):
        super().__init__(timeout=None)

        self.server_select = Select(
            placeholder="Wybierz serwer",
            options=[discord.SelectOption(label=key) for key in SERVER_OPTIONS.keys()]
        )
        self.server_select.callback = self.server_selected

        self.mode_select = Select(
            placeholder="Wybierz tryb",
            options=[],
            disabled=True
        )
        self.mode_select.callback = self.mode_selected

        self.item_select = Select(
            placeholder="Wybierz itemy",
            options=[],
            disabled=True
        )
        self.item_select.callback = self.item_selected

        self.close_button = Button(label="Zamknij ticket", style=discord.ButtonStyle.danger)
        self.close_button.callback = self.close_ticket

        # Dodajemy komponenty w kolejności: selecty, potem przycisk
        self.add_item(self.server_select)
        self.add_item(self.mode_select)
        self.add_item(self.item_select)
        self.add_item(self.close_button)

    async def server_selected(self, interaction: discord.Interaction):
        server = self.server_select.values[0]
        modes = SERVER_OPTIONS.get(server, {})
        self.mode_select.options = [discord.SelectOption(label=mode) for mode in modes.keys()]
        self.mode_select.disabled = False
        self.item_select.options = []
        self.item_select.disabled = True
        await interaction.response.edit_message(view=self)

    async def mode_selected(self, interaction: discord.Interaction):
        server = self.server_select.values[0]
        mode = self.mode_select.values[0]
        items = SERVER_OPTIONS.get(server, {}).get(mode, [])
        self.item_select.options = [discord.SelectOption(label=item) for item in items]
        self.item_select.disabled = False
        await interaction.response.edit_message(view=self)

    async def item_selected(self, interaction: discord.Interaction):
        selected_items = ", ".join(self.item_select.values)
        await interaction.response.send_message(f"Wybrałeś: {selected_items}", ephemeral=True)

    async def close_ticket(self, interaction: discord.Interaction):
        await interaction.response.send_message("Ticket zostanie zamknięty...", ephemeral=True)
        # Tutaj można dodać logikę usuwania kanału lub innego zamykania


@bot.command()
async def ticket(ctx):
    await ctx.send("Wybierz opcje:", view=TicketMenu())


bot.run("YOUR_BOT_TOKEN")
