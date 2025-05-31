import discord
from discord.ext import commands
from discord import app_commands

intents = discord.Intents.default()
intents.members = True  # potrzebne do nadawania ról

bot = commands.Bot(command_prefix="!", intents=intents)

GUILD_ID = 1373253103176122399  # ← wpisz ID swojego serwera
ROLE_ID = 1373275307150278686   # ← wpisz ID roli weryfikacyjnej

class WeryfikacjaButton(discord.ui.View):
    @discord.ui.button(label="Zweryfikuj się ✅", style=discord.ButtonStyle.success, custom_id="verify_button")
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(ROLE_ID)
        if role in interaction.user.roles:
            await interaction.response.send_message("🔔 Już masz tę rolę!", ephemeral=True)
        else:
            try:
                await interaction.user.add_roles(role)
                await interaction.response.send_message("✅ Zostałeś zweryfikowany! Rola została nadana.", ephemeral=True)
            except discord.Forbidden:
                await interaction.response.send_message("❌ Nie mam uprawnień, aby nadać Ci rolę.", ephemeral=True)

@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user}")
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"Zsynchronizowano {len(synced)} komend.")
    except Exception as e:
        print(f"Błąd synchronizacji komend: {e}")

@bot.tree.command(name="weryfikacja", description="Wysyła wiadomość z przyciskiem do weryfikacji", guild=discord.Object(id=GUILD_ID))
async def weryfikacja(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🔒 Weryfikacja",
        description="Kliknij przycisk poniżej, aby się zweryfikować i otrzymać dostęp.",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed, view=WeryfikacjaButton())

import os
bot.run(os.getenv("DISCORD_TOKEN"))
