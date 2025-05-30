import discord

bot = discord.Bot()

@bot.command(description="Ping the bot", guild_ids=[1373295891460526200])  # Zastąp ID serwera
async def ping(ctx):
    await ctx.respond("Pong!")

bot.run("TWÓJ_TOKEN_BOTA")
