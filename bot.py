import discord
from discord import app_commands
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.members = True  # potrzebne do nadawania ról
intents.message_content = True  # potrzebne do usuwania wiadomości (opcjonalnie)

bot = commands.Bot(command_prefix="!", intents=intents)

ROLE_ID = 123456789012345678  # <-- zmień na ID swojej roli "Zweryfikowany"
CHANNEL_ID = 1373258480382771270  # kanał do wysłania wiadomości

@bot.event
async def on_ready():
    print(f'Zalogowano jako {bot.user}!')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} komend slash.')
    except Exception as e:
        print(f'Błąd sync komend: {e}')

    # Pobierz kanał
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        print(f"Nie mogę znaleźć kanału o ID {CHANNEL_ID}")
        return

    # Usuń poprzednie wiadomości bota na tym kanale
    def is_bot(m):
        return m.author == bot.user

    deleted = await channel.purge(limit=100, check=is_bot)
    print(f"Usunięto {len(deleted)} wiadomości bota na kanale {channel.name}")

    # Stwórz i wyślij embed z przyciskiem
    embed = discord.Embed(
        title="Weryfikacja",
        description="Kliknij przycisk poniżej, aby się zweryfikować i uzyskać dostęp do serwera.",
        color=discord.Color.blue()
    )
    view = VerifyView()
    await channel.send(embed=embed, view=view)
    print(f"Wysłano wiadomość z przyciskiem na kanał {channel.name}")

class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # brak timeoutu

    @discord.ui.button(label="Weryfikuj", style=discord.ButtonStyle.green, custom_id="verify_button")
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(ROLE_ID)
        if role is None:
            await interaction.response.send_message("Nie mogę znaleźć roli weryfikacji.", ephemeral=True)
            return
        if role in interaction.user.roles:
            await interaction.response.send_message("Już jesteś zweryfikowany!", ephemeral=True)
            return
        try:
            await interaction.user.add_roles(role, reason="Weryfikacja przez przycisk")
            await interaction.response.send_message("Pomyślnie zweryfikowano!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Błąd przy nadawaniu roli: {e}", ephemeral=True)

@bot.tree.command(name="verifybutton", description="Wyślij embed z przyciskiem weryfikacji w tym kanale")
async def verifybutton(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Weryfikacja",
        description="Kliknij przycisk poniżej, aby się zweryfikować i uzyskać dostęp do serwera.",
        color=discord.Color.blue()
    )
    view = VerifyView()
    await interaction.channel.send(embed=embed, view=view)
    await interaction.response.send_message("Wiadomość z przyciskiem wysłana.", ephemeral=True)

# Token bota z zmiennej środowiskowej (polecane na Railway)
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

if not TOKEN:
    print("Nie ustawiono tokena bota w zmiennych środowiskowych!")
else:
    bot.run(TOKEN)
