import discord
from discord.ui import View

# Button handler to manage pagination with looping


class PaginationView(View):
    def __init__(self, item_list: list, item_id: list = None,
                 title: str = "Items List",
                 list_description: str = "List of items",
                 id_name: str = "IDs", value_name: str = "Values",
                 items_per_page: int = 10, page: int = 0):
        super().__init__()
        self.page = page
        self.item_list = item_list
        self.item_id = item_id
        self.items_per_page = items_per_page
        self.title = title
        self.list_description = list_description
        self.id_name = id_name
        self.value_name = value_name

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        total_pages = (len(self.item_list) - 1) // self.items_per_page + 1
        if self.page == 0:
            self.page = total_pages - 1
        else:
            self.page -= 1
        embed = self.create_embed()
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        total_pages = (len(self.item_list) - 1) // self.items_per_page + 1
        if self.page + 1 >= total_pages:
            self.page = 0
        else:
            self.page += 1
        embed = self.create_embed()
        await interaction.response.edit_message(embed=embed)

    # Embed creation method remains part of PaginationView
    def create_embed(self):
        embed = discord.Embed(title=self.title,
                              color=discord.Color.blue())

        embed.description = self.list_description

        # Calculate the items for the current page
        start = self.page * self.items_per_page
        end = start + self.items_per_page
        items_for_page = self.item_list[start:end]

        # List with no IDs
        if self.item_id == None:
            embed = discord.Embed(title="Items List",
                                  color=discord.Color.blue())
            start = self.page * self.items_per_page
            end = start + self.items_per_page
            items = "\n".join(item for item in items_for_page)
            embed.description = items or "No more items."
            embed.set_footer(
                text=f"Page {self.page + 1} of {(len(self.item_list) - 1) // self.items_per_page + 1}")
            return embed

        # List with IDs
        if not items_for_page:
            embed.description = "No more items."
        else:
            ids = "\n".join(id for id in self.item_id[start:end])
            names = "\n".join(str(item) for item in items_for_page)

            embed.add_field(name=self.id_name, value=ids, inline=True)
            embed.add_field(name=self.value_name, value=names, inline=True)

        embed.set_footer(
            text=f"Page {self.page + 1} of {(len(self.item_list) - 1) // self.items_per_page + 1}")

        return embed
