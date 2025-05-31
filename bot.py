import discord
from discord import app_commands
from discord.ext import commands
import os

# Ustawienia
VERIFICATION_ROLE_ID = 1373275307150278686  # <- podmień na ID roli weryfikacyjnej
VERIFICATION_CHANNEL_ID = 1373258480382771270  # <- podmień na ID kanału, gdzie ma się pojawić przycisk
GUILD_ID = 1373258480382771270  # <- podmień na ID Twojego serwera

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # wymagane do przyznawania ról

bot = commands.Bot(command_prefix="!", intents=intents)

# Klasa przycisku weryfikacyjnego
class VerifyButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # bez wygasania

    @discord.ui.button(label="✅ Zweryfikuj", style=discord.ButtonStyle.success, custom_id="verify_button")
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(VERIFICATION_ROLE_ID)
        if role in interaction.user.roles:
            await interaction.response.send_message("Już jesteś zweryfikowany!", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("Zostałeś pomyślnie zweryfikowany!", ephemeral=True)

# Slash komenda do wysyłania przycisku weryfikacyjnego
@bot.tree.command(name="weryfikacja", description="Wyślij panel weryfikacji z przyciskiem", guild=discord.Object(id=GUILD_ID))
@app_commands.checks.has_permissions(administrator=True)
async def send_verification_panel(interaction: discord.Interaction):
    embed = discord.Embed(
        title="✅ Weryfikacja",
        description="Kliknij przycisk poniżej, aby się zweryfikować i uzyskać dostęp do serwera.",
        color=discord.Color.green()
    )
    view = VerifyButton()
    await interaction.response.send_message(embed=embed, view=view)

# Event po uruchomieniu
@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user} (ID: {bot.user.id})")
    try:
        guild = discord.Object(id=GUILD_ID)
        synced = await bot.tree.sync(guild=guild)
        print(f"Zsynchronizowano {len(synced)} komend slash dla serwera {GUILD_ID}.")
    except Exception as e:
        print(f"Błąd synchronizacji komend: {e}")
    # Dodanie persistent view przy starcie
    bot.add_view(VerifyButton())

# Obsługa błędów komend
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    await interaction.response.send_message(f"Wystąpił błąd: {error}", ephemeral=True)

# Uruchomienie
TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN is None:
    raise ValueError("Brak tokenu! Ustaw DISCORD_TOKEN w zmiennych środowiskowych.")

if __name__ == "__main__":
    bot.run(TOKEN)
