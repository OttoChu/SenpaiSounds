import discord
from discord.ext import commands


class Bot_Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Command to show the bot's info
    @commands.command(name="info", aliases=["botinfo", "bot_info"])
    async def info(self, ctx):
        embed = discord.Embed(title="About Me", color=0x00FF00)
        embed.set_thumbnail(url=self.bot.user.avatar)
        embed.add_field(name="Name", value=self.bot.user.name)
        embed.add_field(name="ID", value=self.bot.user.id)
        embed.add_field(name="Created at", value=self.bot.user.created_at.strftime(
            "%d/%m/%Y %H:%M:%S"))
        embed.add_field(
            name="Developer", value=f"{self.bot.get_user(536600125506846723).mention}", inline=False)
        embed.add_field(
            name="Source code", value="[GitHub](https://github.com/OttoChu/SenpaiSounds)", inline=False)
        embed.set_footer(text="© 2024 SenpaiSounds")
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Bot_Info(bot))
