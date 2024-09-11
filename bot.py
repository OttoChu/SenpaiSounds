import os
from dotenv import load_dotenv

import random

import discord
from discord.ext import commands
load_dotenv()

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try: 
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.tree.command(name='hello', description='Say hello to the bot')
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("Hello!", ephemeral=True)


@bot.tree.command(name='ping', description='Check the bot\'s latency')
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! {round(bot.latency * 1000)}ms", ephemeral=True)

@bot.command()
async def echo(ctx, *, message):
    await ctx.send("".join(message))

@bot.command()
async def roll_dice(ctx, number_of_dice: int = 1, number_of_sides: int = 6):
    dice = [
        str(random.choice(range(1, number_of_sides + 1)))
        for _ in range(number_of_dice)
    ]
    await ctx.send(", ".join(dice))

@bot.command()
async def laugh(ctx):
    await ctx.send("<a:laugh:1283320822928248902>")

bot.run(os.getenv("DISCORD_TOKEN"))