import discord
from discord.ext import commands
import discord.ext
from utils.embedded_list import PaginationView
from utils import dog, gif
import random


class General(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Command to send a laughing gif
    @commands.command()
    async def laugh(self, ctx: commands.Context, person: str = None):
        try:
            person = await commands.MemberConverter().convert(ctx, str(person))
        except commands.errors.MemberNotFound:
            person = None
        if ctx.author == person:
            laugh_message = f"{ctx.author.mention} is laughing at themselves"
        elif person is None:
            laugh_message = f"{ctx.author.mention} is laughing"
        else:
            laugh_message = f"{ctx.author.mention} is laughing at {person.mention}"

        gif_url = gif.get_gif_laugh()
        if not gif_url:
            embed = discord.Embed(title="Error", color=0xff0000)
            embed.description = "GIPHY rate limit exceeded"
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="Laughing GIF", color=0x00ff00)
            embed.description = laugh_message
            embed.set_image(url=gif_url)
            await ctx.send(embed=embed)

    # Command to send a slapping gif
    @commands.command()
    async def slap(self, ctx: commands.Context, person: str = None):
        try:
            person = await commands.MemberConverter().convert(ctx, str(person))
        except commands.errors.MemberNotFound:
            person = None
        if person is None:
            slap_message = f"{ctx.author.mention} is slapping someone"
        elif person == self.bot.user:
            slap_message = f"{ctx.author.mention} is abusing a bot"
        elif ctx.author == person:
            slap_message = f"{ctx.author.mention} is slapping themselves"
        else:
            slap_message = f"{ctx.author.mention} is slapping {person.mention}"

        gif_url = gif.get_gif_slap()
        embed = discord.Embed(title="Slapping GIF", color=0x00ff00)
        embed.description = slap_message
        embed.set_image(url=gif_url)
        await ctx.send(embed=embed)

    # Command to echo the message
    @commands.command()
    async def echo(self, ctx: commands.Context, *, message: str):
        await ctx.send("".join(message))

    # Command to roll a dice
    @commands.command()
    async def roll_dice(self, ctx: commands.Context, number_of_dice: int = 1, number_of_sides: int = 6):
        dice = [
            str(random.choice(range(1, number_of_sides + 1)))
            for _ in range(number_of_dice)
        ]
        await ctx.send(", ".join(dice))

    # Command to send a random dog image and its details (if available)
    @commands.command()
    async def dog(self, ctx: commands.Context, breed_id: int = None):
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
    async def dogs(self, ctx: commands.Context):
        view = PaginationView(dog.get_breeds_keys(), dog.get_breeds_value(),
                              "Dog Breeds", "Some IDs are missing due to API limitations",
                              "Breed ID", "Breed Name")
        embed = view.create_embed()
        await ctx.send(embed=embed, view=view)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(General(bot))
