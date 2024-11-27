import discord
from discord.ext import commands
import discord.ext
from utils import gif, messages
import random


class General(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Command to see the latency of the bot
    @commands.command(help="Check the bot's latency",
                      usage="!ping")
    async def ping(self, ctx: commands.Context):
        latency = round(self.bot.latency * 1000)
        await ctx.send(f"Pong! {latency}ms")

    # Command to send a laughing gif
    @commands.command(help="Sends a laughing message and a gif",
                      usage="!laugh <@username>(optional)")
    async def laugh(self, ctx: commands.Context, target: str = None):
        if target == "@everyone" or target == "@here":
            return

        try:
            target = await commands.MemberConverter().convert(ctx, str(target))
        except commands.errors.MemberNotFound:
            target = None

        if ctx.author == target:
            laugh_message = f"{ctx.author.mention} is laughing at themselves"
        elif target is None:
            laugh_message = eval(messages.get_laugh_message())
        else:
            laugh_message = eval(messages.get_laugh_message(target))

        gif_url = gif.get_gif_laugh()
        if not gif_url:
            embed = discord.Embed(title="Error", color=0xff0000)
            embed.description = "GIPHY rate limit exceeded"
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="Laughing Time", color=0x00ff00)
            embed.description = laugh_message
            embed.set_image(url=gif_url)
            embed.set_footer(text="Powered by GIPHY")
            await ctx.send(embed=embed)

    # Command to send a slapping gif
    @commands.command(help="Sends a slapping message and a gif",
                      usage="!slap <@username>(optional)")
    async def slap(self, ctx: commands.Context, target: str = None):
        if target == "@everyone" or target == "@here":
            return

        try:
            target = await commands.MemberConverter().convert(ctx, str(target))
        except commands.errors.MemberNotFound:
            target = None

        if target is None:
            slap_message = eval(messages.get_slap_message())
        elif ctx.author == target:
            slap_message = f"{ctx.author.mention} is slapping themselves"
        elif target == self.bot.user:
            slap_message = f"{ctx.author.mention} is abusing a bot. Shame on you!"
        else:
            slap_message = eval(messages.get_slap_message(target))

        gif_url = gif.get_gif_slap()
        embed = discord.Embed(title="Slapping Time", color=0x00ff00)
        embed.description = slap_message
        embed.set_image(url=gif_url)
        embed.set_footer(text="Powered by GIPHY")
        await ctx.send(embed=embed)

    # Command to echo the message
    @commands.command(help="Repeats the message",
                      usage="!echo <message>")
    async def echo(self, ctx: commands.Context, *, message: str):
        if "I am dumb" in message:
            await ctx.send(f"{ctx.author.mention} is dumb. I agree.")
            return
        elif "@everyone" in message or "@here" in message:
            return
        await ctx.send("".join(message))

    # Command to roll a dice
    @commands.command(help="Roll a dice with 6 sides by default",
                      usage="!roll_dice <number_of_dice>(optional) <number_of_sides>(optional)")
    async def roll_dice(self, ctx: commands.Context, number_of_dice: int = 1, number_of_sides: int = 6):
        dice = [
            str(random.choice(range(1, number_of_sides + 1)))
            for _ in range(number_of_dice)
        ]
        await ctx.send(", ".join(dice))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(General(bot))
