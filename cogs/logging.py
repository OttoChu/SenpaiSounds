import discord
from discord.ext import commands, tasks
from utils.messages import get_annoying_messages
from random import choice


class Logging(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.counter = 0
        self.annoying_messages = get_annoying_messages()

    # Event to handle message edits
    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.author.bot:
            return

        if before.content != after.content:
            embed = discord.Embed(title=f'Message edited', color=0xFF0000)
            embed.description = f"[Jump to message]({after.jump_url})"
            embed.add_field(name="Before", value=before.content, inline=False)
            embed.add_field(name="After", value=after.content, inline=False)
            embed.set_footer(
                text=f"Edited in {before.channel.name} by {before.author.name}")
            await before.channel.send(embed=embed)

    # Event to handle message deletions
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot or '@everyone' in message.content or '@here' in message.content:
            return

        emb = discord.Embed(
            title=f"Someone is trying to be sneaky!", color=0xFF0000)
        emb.add_field(name="The following message was deleted",
                      value=message.content, inline=False)
        emb.set_footer(
            text=f"Originally sent by {message.author.name} in {message.channel.name}")
        await message.channel.send(embed=emb)

    # Event to handle message pings
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if '@everyone' in message.content or '@here' in message.content:
            self.annoying_pings.start(message)

    # Task to send annoying messages when someone pings everyone
    @tasks.loop(minutes=1)
    async def annoying_pings(self, message: discord.Message):
        await message.channel.send(eval(choice(self.annoying_messages)))
        self.counter += 1
        if self.counter >= 5:
            self.annoying_pings.stop()
            self.counter = 0


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Logging(bot))
