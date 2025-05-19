import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# 🔧 Ustawienia – podaj tutaj swoje ID
ROLE_ID = 1373275307150278686  # <- ID roli do nadania przy weryfikacji
TICKET_CATEGORY_ID = 1373277957446959135  # <- ID kategorii gdzie tworzyć tickety

verification_message_id = None
ticket_message_id = None

@bot.event
async def on_ready():
    print(f"✅ Zalogowano jako {bot.user}")

@bot.command()
@commands.has_permissions(administrator=True)
async def weryfikacja(ctx):
    """Wysyła wiadomość weryfikacyjną z reakcją."""
    embed = discord.Embed(title="✅ Weryfikacja",
                          description="Kliknij ✅ aby się zweryfikować i dostać dostęp.",
                          color=discord.Color.green())
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("✅")

    global verification_message_id
    verification_message_id = msg.id
    await ctx.send("✅ Wiadomość weryfikacyjna została wysłana.")

@bot.command()
@commands.has_permissions(administrator=True)
async def ticket(ctx):
    """Wysyła wiadomość ticket z reakcją 🎟️."""
    embed = discord.Embed(title="🎟️ Pomoc techniczna",
                          description="Kliknij 🎟️ aby otworzyć prywatny ticket.",
                          color=discord.Color.blue())
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("🎟️")

    global ticket_message_id
    ticket_message_id = msg.id
    await ctx.send("✅ Wiadomość ticket została wysłana.")

@bot.event
async def on_raw_reaction_add(payload):
    if payload.member is None or payload.member.bot:
        return

    guild = bot.get_guild(payload.guild_id)

    # ✅ WERYFIKACJA
    if payload.message_id == verification_message_id and str(payload.emoji) == "✅":
        role = guild.get_role(ROLE_ID)
        if role:
            await payload.member.add_roles(role)
            channel = guild.get_channel(payload.channel_id)
            await channel.send(f"{payload.member.mention}, zostałeś zweryfikowany!", delete_after=5)

    # 🎟️ TICKETY
    elif payload.message_id == ticket_message_id and str(payload.emoji) == "🎟️":
        category = guild.get_channel(TICKET_CATEGORY_ID)
        if not isinstance(category, discord.CategoryChannel):
            return

        # Sprawdź czy użytkownik ma już ticket
        channel_name = f"ticket-{payload.member.name}".lower()
        existing = discord.utils.get(guild.channels, name=channel_name)
        if existing:
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            payload.member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        ticket_channel = await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)
        await ticket_channel.send(f"{payload.member.mention}, Twój ticket został utworzony!")

import os
bot.run(os.getenv("DISCORD_TOKEN"))
