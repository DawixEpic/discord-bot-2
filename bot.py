import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# 🔧 Ustawienia – podaj swoje ID
ROLE_ID = 1373275307150278686  # rola do nadania przy weryfikacji
TICKET_CATEGORY_ID = 1373277957446959135  # kategoria do ticketów

verification_message_id = None
ticket_message_id = None

# Słownik do przechowywania wyborów użytkowników
user_selections = {}

@bot.event
async def on_ready():
    print(f"✅ Zalogowano jako {bot.user}")

@bot.command()
@commands.has_permissions(administrator=True)
async def weryfikacja(ctx):
    embed = discord.Embed(
        title="✅ Weryfikacja",
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
    embed = discord.Embed(
        title="🎟️ Napisz co chcesz kupic",
        description="Kliknij 🎟️ aby otworzyć prywatny ticket i wybrać opcje.",
        color=discord.Color.blue())
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("🎟️")
    global ticket_message_id
    ticket_message_id = msg.id
    await ctx.send("✅ Wiadomość ticket została wysłana.")

# --- Klasy widoków i selectów do menu ---

class ServerSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Serwer 1", description="Serwer główny"),
            discord.SelectOption(label="Serwer 2", description="Serwer zapasowy"),
            discord.SelectOption(label="Serwer 3", description="Serwer testowy")
        ]
        super().__init__(placeholder="Wybierz serwer...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        user_selections[interaction.user.id] = {"server": self.values[0]}
        await interaction.response.send_message("Wybrałeś serwer: **{}**\nTeraz wybierz tryb:".format(self.values[0]), ephemeral=True)
        await interaction.followup.send(view=ModeSelectView(), ephemeral=True)

class ModeSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Tryb 1", description="Tryb PvP"),
            discord.SelectOption(label="Tryb 2", description="Tryb Survival"),
            discord.SelectOption(label="Tryb 3", description="Tryb Kreatywny")
        ]
        super().__init__(placeholder="Wybierz tryb...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        user_selections[interaction.user.id]["mode"] = self.values[0]
        await interaction.response.send_message("Wybrałeś tryb: **{}**\nTeraz wybierz item:".format(self.values[0]), ephemeral=True)
        await interaction.followup.send(view=ItemSelectView(), ephemeral=True)

class ItemSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Item 1", description="Miecz diamentowy"),
            discord.SelectOption(label="Item 2", description="Zbroja złota"),
            discord.SelectOption(label="Item 3", description="Kilof żelazny")
        ]
        super().__init__(placeholder="Wybierz item...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        user_selections[interaction.user.id]["item"] = self.values[0]

        # Tworzymy ticket z wybranymi opcjami
        guild = interaction.guild
        member = interaction.user
        category = guild.get_channel(TICKET_CATEGORY_ID)
        if not isinstance(category, discord.CategoryChannel):
            await interaction.response.send_message("Nie znaleziono kategorii ticketów.", ephemeral=True)
            return

        # Sprawdź czy ticket już istnieje
        channel_name = f"ticket-{member.name}".lower()
        existing = discord.utils.get(guild.channels, name=channel_name)
        if existing:
            await interaction.response.send_message("Masz już otwarty ticket.", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        ticket_channel = await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)

        embed = discord.Embed(title="Nowy Ticket",
                              description=f"Użytkownik {member.mention} utworzył ticket z wyborem:",
                              color=discord.Color.blue())
        embed.add_field(name="Serwer", value=user_selections[member.id]["server"], inline=False)
        embed.add_field(name="Tryb", value=user_selections[member.id]["mode"], inline=False)
        embed.add_field(name="Item", value=user_selections[member.id]["item"], inline=False)

        await ticket_channel.send(embed=embed)
        await interaction.response.send_message(f"Ticket został utworzony: {ticket_channel.mention}", ephemeral=True)

        # Usuń zapis wyborów użytkownika
        del user_selections[member.id]

class ServerSelectView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(ServerSelect())

class ModeSelectView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(ModeSelect())

class ItemSelectView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(ItemSelect())

# --- Obsługa reakcji ---

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

    # 🎟️ TICKETY - tutaj zamiast tworzyć ticket na reakcję, wysyłamy menu wyboru
    elif payload.message_id == ticket_message_id and str(payload.emoji) == "🎟️":
        channel = guild.get_channel(payload.channel_id)
        member = payload.member
        await channel.send(f"{member.mention}, wybierz serwer z poniższego menu:", view=ServerSelectView())

import os
bot.run(os.getenv("DISCORD_TOKEN"))
