import discord
from discord.ext import commands


class Errors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Error handling
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        emb = discord.Embed(title="Error", color=0xff0000)
        if isinstance(error, commands.CommandNotFound):
            emb.description = "Command not found. Please check the command and try again."
            emb.add_field(
                name="** **", value="Type `!commands` to see the list of available commands.")
        elif isinstance(error, commands.MissingRequiredArgument):
            emb.description = "Missing required argument."
            emb.add_field(
                name="** **", value=f"Try `{ctx.command.usage}` instead.")
        elif isinstance(error, commands.BadArgument):
            emb.description = "The argument provided is an incorrect type."
            # Show the type of argument expected
            emb.add_field(
                name="** **", value=f"Expected: `{ctx.command.usage}`")
        elif isinstance(error, commands.MissingPermissions):
            emb.description = "You don't have the required permissions to run this command."
            emb.add_field(
                name="** **", value="Contact an admin for help.")
        elif isinstance(error, commands.BotMissingPermissions):
            emb.description = "I don't have the required permissions to run this command."
            emb.add_field(
                name="** **", value="Please contact an admin to fix this.")
        else:
            emb.description = "An error occurred that the developer didn't account for.\nPlease contact the developer with the error message below and the command you ran."
            emb.add_field(name="** **", value=error)

        await ctx.send(embed=emb)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Errors(bot))
