import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.members = True  # potrzebne do nadawania roli
intents.message_content = True  # do czytania treści wiadomości (do purge)

bot = commands.Bot(command_prefix="!", intents=intents)

ROLE_ID = 1373275307150278686  # <-- podmień na ID roli "Zweryfikowany"
CHANNEL_ID = 1373258480382771270  # kanał, gdzie wysyłamy embed z przyciskiem

class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # brak timeoutu

    @discord.ui.button(label="Weryfikuj", style=discord.ButtonStyle.green, custom_id="verify_button")
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(ROLE_ID)
        if role is None:
            await interaction.response.send_message("Nie mogę znaleźć roli do weryfikacji.", ephemeral=True)
            return
        if role in interaction.user.roles:
            await interaction.response.send_message("Już jesteś zweryfikowany!", ephemeral=True)
            return
        try:
            await interaction.user.add_roles(role, reason="Weryfikacja przez przycisk")
            await interaction.response.send_message("Pomyślnie zweryfikowano!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Błąd przy nadawaniu roli: {e}", ephemeral=True)

@bot.event
async def on_ready():
    print(f'Zalogowano jako {bot.user}!')

    try:
        channel = await bot.fetch_channel(CHANNEL_ID)
    except Exception as e:
        print(f"Nie udało się pobrać kanału: {e}")
        return

    perms = channel.permissions_for(channel.guild.me)
    if not (perms.read_messages and perms.send_messages and perms.manage_messages):
        print("Bot nie ma wymaganych uprawnień na kanale!")
        return

    try:
        deleted = await channel.purge(limit=100, check=lambda m: m.author == bot.user)
        print(f"Usunięto {len(deleted)} wiadomości bota na kanale {channel.name}")
    except Exception as e:
        print(f"Błąd usuwania wiadomości: {e}")

    embed = discord.Embed(
        title="Weryfikacja",
        description="Kliknij przycisk, aby się zweryfikować i uzyskać dostęp do serwera.",
        color=discord.Color.blue()
    )
    view = VerifyView()
    try:
        await channel.send(embed=embed, view=view)
        print(f"Wysłano wiadomość z przyciskiem na kanał {channel.name}")
    except Exception as e:
        print(f"Błąd przy wysyłaniu wiadomości: {e}")

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

TOKEN = os.getenv("DISCORD_BOT_TOKEN")  # na Railway ustaw zmienną środowiskową DISCORD_BOT_TOKEN

if not TOKEN:
    print("Nie ustawiono tokena bota w zmiennych środowiskowych!")
else:
    bot.run(TOKEN)
