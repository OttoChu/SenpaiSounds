import discord
from discord.ext import commands
from utils.embbed_list import PaginationView
import random

from utils import dog


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Command to send a laughing gif
    @commands.command()
    async def laugh(self, ctx):
        await ctx.send("<a:laugh:1283320822928248902>")

    # Command to echo the message
    @commands.command()
    async def echo(self, ctx, *, message):
        await ctx.send("".join(message))

    # Command to roll a dice
    @commands.command()
    async def roll_dice(self, ctx, number_of_dice: int = 1, number_of_sides: int = 6):
        dice = [
            str(random.choice(range(1, number_of_sides + 1)))
            for _ in range(number_of_dice)
        ]
        await ctx.send(", ".join(dice))

    # Command to send a random dog image and its details (if available)
    @commands.command()
    async def dog(self, ctx, breed_id=None):
        if breed_id:
            pic_url, pic_detail = dog.get_specific_breed_dog(breed_id)
            if not pic_url:
                await ctx.send("Breed not found!")
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
    @commands.command()
    async def dogs(self, ctx):
        view = PaginationView(dog.get_breeds_keys(), dog.get_breeds_value(),
                              "Dog Breeds", "Some IDs are missing due to API limitations",
                              "Breed ID", "Breed Name")
        embed = view.create_embed()
        await ctx.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(General(bot))
