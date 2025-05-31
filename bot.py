import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

GUILD_ID = 123456789012345678  # ← ID Twojego serwera
ROLE_ID = 987654321098765432   # ← ID roli do nadania
CHANNEL_ID = 112233445566778899  # ← ID kanału, gdzie bot ma wysłać przycisk

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
    print(f"✅ Zalogowano jako {bot.user}")
    guild = bot.get_guild(GUILD_ID)
    channel = guild.get_channel(CHANNEL_ID)

    if channel:
        embed = discord.Embed(
            title="🔒 Weryfikacja",
            description="Kliknij przycisk poniżej, aby się zweryfikować i otrzymać dostęp do serwera.",
            color=discord.Color.green()
        )
        await channel.send(embed=embed, view=WeryfikacjaButton())
    else:
        print("❌ Nie znaleziono kanału!")

bot.run(os.getenv("DISCORD_TOKEN"))
