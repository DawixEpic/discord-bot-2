import discord
from discord.ext import commands
from discord.ui import View, Select, Button
import asyncio
import os
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

ROLE_ID = 1373275307150278686
TICKET_CATEGORY_ID = 1373277957446959135
LOG_CHANNEL_ID = 1374479815914291240
TICKET_CHANNEL_ID = 1373305137228939416
ADMIN_PANEL_CHANNEL_ID = 1374781085895884820  # tutaj id kanału do wysyłania panelu admina

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
        "𝐋𝐈𝐅𝐄𝐒𝐓𝐄𝐀𝐋": ["Buddha", "Love swap", "Klata meduzy"],
        "𝐁𝐎𝐗𝐏𝐕𝐏": ["nie dostępne", "nie dostępne", "nie dostępne"]
    }
}

OFFER_DATA = {
    1373273108093337640: [
        ("💸 10mld$", "1zł"),
        ("<:Miecz_emoji:1374791139462352906> Miecz 35", "40zł"),
        ("<:Klata_emoji:1374793644246306866> Set 35", "57zł"),
    ],
    1373270295556788285: [
        ("💵 50k$", "1zł"),
        ("💰 1mln$", "15zł"),
        ("🎉 EVENTOWKI:", ""),
        ("<:Excalibur_emoji:1374785662191927416> Excalibur", "270zł"),
        ("<:Totem_emoji:1374788635211206757> Totem ułaskawienia", "80zł"),
        ("<:Sakiewka_emoji:1374799829120716892> Sakiewka", "20zł"),
    ],
    1373268875407396914: [
        ("💸 4,5k$", "1zł"),
        ("💸 50k$", "15zł"),
        ("💸 550k$", "130zł"),
        ("<:ana2_emoji:1374799017359314944> Anarchiczny set 2", "28zł"),
        ("<:Klata_emoji:1374793644246306866> Anarchiczny set 1", "9zł"),
        ("⚔️ MIECZE:", ""),
        ("13732702955567882 Anarchiczny miecz", "3zł"),
        ("🎉 EVENTÓWKI:", ""),
        ("🐰 Zajęczy miecz", "65zł"),
        ("<:Totem_emoji:1374788635211206757 Totem ułaskawienia", "170zł"),
        ("<:Excalibur_emoji:1374785662191927416> Excalibur", "360zł"),
    ],
    1373267159576481842: [
        ("<:Klata_emoji:1374793644246306866> Set 25", "30zł"),
        ("<:Miecz_emoji:1374791139462352906> Miecz 25", "25zł"),
        ("<:Kilof_emoji:1374795407493959751> Kilof 25", "10zł"),
        ("💵 1mln$", "18zł"),
    ],
    1373266589310517338: [
        ("<:Elytra_enoji:1374797373406187580> Elytra", "12zł"),
        ("<:Buty_enoji:1374796797222064230> Buty flasha", "5zł"),
        ("<:Miecz_emoji:1374791139462352906> Miecz 6", "3zł"),
        ("💵 1k$", "1zł"),
        ("<:Shulker_enoji:1374795916531335271> Shulker s2", "7zł"),
        ("<:Shulker_enoji:1374795916531335271> Shulker totemów", "6zł"),
    ],
    1374380939970347019: [
        ("💸 15k$", "1zł"),
        ("🌟 Buddha", "30zł"),
        ("💖 Love swap", "100zł"),
        ("🐉 Klata meduzy", "140zł"),
    ],
}

async def log_action(guild, message):
    log_channel = guild.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(message)

@bot.event
async def on_ready():
    print(f"✅ Zalogowano jako {bot.user}")

    channel = bot.get_channel(ADMIN_PANEL_CHANNEL_ID)
    if channel:
        embed = discord.Embed(
            title="Panel administracyjny ticketów",
            description="Użyj przycisków poniżej aby zarządzać ticketami.\n\n"
                        "- Zamknij ten ticket (usuwa kanał, działa w kanale ticketu)\n"
                        "- Pokaż listę ticketów (lista otwartych kanałów ticketów)",
            color=discord.Color.red()
        )
        view = AdminPanelView()
        await channel.send(embed=embed, view=view)
    else:
        print("❌ Nie znaleziono kanału do wysłania panelu admina.")


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
    embed = discord.Embed(
        title="🎟️ Napisz co chcesz kupić",
        description="Kliknij 🎟️ aby otworzyć prywatny ticket z wyborem opcji.",
        color=discord.Color.blue()
    )
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
                label="Otwórz ticket",
                style=discord.ButtonStyle.green,
                custom_id=f"open_ticket_{channel_id}"
            )

            async def button_callback(interaction):
                # Tutaj możesz zdefiniować co się dzieje po kliknięciu
                await interaction.response.send_message("Ticket zostanie utworzony, proszę czekać...", ephemeral=True)
                # Możesz wywołać funkcję otwierającą ticket

            button.callback = button_callback

            view = View()
            view.add_item(button)
            await channel.send(embed=embed, view=view)
        except Exception as e:
            print(f"❌ Błąd podczas wysyłania oferty do kanału {channel_id}: {e}")


