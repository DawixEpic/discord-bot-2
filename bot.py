import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# 🔧 KONFIGURACJA:
GUILD_ID = 1373253103176122399
ROLE_ID = 1373275307150278686
VERIFY_CHANNEL_ID = 1373258480382771270
TICKET_CHANNEL_ID = 1373305137228939416
TICKET_CATEGORY_ID = 1373277957446959135

# 🌟 WERYFIKACJA
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

# 🎫 TICKETY
class TicketButton(discord.ui.View):
    @discord.ui.button(label="🎫 Utwórz ticket", style=discord.ButtonStyle.primary, custom_id="create_ticket")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        existing = discord.utils.get(guild.text_channels, name=f"ticket-{interaction.user.name.lower().replace(' ', '-')}")
        if existing:
            await interaction.response.send_message("🛑 Masz już otwarty ticket!", ephemeral=True)
            return

        category = guild.get_channel(TICKET_CATEGORY_ID)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True)
        }

        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            overwrites=overwrites,
            category=category,
            reason="Nowy ticket"
        )

        await ticket_channel.send(f"{interaction.user.mention} 🎫 Ticket został utworzony. Napisz, w czym możemy pomóc!")
        await interaction.response.send_message("✅ Ticket utworzony!", ephemeral=True)

# 🚀 BOT START
@bot.event
async def on_ready():
    print(f"✅ Zalogowano jako {bot.user}")
    guild = bot.get_guild(GUILD_ID)

    # Weryfikacja
    verify_channel = guild.get_channel(VERIFY_CHANNEL_ID)
    if verify_channel:
        embed = discord.Embed(
            title="🔒 Weryfikacja",
            description="Kliknij przycisk, aby się zweryfikować i otrzymać dostęp do serwera.",
            color=discord.Color.green()
        )
        await verify_channel.send(embed=embed, view=WeryfikacjaButton())

    # Ticket
    ticket_channel = guild.get_channel(TICKET_CHANNEL_ID)
    if ticket_channel:
        embed = discord.Embed(
            title="🎫 Centrum Pomocy",
            description="Kliknij przycisk poniżej, aby utworzyć ticket i skontaktować się z administracją.",
            color=discord.Color.blue()
        )
        await ticket_channel.send(embed=embed, view=TicketButton())

bot.run(os.getenv("DISCORD_TOKEN"))
