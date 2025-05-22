import discord
from discord.ext import commands
from discord.ui import View, Select, Button
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# KONFIGURACJA
TICKET_CATEGORY_ID = 1373277957446959135  # ID kategorii, gdzie tworzy się ticket
LOG_CHANNEL_ID = 1374479815914291240      # ID kanału logów
SUPPORT_ROLE_ID = 1373275898375176232     # ID roli supportu

SERVER_OPTIONS = {
    "Survival": {
        "Classic": ["Diamenty", "Zbroje", "Miecz"],
        "Hardcore": ["Totemy", "Jabłka", "XP"]
    },
    "SkyBlock": {
        "Easy": ["Dirt", "Obsidian"],
        "Insane": ["Spawner", "VIP"]
    }
}

user_tickets = {}  # user_id: channel_id

# MENU SELECT
class TicketSelect(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.server_select = Select(
            placeholder="Wybierz serwer",
            options=[discord.SelectOption(label=s) for s in SERVER_OPTIONS]
        )
        self.server_select.callback = self.server_callback
        self.add_item(self.server_select)

        self.mode_select = Select(placeholder="Najpierw wybierz serwer", options=[], disabled=True)
        self.mode_select.callback = self.mode_callback
        self.add_item(self.mode_select)

        self.item_select = Select(placeholder="Najpierw wybierz tryb", options=[], disabled=True)
        self.item_select.callback = self.item_callback
        self.add_item(self.item_select)

    async def server_callback(self, interaction: discord.Interaction):
        server = self.server_select.values[0]
        self.mode_select.options = [discord.SelectOption(label=mode) for mode in SERVER_OPTIONS[server]]
        self.mode_select.disabled = False
        self.item_select.disabled = True
        await interaction.response.edit_message(view=self)

    async def mode_callback(self, interaction: discord.Interaction):
        server = self.server_select.values[0]
        mode = self.mode_select.values[0]
        self.item_select.options = [discord.SelectOption(label=item) for item in SERVER_OPTIONS[server][mode]]
        self.item_select.disabled = False
        await interaction.response.edit_message(view=self)

    async def item_callback(self, interaction: discord.Interaction):
        user = interaction.user
        server = self.server_select.values[0]
        mode = self.mode_select.values[0]
        item = self.item_select.values[0]

        ticket_channel = user_tickets.get(user.id)
        if not ticket_channel:
            await interaction.response.send_message("Nie znaleziono twojego ticketa.", ephemeral=True)
            return

        ticket_channel = bot.get_channel(ticket_channel)
        await ticket_channel.send(f"**{user.mention} wybrał:** `{server}` → `{mode}` → `{item}`")

        # LOGI
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(
                title="📥 Nowe zgłoszenie",
                description=f"**Użytkownik:** {user.mention}\n**Serwer:** {server}\n**Tryb:** {mode}\n**Przedmiot:** {item}",
                color=discord.Color.green()
            )
            await log_channel.send(embed=embed)

        await interaction.response.send_message("✅ Wybrano opcje. Support wkrótce się z tobą skontaktuje!", ephemeral=True)

# KOMENDA DO URUCHOMIENIA SYSTEMU
@bot.command()
async def ticket(ctx):
    if ctx.author.id in user_tickets:
        await ctx.send("Masz już otwarty ticket!", delete_after=5)
        return

    category = bot.get_channel(TICKET_CATEGORY_ID)
    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False),
        ctx.author: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        ctx.guild.get_role(SUPPORT_ROLE_ID): discord.PermissionOverwrite(view_channel=True, send_messages=True)
    }

    channel = await ctx.guild.create_text_channel(name=f"ticket-{ctx.author.name}", category=category, overwrites=overwrites)
    user_tickets[ctx.author.id] = channel.id

    await channel.send(
        f"{ctx.author.mention}, wybierz opcje z menu poniżej.",
        view=TicketSelect()
    )

    await ctx.send(f"🎫 Twój ticket został utworzony: {channel.mention}", delete_after=10)

# AUTO USUWANIE Z user_tickets PO ZAMKNIĘCIU
@bot.command()
async def close(ctx):
    if ctx.channel.category_id != TICKET_CATEGORY_ID:
        await ctx.send("To nie jest kanał ticketa.")
        return

    user = None
    for uid, cid in user_tickets.items():
        if cid == ctx.channel.id:
            user = uid
            break

    if user:
        del user_tickets[user]

    await ctx.send("Zamykam ticket za 5 sekund...")
    await asyncio.sleep(5)
    await ctx.channel.delete()

# ZAREJESTRUJ VIEW GLOBALNIE PO STARCIE
@bot.event
async def on_ready():
    bot.add_view(TicketSelect())
    print(f"Zalogowano jako {bot.user}")

bot.run("TWÓJ_TOKEN_BOTA")
