import discord as dc
from discord.ext import commands
from models.stats import StatsPage
from models.harm import HarmPage
from models.hx import HxPage
from models.moves import MovesPage
from models.improvements import ImprovementPage
from models.inventory import InventoryPage
from models.page_manager import PageManager
from config import TOKEN  # Import the bot token from the config module
from emojis import EMOJI_LEFT, EMOJI_RIGHT 

intents = dc.Intents.all()
bot = commands.Bot( command_prefix='!', intents=intents )

# @bot.command()
# async def checksheet(ctx):

    # embed=dc.Embed(title="Name: Dou", description="Playbook: The Angel", color=0xff3838)
    # embed.set_author(name=f'@user')
    # embed.set_thumbnail(url="https://i.imgur.com/fAi8DsQ.png")
    # embed.add_field(name="STATS", value="stats here\nfstsd", inline=True)

    # msg = await ctx.send( embed=embed )
    # await msg.add_reaction(EMOJI_LEFT)
    # await msg.add_reaction(EMOJI_RIGHT) 

    # def check(reaction, user):
    #     return reaction.message.id == msg.id and str(reaction.emoji) in [EMOJI_LEFT, EMOJI_RIGHT]

    # reaction, user = await bot.wait_for('reaction_add', check=check)
    # if str(reaction.emoji) == EMOJI_LEFT:
    #     await ctx.send(f'Thanks for the thumbs up, {user.mention}!')
    # elif str(reaction.emoji) == EMOJI_RIGHT:
    #     await ctx.send(f'Sorry you didn\'t like it, {user.mention}!')

@bot.command()
async def checksheet(ctx):
    
    pages = [
        StatsPage(),
        HxPage(),
        HarmPage(),
        MovesPage(),
        ImprovementPage(),
        InventoryPage()
    ]
    pageManager = PageManager("Name: Dou", "Playbook: The Angel", pages)

    embed = dc.Embed.from_dict(pageManager.get_embed_dict())
    msg = await ctx.reply(embed=embed)

    await msg.add_reaction(EMOJI_LEFT) # left arrow
    await msg.add_reaction(EMOJI_RIGHT) # right arrow

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in [EMOJI_LEFT, EMOJI_RIGHT]

    while True:
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)

            if str(reaction.emoji) == EMOJI_LEFT:
                pageManager.turn_page(-1)
            elif str(reaction.emoji) == EMOJI_RIGHT:
                pageManager.turn_page(1)

            embed = dc.Embed.from_dict(pageManager.get_embed_dict())
            await msg.edit(embed=embed)
            await msg.remove_reaction(reaction, user)
        except:
            break

@bot.command()
async def snow(ctx):
    user_id = str(ctx.author.id)
    await ctx.reply(f'{ctx.message.author.mention} {user_id}')

@bot.command()
async def test(ctx):
    print(PageManager('teste', [HxPage()]).get_embed_dict())

bot.run( TOKEN )