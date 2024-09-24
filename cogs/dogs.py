import discord
from discord.ext import commands
from utils.embedded_list import PaginationView
from utils import dog

class Dog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Command to send a random dog image and its details (if available)
    @commands.command(help="Sends a dog image with its details",
                      usage="!dog <breed_id>(optional)")
    async def dog(self, ctx: commands.Context, breed_id: int = None):
        if breed_id:
            pic_url, pic_detail = dog.get_specific_breed_dog(breed_id)
            if not pic_url:
                emb = discord.Embed(title="Breed not found", color=0xff0000)
                emb.description = "Please check the breed ID and try again."
                await ctx.send(embed=emb)
                return
        else:
            pic_url, pic_detail = dog.get_random_dog()

        emb = discord.Embed(title="A dog has been summoned!", color=0x00ff00)
        emb.set_image(url=pic_url)

        breed_fields = {
            "Breed": "name",
            "Bred For": "bred_for",
            "Description": "description",
            "Temperament": "temperament",
            "Life Span": "life_span"
        }

        breed_info = pic_detail.get('breeds', [{}])[0]
        for field_name, key in breed_fields.items():
            if key in breed_info:
                emb.add_field(name=field_name,
                              value=breed_info[key], inline=False)

        emb.set_footer(text=f"Requested by {ctx.author.name}")
        await ctx.send(embed=emb)

    # Command to list all dog breeds
    @commands.command(help="List all dog breeds",
                      usage="!dogs")
    async def dogs(self, ctx: commands.Context):
        view = PaginationView(dog.get_breeds_keys(), dog.get_breeds_value(),
                              "Dog Breeds", "Some IDs are missing due to API limitations",
                              "Breed ID", "Breed Name")
        embed = view.create_embed()
        await ctx.send(embed=embed, view=view)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Dog(bot))