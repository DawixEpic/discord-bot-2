import discord
from discord.ext import commands
from discord.ui import View, Select, Button
import asyncio
import os
import datetime

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

ROLE_ID = 1373275307150278686
TICKET_CATEGORY_ID = 1373277957446959135
LOG_CHANNEL_ID = 123456789012345678  # <-- Wstaw tutaj ID swojego kanału logów
TICKET_CHANNEL_ID = 1373305137228939416  # <-- Wstaw tutaj ID kanału ticketów

verification_message_id = None
ticket_message_id = None

SERVER_OPTIONS = {
    "𝐂𝐑𝐀𝐅𝐓𝐏𝐋𝐀𝐘": {
        "𝐆𝐈𝐋𝐃𝐈𝐄": ["Elytra", "Buty flasha", "Miecz 6", "Shulker S2", "Shulker totemów", "1k$"],
        "𝐁𝐎𝐗𝐏𝐕𝐏": ["Set 25", "Miecz 25", "Kilof 25", "10k$"]
    },
    "𝐀𝐍𝐀𝐑𝐂𝐇𝐈𝐀": {
        "𝐋𝐈𝐅𝐄𝐒𝐓𝐄𝐀𝐋": ["Set anarchczny 2", "Set anarchiczny 1", "Miecze anarchcznye", "Excalibur", "Totem ułskawienia", "4,5k$", "50k$", "550k$"],
        "𝐁𝐎𝐗𝐏𝐕𝐏": ["Excalibur", "Totem ułskawienia", "Sakiewka", "50k$", "1mln"]
    },
    "𝐑𝐀𝐏𝐘": {
        "𝐋𝐈𝐅𝐄𝐒𝐓𝐄𝐀𝐋": ["nie dostępne", "nie dostępne", "nie dostępne"],
        "𝐁𝐎𝐗𝐏𝐕𝐏": ["Set 35", "Miecz 35", "Kilof 35", "10mld$", "50mld$", "100mld$"]
    },
    "𝐏𝐘𝐊𝐌𝐂": {
        "𝐋𝐈𝐅𝐄𝐒𝐓𝐄𝐀𝐋": ["Budda", "Love swap", "Klata meduzy"],
        "𝐁𝐎𝐗𝐏𝐕𝐏": ["nie dostępne", "nie dostępne", "nie dostępne"]
    }
}

OFFER_DATA = {
    1373273108093337640: [
        ("10MLD", "1 ZŁ"),
        ("MIECZ35", "40 ZŁ"),
        ("SET35", "57 ZŁ"),
    ],
    1373270295556788285: [
        ("1 ZŁ", "50 K$"),
        ("15 ZŁ", "1 MLN"),
        ("EVENTOWKI", ""),
        ("EXCALIBUR 45 +44% +1000 KILLI", "150 ZŁ"),
        ("TOTEM UŁASKAWIENIA", "80 ZŁ"),
        ("SAKIEWKA", "20 ZŁ"),
    ],
    1373268875407396914: [
        ("1 ZŁ", "4,5 K$"),
        ("10 ZŁ", "50 K$"),
        ("100 ZŁ", "550 K$"),
        ("21 ZŁ", "SET ANA 2"),
        ("8 ZŁ", "SET ANA 1"),
        ("MIECZE:", ""),
        ("ANA 51%", "120 ZŁ"),
        ("ANA 40%", "10 ZŁ"),
        ("ANA 44%", "60 ZŁ"),
        ("EVENTOWKI", ""),
        ("ZAJĘCZY MIECZ", "65 ZŁ"),
        ("TOTEM UŁASKAWIENIA", "170 ZŁ"),
        ("EXCALIBUR 39%", "185 ZŁ"),
    ],
    1373267159576481842: [
        ("SET25", "20 ZŁ"),
        ("MIECZ25", "15 ZŁ"),
        ("KILOF25", "5 ZŁ"),
        ("1 MLN", "15 ZŁ"),
    ],
    1373266589310517338: [
        ("ELYTRA", "8 ZŁ"),
        ("BUTY FLASHA", "3 ZŁ"),
        ("MIECZ6", "2 ZŁ"),
        ("1K", "ZŁ"),
        ("SHULKER S2", "2 ZŁ"),
        ("SHULKER TOTEMÓW", "1 ZŁ"),
        ("SPOSÓB NA KOPIOWANIE PRZEDMIOTÓW", "70 ZŁ"),
        ("MOŻLIWOŚĆ ZAKUPU OD 10 ZŁ", ""),
    ],
}

@bot.event
async def on_ready():
    print(f"✅ Zalogowano jako {bot.user}")

@bot.command()
@commands.has_permissions(administrator=True)
async def weryfikacja(ctx):
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
    embed = discord.Embed(title="🎟️ Napisz co chcesz kupić",
                          description="Kliknij 🎟️ aby otworzyć prywatny ticket z wyborem opcji.",
                          color=discord.Color.blue())
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("🎟️")
    global ticket_message_id
    ticket_message_id = msg.id
    await ctx.send("✅ Wiadomość ticket została wysłana.")

@bot.command()
@commands.has_permissions(administrator=True)
async def oferta(ctx):
    for channel_id, items in OFFER_DATA.items():
        try:
            channel = await bot.fetch_channel(channel_id)
            description = ""
            for name, price in items:
                if price:
                    description += f"**{name}** — *Cena:* `{price}`\n"
                else:
                    description += f"**{name}**\n"

            embed = discord.Embed(
                title="🛒 Oferta itemów na sprzedaż",
                description=description + "\n**Kliknij przycisk poniżej, aby otworzyć ticket i dokonać zakupu!**",
                color=discord.Color.blurple()
            )

            button = Button(
                label="📝 Otwórz Ticket",
                style=discord.ButtonStyle.link,
                url=f"https://discord.com/channels/{ctx.guild.id}/{TICKET_CHANNEL_ID}"
            )
            view = View()
            view.add_item(button)

            await channel.send(embed=embed, view=view)
        except Exception as e:
            print(f"Nie udało się wysłać oferty na kanał {channel_id}: {e}")

    await ctx.send("✅ Oferta została wysłana na wszystkie kanały.")

@bot.event
async def on_raw_reaction_add(payload):
    if payload.member is None or payload.member.bot:
        return

    guild = bot.get_guild(payload.guild_id)

    if payload.message_id == verification_message_id and str(payload.emoji) == "✅":
        role = guild.get_role(ROLE_ID)
        if role:
            await payload.member.add_roles(role)
            channel = guild.get_channel(payload.channel_id)
            await channel.send(f"{payload.member.mention}, zostałeś zweryfikowany!", delete_after=5)

    elif payload.message_id == ticket_message_id and str(payload.emoji) == "🎟️":
        category = guild.get_channel(TICKET_CATEGORY_ID)
        if not isinstance(category, discord.CategoryChannel):
            return

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
        await ticket_channel.send(f"{payload.member.mention}, wybierz co chcesz kupić:", view=MenuView(payload.member, ticket_channel))

        # Automatyczne zamykanie po 1h
        await asyncio.sleep(3600)
        if ticket_channel:
           
