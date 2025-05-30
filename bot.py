import discord
from discord import app_commands

TOKEN = "TWÓJ_TOKEN_TUTAJ"  # Zamień na swój token bota
GUILD_ID = 1373253103176122399  # Zamień na ID swojego serwera (liczba, bez cudzysłowów)

class MyClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        guild = discord.Object(id=GUILD_ID)
        await self.tree.sync(guild=guild)
        print(f"Slash commands zarejestrowane dla serwera {GUILD_ID}")

client = MyClient()

@client.tree.command(name="ping", description="Odpowiada pongiem")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")

if __name__ == "__main__":
    client.run(TOKEN)
