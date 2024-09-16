from discord.ext import commands
import discord
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)


async def load_extensions():
    await bot.load_extension('cogs.logging')
    await bot.load_extension('cogs.general')
    await bot.load_extension('cogs.admin')
    await bot.load_extension('cogs.slash_commands')


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Logged in as {bot.user}!')

if __name__ == "__main__":
    import asyncio
    asyncio.run(load_extensions())
    bot.run(os.getenv("DISCORD_TOKEN"))
