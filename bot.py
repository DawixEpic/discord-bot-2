import discord
from discord.ui import View, Button
from discord.ext import commands
import datetime

# ID kanału ocen – upewnij się, że masz to zdefiniowane wcześniej
RATING_CHANNEL_ID = 1375528888586731762

class RatingButton(Button):
    def __init__(self, user_id, rating):
        super().__init__(label="⭐" * rating, style=discord.ButtonStyle.secondary)
        self.user_id = user_id
        self.rating = rating

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ To nie twoja ocena.", ephemeral=True)
            return

        await interaction.response.send_message("✅ Dziękujemy za ocenę! Czy chciałbyś dodać opinię? Odpowiedz tutaj w ciągu 60 sekund, lub wpisz `nie`.", ephemeral=True)

        def check(msg):
            return msg.author.id == self.user_id and isinstance(msg.channel, discord.DMChannel)

        try:
            msg = await interaction.client.wait_for("message", check=check, timeout=60)
            opinion = None if msg.content.lower() in ["nie", "no"] else msg.content
        except:
            opinion = None

        # Wyślij ocenę do kanału
        channel = interaction.client.get_channel(RATING_CHANNEL_ID)
        if channel:
            embed = discord.Embed(
                title="⭐ Nowa ocena",
                description=(
                    f"**Użytkownik:** {interaction.user.mention}\n"
                    f"**Ocena:** {'⭐' * self.rating} ({self.rating}/5)\n"
                    f"**Data:** <t:{int(datetime.datetime.now().timestamp())}:f>"
                ),
                color=discord.Color.gold()
            )
            if opinion:
                embed.add_field(name="💬 Opinia", value=opinion, inline=False)

            await channel.send(embed=embed)

        self.view.disable_all_items()
        await interaction.edit_original_response(content="✅ Dziękujemy za ocenę!", view=self.view)


class RatingView(View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id
        for i in range(1, 6):
            self.add_item(RatingButton(user_id, i))


async def send_rating_prompt(user: discord.User, bot: commands.Bot):
    try:
        view = RatingView(user.id)
        await user.send("Jak oceniasz zamówienie? Kliknij odpowiednią liczbę gwiazdek:", view=view)
    except discord.Forbidden:
        print(f"❌ Nie mogę wysłać wiadomości do {user.name}.")
