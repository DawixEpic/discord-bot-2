import discord
from discord.ext import commands, tasks
import os
import asyncio

intents = discord.Intents.default()
intents.members = True
intents.invites = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# --- KONFIGURACJA ---
GUILD_ID = 1373253103176122399
ROLE_ID = 1373275307150278686
VERIFY_CHANNEL_ID = 1373258480382771270
TICKET_CHANNEL_ID = 1373305137228939416
TICKET_CATEGORY_ID = 1373277957446959135
LOG_CHANNEL_ID = 1374479815914291240
ADMIN_ROLE_ID = 1373275898375176232
INVITE_STATS_CHANNEL_ID = 1378727886478901379  # Zamień na właściwe ID

SERVER_OPTIONS = {
    "𝐂𝐑𝐀𝐅𝐓𝐏𝐋𝐀𝐘": {
        "𝐆𝐈𝐋𝐃𝐈𝐄": ["Elytra", "Buty flasha", "Miecz 6", "1k$", "Shulker s2", "Shulker totemów"],
        "𝐁𝐎𝐗𝐏𝐕𝐏": ["Set 25", "Miecz 25", "Kilof 25", "1mln$"]
    },
    "𝐀𝐍𝐀𝐑𝐂𝐇𝐈𝐀": {
        "𝐋𝐈𝐅𝐄𝐒𝐓𝐄𝐀𝐋": ["4,5k$", "50k$", "550k$", "Anarchiczny set 2", "Anarchiczny set 1", "Anarchiczny miecz", "Zajęczy miecz", "Totem ułaskawienia", "Excalibur"],
        "𝐁𝐎𝐗𝐏𝐕𝐏": ["50k$", "1mln$", "Excalibur", "Totem ułaskawienia", "Sakiewka"]
    },
    "𝐑𝐀𝐏𝐘": {
        "𝐋𝐈𝐅𝐄𝐒𝐓𝐄𝐀𝐋": ["nie dostępne", "nie dostępne", "nie dostępne"],
        "𝐁𝐎𝐗𝐏𝐕𝐏": ["10mld$", "Miecz 35", "Set 35"]
    },
    "𝐏𝐘𝐊𝐌𝐂": {
        "𝐋𝐈𝐅𝐄𝐒𝐓𝐄𝐀𝐋": ["15k$", "Buda", "Love swap", "Klata meduzy"],
        "𝐁𝐎𝐗𝐏𝐕𝐏": ["nie dostępne", "nie dostępne", "nie dostępne"]
    }
}

# Cache zaproszeń do śledzenia użyć
invite_uses_cache = {}

# --- WERYFIKACJA ---
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

# --- TICKET ---
class CloseButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="❌ Zamknij ticket", style=discord.ButtonStyle.danger)
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        admin_role = interaction.guild.get_role(ADMIN_ROLE_ID)
        if admin_role in interaction.user.roles:
            await interaction.channel.delete(reason="Ticket zamknięty przez admina.")
        else:
            await interaction.response.send_message("❌ Tylko administrator może zamknąć ten ticket.", ephemeral=True)

