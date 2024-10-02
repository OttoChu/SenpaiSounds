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
    await bot.load_extension('cogs.dogs')
    await bot.load_extension('cogs.music_player')
    await bot.load_extension('cogs.help')
    await bot.load_extension('cogs.errors')

    # Disable the admin cog for now due to the lack of roles check
    # await bot.load_extension('cogs.admin')

    bot.remove_command('help')


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'{bot.user} is ready!')

if __name__ == "__main__":
    import asyncio
    asyncio.run(load_extensions())
    bot.run(os.getenv("DISCORD_TOKEN"))
