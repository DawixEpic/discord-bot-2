import os
import discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")
print(f'TOKEN: "{TOKEN}"')  # DEBUG - sprawdzenie tokena
if not TOKEN:
    print("Token jest pusty! Sprawdź ustawienia zmiennych środowiskowych.")

GUILD_ID = 1373253103176122399  # <-- wpisz ID serwera jako int
CHANNEL_ID = 1373258480382771270
ROLE_ID = 1373275307150278686

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

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
    print(f"Zalogowano jako {bot.user}")
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        print("Nie znalazłem serwera o podanym ID!")
        return

    channel = guild.get_channel(CHANNEL_ID)
    if not channel:
        print("Nie znalazłem kanału o podanym ID!")
        return

    messages = await channel.history(limit=100).flatten()
    for msg in messages:
        await msg.delete()

    await channel.send(
        "**Kliknij przycisk poniżej, aby się zweryfikować i uzyskać dostęp do serwera.**",
        view=VerifyView()
    )

@bot.event
async def setup_hook():
    bot.add_view(VerifyView())

import os

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    print('Token jest pusty! Sprawdź ustawienia zmiennych środowiskowych.')
else:
    bot.run(TOKEN)

