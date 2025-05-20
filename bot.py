import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# 🔧 Ustawienia – podaj swoje ID
ROLE_ID = 1373275307150278686  # ID roli do nadania przy weryfikacji
TICKET_CATEGORY_ID = 1373277957446959135  # ID kategorii gdzie tworzyć tickety

verification_message_id = None
ticket_message_id = None

# Słownik do przechowywania wyborów użytkowników: user_id -> {server, mode, items}
user_choices = {}

# Selecty do wyboru w jednej wiadomości
class ServerSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Serwer 1", description="Opis serwera 1"),
            discord.SelectOption(label="Serwer 2", description="Opis serwera 2"),
            discord.SelectOption(label="Serwer 3", description="Opis serwera 3"),
        ]
        super().__init__(placeholder="Wybierz serwer...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        user_choices.setdefault(user_id, {})
        user_choices[user_id]['server'] = self.values[0]
        await interaction.response.send_message(f"Wybrałeś serwer: **{self.values[0]}**", ephemeral=True)

class ModeSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Tryb 1"),
            discord.SelectOption(label="Tryb 2"),
            discord.SelectOption(label="Tryb 3"),
        ]
        super().__init__(placeholder="Wybierz tryb...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        user_choices.setdefault(user_id, {})
        user_choices[user_id]['mode'] = self.values[0]
        await interaction.response.send_message(f"Wybrałeś tryb: **{self.values[0]}**", ephemeral=True)

class ItemSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Item 1"),
            discord.SelectOption(label="Item 2"),
            discord.SelectOption(label="Item 3"),
            discord.SelectOption(label="Item 4"),
            discord.SelectOption(label="Item 5"),
        ]
        super().__init__(placeholder="Wybierz itemy... (max 3)", min_values=1, max_values=3, options=options)

    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        user_choices.setdefault(user_id, {})
        user_choices[user_id]['items'] = self.values
        await interaction.response.send_message(f"Wybrałeś itemy: **{', '.join(self.values)}**", ephemeral=True)

class SelectionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ServerSelect())
        self.add_item(ModeSelect())
        self.add_item(ItemSelect())

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
    embed = discord.Embed(title="🎟️ Wybierz serwer, tryb i itemy do zakupu",
                          description="Użyj poniższych menu, aby wybrać co chcesz kupić, a potem kliknij 🎟️ aby otworzyć ticket.",
                          color=discord.Color.blue())
    view = SelectionView()
    msg = await ctx.send(embed=embed, view=view)
    await msg.add_reaction("🎟️")

    global ticket_message_id
    ticket_message_id = msg.id
    await ctx.send("✅ Wiadomość ticket została wysłana.")

@bot.event
async def on_raw_reaction_add(payload):
    # Ignoruj reakcje bota i brak membera
    if payload.member is None or payload.member.bot:
        return

    guild = bot.get_guild(payload.guild_id)
    if guild is None:
        return

    # Weryfikacja
    if payload.message_id == verification_message_id and str(payload.emoji) == "✅":
        role = guild.get_role(ROLE_ID)
        if role:
            await payload.member.add_roles(role)
            channel = guild.get_channel(payload.channel_id)
            await channel.send(f"{payload.member.mention}, zostałeś zweryfikowany!", delete_after=5)

    # Ticket
    elif payload.message_id == ticket_message_id and str(payload.emoji) == "🎟️":
        category = guild.get_channel(TICKET_CATEGORY_ID)
        if not isinstance(category, discord.CategoryChannel):
            return

        user_id = payload.user_id
        member = payload.member
        choices = user_choices.get(user_id)
        if choices is None:
            # Nie wybrano jeszcze niczego
            channel = guild.get_channel(payload.channel_id)
            await channel.send(f"{member.mention}, najpierw wybierz serwer, tryb i itemy w menu!", delete_after=7)
            return

        channel_name = f"ticket-{member.name}".lower()
        existing = discord.utils.get(guild.channels, name=channel_name)
        if existing:
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }

        ticket_channel = await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)

        # Wyświetl wybrane opcje w tickecie
        server = choices.get('server', 'Nie wybrano')
        mode = choices.get('mode', 'Nie wybrano')
        items = choices.get('items', [])
        items_str = ", ".join(items) if items else "Nie wybrano"

        await ticket_channel.send(f"{member.mention}, Twój ticket został utworzony!\n"
                                  f"**Serwer:** {server}\n"
                                  f"**Tryb:** {mode}\n"
                                  f"**Itemy:** {items_str}")

bot.run(os.getenv("DISCORD_TOKEN"))
