import discord
from discord.ext import commands


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Kick a member from the server",
                      usage="!kick <@username> <reason>(optional)")
    async def kick(self, ctx: commands.Context, member: discord.Member, *, reason: str = None):
        await member.kick(reason=reason)
        await ctx.send(f'{member.mention} has been kicked.')

    @commands.command(help="Ban a member from the server",
                      usage="!ban <@username> <reason>(optional)")
    async def ban(self, ctx: commands.Context, member: discord.Member, *, reason: str = None):
        await member.ban(reason=reason)
        await ctx.send(f'{member.mention} has been banned.')

    @commands.command(help="Unban a member from the server",
                      usage="!unban <username#discriminator>")
    async def unban(self, ctx: commands.Context, *, member: str):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')

        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(f'{user.mention} has been unbanned.')
                return

    # Clear messages in a channel
    @commands.command(help="Clear messages in a channel",
                      usage="!clear <amount>")
    async def clear_messages(self, ctx: commands.Context, amount: int):
        await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f'{amount} messages have been cleared by {ctx.author.mention}.')


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Admin(bot))
