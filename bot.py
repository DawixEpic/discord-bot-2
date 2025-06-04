import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

ROLE_ID = 1373275307150278686  # ZMIEŃ NA PRAWDZIWE ID ROLI
CHANNEL_ID = 1373258480382771270  # ZMIEŃ NA ID KANAŁU WERYFIKACJI

class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="✅ Weryfikuj", style=discord.ButtonStyle.green, custom_id="verify_button")
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(ROLE_ID)
        if not role:
            await interaction.response.send_message("❌ Rola do weryfikacji nie została znaleziona.", ephemeral=True)
            return

        if role in interaction.user.roles:
            await interaction.response.send_message("✅ Już jesteś zweryfikowany!", ephemeral=True)
            return

        try:
            await interaction.user.add_roles(role, reason="Weryfikacja przez przycisk")
            await interaction.response.send_message("✅ Zweryfikowano pomyślnie!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Błąd przy nadawaniu roli: {e}", ephemeral=True)

@bot.event
async def setup_hook():
    await bot.tree.sync()

@bot.event
async def on_ready():
    print(f"✅ Zalogowano jako {bot.user} ({bot.user.id})")

    try:
        channel = await bot.fetch_channel(CHANNEL_ID)
        print(f"📡 Znaleziono kanał: {channel.name} ({channel.id})")
    except Exception as e:
        print(f"❌ Nie można pobrać kanału: {e}")
        return

    perms = channel.permissions_for(channel.guild.me)
    if not (perms.read_messages and perms.send_messages and perms.manage_messages):
        print("❌ Bot nie ma wymaganych uprawnień na tym kanale!")
        return

    try:
        deleted = await channel.purge(limit=100, check=lambda m: m.author == bot.user)
        print(f"🧹 Usunięto {len(deleted)} starych wiadomości bota.")
    except Exception as e:
        print(f"❌ Błąd przy usuwaniu wiadomości: {e}")

    embed = discord.Embed(
        title="🔒 Weryfikacja",
        description="Kliknij przycisk poniżej, aby się zweryfikować i uzyskać dostęp do serwera.",
        color=discord.Color.green()
    )

    try:
        await channel.send(embed=embed, view=VerifyView())
        print("✅ Wiadomość z przyciskiem została wysłana.")
    except Exception as e:
        print(f"❌ Błąd przy wysyłaniu wiadomości: {e}")

@bot.tree.command(name="verifybutton", description="Wyślij embed weryfikacyjny z przyciskiem")
async def verifybutton(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🔒 Weryfikacja",
        description="Kliknij przycisk poniżej, aby się zweryfikować i uzyskać dostęp do serwera.",
        color=discord.Color.green()
    )
    await interaction.channel.send(embed=embed, view=VerifyView())
    await interaction.response.send_message("✅ Wysłano wiadomość z przyciskiem.", ephemeral=True)

# Uruchomienie bota
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not TOKEN:
    print("❌ Nie ustawiono tokena bota (zmienna środowiskowa DISCORD_BOT_TOKEN)")
else:
    bot.run(TOKEN)
