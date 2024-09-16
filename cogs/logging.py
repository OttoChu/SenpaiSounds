import discord
from discord.ext import commands


class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Event to handle message edits
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot:
            return

        if before.content != after.content:
            embed = discord.Embed(title=f'Message edited', color=0xFF0000)
            embed.add_field(name="Before", value=before.content, inline=False)
            embed.add_field(name="After", value=after.content, inline=False)
            embed.add_field(
                name="** **", value=f"[Jump to message]({after.jump_url})", inline=False)
            embed.set_footer(
                text=f"Edited in {before.channel.name} by {before.author.name}")
            await before.channel.send(embed=embed)

    # Event to handle message deletions
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return

        emb = discord.Embed(
            title=f"Someone is trying to be sneaky!", color=0xFF0000)
        emb.add_field(name="The following message was deleted",
                      value=message.content, inline=False)
        emb.set_footer(
            text=f"Originally sent by {message.author.name} in {message.channel.name}")
        await message.channel.send(embed=emb)


async def setup(bot):
    await bot.add_cog(Logging(bot))
