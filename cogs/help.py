import discord
from discord.ext import commands
from utils.embedded_list import PaginationView


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Dropdown view for selecting categories
    class CategorySelect(discord.ui.Select):
        def __init__(self, bot):
            self.bot = bot
            categories = [cog_name for cog_name in bot.cogs.keys(
            ) if bot.get_cog(cog_name).get_commands()]
            categories.sort()
            options = [discord.SelectOption(
                label=category, value=category) for category in categories]
            super().__init__(placeholder="Select a category", options=options)

        async def callback(self, interaction: discord.Interaction):
            selected_category = self.values[0]
            commands_list = self.bot.get_cog(selected_category).get_commands()

            # No commands in the category
            if not commands_list:
                await interaction.response.send_message(f"No commands in {selected_category}", ephemeral=True)
                return

            # Sort the commands by name
            commands_list.sort(key=lambda x: x.name)

            # Extract the command names and descriptions
            command_names = [command.name for command in commands_list]
            command_descriptions = [
                command.help or "No description" for command in commands_list]
            command_usage = [
                command.usage or "No usage" for command in commands_list]
            formatted_commands = [f"### !{name}\n{description}\n*`{usage}`*" for name,
                                  description, usage in zip(command_names, command_descriptions, command_usage)]

            # Pagination of commands
            paginated_view = PaginationView(item_list=formatted_commands, item_id=None,
                                            title=f"Commands in {selected_category}",
                                            list_description=None, value_name="Command",
                                            items_per_page=5)

            new_view = discord.ui.View()
            for button in paginated_view.children:
                new_view.add_item(button)
            category_select = Help.CategorySelect(self.bot)
            new_view.add_item(category_select)

            # Edit the original message to show only the commands and dropdown
            await interaction.response.edit_message(
                embed=paginated_view.create_embed(),
                view=new_view
            )

    # Command to show the list of categories with a dropdown menu
    @commands.command(help="Show the list of available commands",
                      usage="!commands")
    async def commands(self, ctx):
        view = discord.ui.View()
        category_select = Help.CategorySelect(self.bot)
        view.add_item(category_select)
        await ctx.send("Select a category to see available commands:", view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))
