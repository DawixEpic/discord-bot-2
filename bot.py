import discord
from discord.ext import commands
import asyncio
import os

TOKEN = 'TWÓJ_TOKEN_BOTA'
CHANNEL_ID = 1373258480382771270
ROLE_ID = 1373275307150278686

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)


class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="✅ Zweryfikuj się", style=discord.ButtonStyle.success, custom_id="verify_button")
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(ROLE_ID)
        if role in interaction.user.roles:
            await interaction.response.send_message("Masz już tę rolę!", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("✅ Została Ci nadana rola!", ephemeral=True)


@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user}!")

    channel = bot.get_channel(CHANNEL_ID)

    # Usuwanie starych wiadomości
    try:
        messages = await channel.history(limit=100).flatten()
        for msg in messages:
            await msg.delete()
    except Exception as e:
        print("Błąd przy usuwaniu wiadomości:", e)

    # Wysyłanie nowej wiadomości z przyciskiem
    view = VerifyView()
    await channel.send(
        "**Kliknij przycisk poniżej, aby się zweryfikować i uzyskać dostęp do serwera.**",
        view=view
    )

# Zarejestruj View przy starcie bota, żeby przycisk działał po restarcie
@bot.event
async def setup_hook():
    bot.add_view(VerifyView())

bot.run(TOKEN)
