import discord
from discord.ext import commands
from discord.ui import View, Select

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

SERVER_OPTIONS = {
    "Survival": {
        "Classic": ["Diamenty", "Zbroje"],
        "Hardcore": ["Totemy", "Jabłka"]
    }
}

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.server_select = Select(
            placeholder="Wybierz serwer",
            options=[discord.SelectOption(label=s) for s in SERVER_OPTIONS]
        )
        self.server_select.callback = self.server_callback
        self.add_item(self.server_select)

    async def server_callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Wybrałeś: {self.server_select.values[0]}", ephemeral=True)

@bot.event
async def on_ready():
    bot.add_view(TicketView())  # GLOBALNY VIEW
    print(f"Zalogowano jako {bot.user}")

@bot.command()
async def test(ctx):
    await ctx.send("Wybierz serwer:", view=TicketView())

bot.run("TWÓJ_TOKEN_BOTA")
