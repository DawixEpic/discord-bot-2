import discord
from discord.ext import commands
from discord.ui import Select, View

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

ROLE_ID = 1373275307150278686
TICKET_CATEGORY_ID = 1373277957446959135

verification_message_id = None

@bot.event
async def on_ready():
    print(f"✅ Zalogowano jako {bot.user}")

@bot.command()
@commands.has_permissions(administrator=True)
async def weryfikacja(ctx):
    embed = discord.Embed(
        title="✅ Weryfikacja",
        description="Kliknij ✅ aby się zweryfikować i dostać dostęp.",
        color=discord.Color.green()
    )
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("✅")

    global verification_message_id
    verification_message_id = msg.id
    await ctx.send("✅ Wiadomość weryfikacyjna została wysłana.")

@bot.command()
@commands.has_permissions(administrator=True)
async def ticket(ctx):
    class PurchaseSelect(Select):
        def __init__(self):
            options = [
                discord.SelectOption(label="Item 1", description="Kup Item 1"),
                discord.SelectOption(label="Item 2", description="Kup Item 2"),
                discord.SelectOption(label="Item 3", description="Kup Item 3"),
            ]
            super().__init__(placeholder="Wybierz przedmiot do zakupu...", options=options, min_values=1, max_values=1)

        async def callback(self, interaction: discord.Interaction):
            guild = interaction.guild
            member = interaction.user
            category = guild.get_channel(TICKET_CATEGORY_ID)

            if not isinstance(category, discord.CategoryChannel):
                await interaction.response.send_message("Kategoria na tickety nie została znaleziona.", ephemeral=True)
                return

            channel_name = f"ticket-{member.name}".lower()
            existing = discord.utils.get(guild.channels, name=channel_name)
            if existing:
                await interaction.response.send_message(f"Masz już otwarty ticket: {existing.mention}", ephemeral=True)
                return

            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }

            ticket_channel = await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)
            await ticket_channel.send(f"{member.mention}, utworzono ticket dotyczący: **{self.values[0]}**")

            await interaction.response.send_message(f"Ticket dotyczący **{self.values[0]}** został utworzony: {ticket_channel.mention}", ephemeral=True)

    view = View()
    view.add_item(PurchaseSelect())

    await ctx.send("Wybierz przedmiot, który chcesz kupić:", view=view)

@bot.event
async def on_raw_reaction_add(payload):
    if payload.member is None or payload.member.bot:
        return

    guild = bot.get_guild(payload.guild_id)

    # Weryfikacja
    if payload.message_id == verification_message_id and str(payload.emoji) == "✅":
        role = guild.get_role(ROLE_ID)
        if role:
            await payload.member.add_roles(role)
            channel = guild.get_channel(payload.channel_id)
            await channel.send(f"{payload.member.mention}, zostałeś zweryfikowany!", delete_after=5)

import os
bot.run(os.getenv("DISCORD_TOKEN"))