@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id:
        return

    guild = bot.get_guild(payload.guild_id)
    if not guild:
        return

    member = guild.get_member(payload.user_id)
    if not member:
        return

    # Reakcja na weryfikację
    if payload.message_id == verification_message_id and str(payload.emoji) == "✅":
        role = guild.get_role(ROLE_ID)
        if role:
            await member.add_roles(role)
            print(f"Przyznano rolę {role.name} użytkownikowi {member.display_name}")
        return

    # Reakcja na otwarcie ticketu
    if payload.message_id == ticket_message_id and str(payload.emoji) == "🎟️":
        # Sprawdź czy użytkownik ma już ticket
        category = guild.get_channel(TICKET_CATEGORY_ID)
        if not category:
            print("❌ Nie znaleziono kategorii ticketów")
            return

        existing_ticket = discord.utils.get(category.channels, name=f"ticket-{member.name.lower()}")
        if existing_ticket:
            # Można wysłać DM z informacją, że już ma ticket
            try:
                await member.send("Masz już otwarty ticket!")
            except:
                pass
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True)
        }

        channel_name = f"ticket-{member.name.lower()}"
        ticket_channel = await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)
        await ticket_channel.send(f"{member.mention}, wybierz co chcesz kupić:", view=MenuView(member, ticket_channel))

        # Logowanie utworzenia ticketu
        await log_action(guild, f"Ticket utworzony przez {member} - kanał: {ticket_channel.name}")


class MenuView(View):
    def __init__(self, member, ticket_channel):
        super().__init__(timeout=None)
        self.member = member
        self.ticket_channel = ticket_channel
        self.server_selected = None
        self.mode_selected = None

        self.server_select = Select(
            placeholder="Wybierz serwer",
            options=[discord.SelectOption(label=s) for s in SERVER_OPTIONS.keys()],
            custom_id="server_select"
        )
        self.server_select.callback = self.server_select_callback

        self.mode_select = Select(
            placeholder="Wybierz tryb",
            options=[],
            custom_id="mode_select"
        )
        self.mode_select.callback = self.mode_select_callback
        self.mode_select.disabled = True

        self.items_select = Select(
            placeholder="Wybierz item",
            options=[],
            custom_id="items_select"
        )
        self.items_select.callback = self.items_select_callback
        self.items_select.disabled = True

        self.add_item(self.server_select)
        self.add_item(self.mode_select)
        self.add_item(self.items_select)

    async def server_select_callback(self, interaction):
        if interaction.user != self.member:
            await interaction.response.send_message("To nie jest twój ticket!", ephemeral=True)
            return

        self.server_selected = self.server_select.values[0]
        self.mode_select.options = [discord.SelectOption(label=m) for m in SERVER_OPTIONS[self.server_selected].keys()]
        self.mode_select.disabled = False
        self.items_select.disabled = True
        self.items_select.options = []
        await interaction.response.edit_message(view=self)

        # Log
        await log_action(interaction.guild, f"{self.member} wybrał serwer: {self.server_selected}")

    async def mode_select_callback(self, interaction):
        if interaction.user != self.member:
            await interaction.response.send_message("To nie jest twój ticket!", ephemeral=True)
            return

        self.mode_selected = self.mode_select.values[0]
        items = SERVER_OPTIONS[self.server_selected][self.mode_selected]
        self.items_select.options = [discord.SelectOption(label=i) for i in items]
        self.items_select.disabled = False
        await interaction.response.edit_message(view=self)

        # Log
        await log_action(interaction.guild, f"{self.member} wybrał tryb: {self.mode_selected}")

    async def items_select_callback(self, interaction):
        if interaction.user != self.member:
            await interaction.response.send_message("To nie jest twój ticket!", ephemeral=True)
            return

        item = self.items_select.values[0]
        await interaction.response.send_message(f"Wybrałeś: {item}", ephemeral=True)

        # Log
        await log_action(interaction.guild, f"{self.member} wybrał item: {item}")


class AdminPanelView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(label="Zamknij ticket", style=discord.ButtonStyle.red, custom_id="close_ticket"))
        self.add_item(Button(label="Lista ticketów", style=discord.ButtonStyle.grey, custom_id="list_tickets"))

    @discord.ui.button(label="Zamknij ticket", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: Button):
        channel = interaction.channel
        if not channel.name.startswith("ticket-"):
            await interaction.response.send_message("Ta komenda działa tylko w kanale ticketu.", ephemeral=True)
            return

        await channel.delete(reason=f"Ticket zamknięty przez {interaction.user}")

        # Log zamknięcia
        await log_action(interaction.guild, f"Ticket {channel.name} został zamknięty przez {interaction.user}")

        await interaction.response.send_message("Ticket został zamknięty.", ephemeral=True)

    @discord.ui.button(label="Lista ticketów", style=discord.ButtonStyle.grey, custom_id="list_tickets")
    async def list_tickets(self, interaction: discord.Interaction, button: Button):
        category = interaction.guild.get_channel(TICKET_CATEGORY_ID)
        if not category:
            await interaction.response.send_message("Nie znaleziono kategorii ticketów.", ephemeral=True)
            return

        tickets = [c.name for c in category.channels if c.name.startswith("ticket-")]
        if tickets:
            msg = "Lista otwartych ticketów:\n" + "\n".join(tickets)
        else:
            msg = "Brak otwartych ticketów."

        await interaction.response.send_message(msg, ephemeral=True)

        # Log zapytania o listę ticketów
        await log_action(interaction.guild, f"{interaction.user} wyświetlił listę ticketów.")


@bot.event
async def on_raw_reaction_remove(payload):
    if payload.user_id == bot.user.id:
        return

    guild = bot.get_guild(payload.guild_id)
    if not guild:
        return

    member = guild.get_member(payload.user_id)
    if not member:
        return

    if payload.message_id == verification_message_id and str(payload.emoji) == "✅":
        role = guild.get_role(ROLE_ID)
        if role:
            await member.remove_roles(role)
            print(f"Usunięto rolę {role.name} użytkownikowi {member.display_name}")
        return


bot.run(os.getenv("TOKEN"))
