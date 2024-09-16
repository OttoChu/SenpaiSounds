import discord
from discord.ext import commands


class SlashCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Slash command to check bot's latency
    @discord.app_commands.command(name="ping", description="Check the bot's latency")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"Pong! {latency}ms", ephemeral=True)


async def setup(bot):
    await bot.add_cog(SlashCommands(bot))