class PurchaseView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.server = None
        self.mode = None
        self.items = []

        self.server_select = discord.ui.Select(
            placeholder="Wybierz serwer...",
            options=[discord.SelectOption(label=server) for server in SERVER_OPTIONS.keys()]
        )
        self.server_select.callback = self.server_selected
        self.add_item(self.server_select)

    async def server_selected(self, interaction: discord.Interaction):
        self.server = self.server_select.values[0]
        self.clear_items()
        self.mode_select = discord.ui.Select(
            placeholder="Wybierz tryb...",
            options=[discord.SelectOption(label=mode) for mode in SERVER_OPTIONS[self.server].keys()]
        )
        self.mode_select.callback = self.mode_selected
        self.add_item(self.mode_select)
        await interaction.response.edit_message(content=f"Serwer: `{self.server}`\nWybierz tryb:", view=self)

    async def mode_selected(self, interaction: discord.Interaction):
        self.mode = self.mode_select.values[0]
        self.clear_items()
        self.item_select = discord.ui.Select(
            placeholder="Wybierz itemy...",
            options=[discord.SelectOption(label=item) for item in SERVER_OPTIONS[self.server][self.mode]],
            min_values=1,
            max_values=len(SERVER_OPTIONS[self.server][self.mode])
        )
        self.item_select.callback = self.item_selected
        self.add_item(self.item_select)
        await interaction.response.edit_message(content=f"Serwer: `{self.server}`\nTryb: `{self.mode}`\nWybierz itemy:", view=self)

    async def item_selected(self, interaction: discord.Interaction):
        self.items = self.item_select.values
        self.clear_items()
        await interaction.response.edit_message(
            content=f"Serwer: `{self.server}`\nTryb: `{self.mode}`\nItemy: `{', '.join(self.items)}`\n\n✅ Dziękujemy za złożenie zamówienia!",
            view=CloseButton()
        )
        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(title="🛒 Nowe zamówienie w tickecie", color=discord.Color.gold())
            embed.add_field(name="Użytkownik", value=f"{interaction.user.mention} ({interaction.user.name})", inline=False)
            embed.add_field(name="Serwer", value=self.server, inline=True)
            embed.add_field(name="Tryb", value=self.mode, inline=True)
            embed.add_field(name="Itemy", value=", ".join(self.items), inline=False)
            embed.set_footer(text=f"Data: {interaction.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            await log_channel.send(embed=embed)

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

        await ticket_channel.send(f"{interaction.user.mention} 🎫 Ticket został utworzony. Wybierz przedmioty z interesującego Cię serwera Minecraft:", view=PurchaseView())
        await interaction.response.send_message("✅ Ticket utworzony!", ephemeral=True)

# --- OFERTY I USUWANIE STARYCH WIADOMOŚCI ---
async def clear_bot_messages(channel):
    try:
        async for msg in channel.history(limit=100):
            if msg.author == bot.user:
                await msg.delete()
                await asyncio.sleep(0.5)  # aby nie było limitów API
    except Exception as e:
        print(f"Błąd przy czyszczeniu wiadomości: {e}")

async def send_offers(channel):
    embed = discord.Embed(title="🛒 Oferta itemów na sprzedaż", color=discord.Color.blue())
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1373268875407396914/1378672704999264377/Zrzut_ekranu_2025-05-17_130038.png")
    # oferta CRAFTPLAY
    embed.add_field(name="𝐂𝐑𝐀𝐅𝐓𝐏𝐋𝐀𝐘", value="\n".join([
        "**𝐆𝐈𝐋𝐃𝐈𝐄:** Elytra\nButy flasha\nMiecz 6\n1k$\nShulker s2\nShulker totemów",
        "**𝐁𝐎𝐗𝐏𝐕𝐏:** Set 25\nMiecz 25\nKilof 25\n1mln$"
    ]), inline=False)
    # oferta ANARCHIA
    embed.add_field(name="𝐀𝐍𝐀𝐑𝐂𝐇𝐈𝐀", value="\n".join([
        "**𝐋𝐈𝐅𝐄𝐒𝐓𝐄𝐀𝐋:** 4,5k$\n50k$\n550k$\nAnarchiczny set 2\nAnarchiczny set 1\nAnarchiczny miecz\nZajęczy miecz\nTotem ułaskawienia\nExcalibur",
        "**𝐁𝐎𝐗𝐏𝐕𝐏:** 50k$\n1mln$\nExcalibur\nTotem ułaskawienia\nSakiewka"
    ]), inline=False)
    # możesz dodać pozostałe oferty w podobny sposób...
    await channel.send(embed=embed, view=TicketButton())
    print("Wysłano ofertę.")

# --- ZAPROSZENIA I ILOŚĆ ZAPROSZONYCH ---

@bot.event
async def on_ready():
    print(f"Bot zalogowany jako {bot.user}")

    guild = bot.get_guild(GUILD_ID)
    if guild:
        invites = await guild.invites()
        # Inicjuj cache zaproszeń wraz z ich użyciami
        for invite in invites:
            invite_uses_cache[invite.code] = invite.uses

    update_offers.start()

@bot.event
async def on_member_join(member):
    guild = member.guild
    try:
        invites_before = invite_uses_cache.copy()  # kopia stanu przed joinem
        invites_after = await guild.invites()
        invite_uses_cache.clear()
        for invite in invites_after:
            invite_uses_cache[invite.code] = invite.uses

        used_invite = None
        for invite in invites_after:
            before_uses = invites_before.get(invite.code, 0)
            if invite.uses > before_uses:
                used_invite = invite
                break

        if used_invite:
            inviter = used_invite.inviter
            if inviter:
                # Wysyłanie prywatnej wiadomości do nowego członka z info kto go zaprosił i ile osób zaprosił
                try:
                    await member.send(f"Cześć {member.name}! Zostałeś zaproszony przez {inviter.name}. On zaprosił już {used_invite.uses} osób!")
                except discord.Forbidden:
                    pass  # Nie można wysłać DM (prawdopodobnie użytkownik ma wyłączone DM)
                
                # Możesz też wysłać statystyki na wybrany kanał:
                stats_channel = guild.get_channel(INVITE_STATS_CHANNEL_ID)
                if stats_channel:
                    embed = discord.Embed(title="Nowy członek dołączył", color=discord.Color.green())
                    embed.add_field(name="Użytkownik", value=member.mention, inline=True)
                    embed.add_field(name="Zaprosił", value=inviter.mention, inline=True)
                    embed.add_field(name="Liczba zaproszonych", value=str(used_invite.uses), inline=True)
                    await stats_channel.send(embed=embed)
        else:
            # Zaproszenie nie zostało wykryte (np. vanity URL, lub zaproszenie wygasło)
            pass
    except Exception as e:
        print(f"Błąd w on_member_join: {e}")

@tasks.loop(minutes=60)
async def update_offers():
    guild = bot.get_guild(GUILD_ID)
    if guild:
        channel = guild.get_channel(TICKET_CHANNEL_ID)
        if channel:
            await clear_bot_messages(channel)
            await send_offers(channel)

# --- Komenda weryfikacji (alternatywa do przycisku) ---
@bot.command()
@commands.has_permissions(manage_roles=True)
async def wyslij_weryfikacje(ctx):
    view = WeryfikacjaButton()
    await ctx.send("Kliknij przycisk, aby się zweryfikować:", view=view)

# Uruchomienie bota
if __name__ == "__main__":
    TOKEN = os.getenv("TOKEN")
    if not TOKEN:
        print("Brak tokenu! Ustaw zmienną środowiskową TOKEN.")
    else:
        bot.run(TOKEN)
