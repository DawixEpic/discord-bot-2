import discord
from discord.ext import commands
from discord.ui import View, Select
import os

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

TICKET_CATEGORY_ID = 1373277957446959135  # Zmień na swoje
SUPPORT_ROLE_ID = 1373275898375176232     # Zmień na swoje
LOG_CHANNEL_ID = 1374479815914291240      # Zmień na swoje

SERVER_OPTIONS = {
    "Serwer A": {
        "Tryb 1": ["Item 1", "Item 2"],
        "Tryb 2": ["Item 3"]
    },
    "Serwer B": {
        "Tryb 3": ["Item 4", "Item 5"]
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

    async def server_callback(self, interaction: discord.Interaction):
        selected_server = self.server_select.values[0]
        await interaction.response.send_message(f"Wybrano serwer: {selected_server}", ephemeral=True)

@bot.command()
async def test(ctx):
    category = discord.utils.get(ctx.guild.categories, id=TICKET_CATEGORY_ID)

    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        ctx.author: discord.PermissionOverwrite(read_messages=True),
        ctx.guild.get_role(SUPPORT_ROLE_ID): discord.PermissionOverwrite(read_messages=True),
    }

    channel = await ctx.guild.create_text_channel(f"ticket-{ctx.author.name}", category=category, overwrites=overwrites)
    await channel.send("🎫 Ticket utworzony! Wybierz serwer:", view=MenuView())

bot.run("TWÓJ_TOKEN_BOTA")
