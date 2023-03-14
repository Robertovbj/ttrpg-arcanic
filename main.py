import discord as dc
import math
from discord.ext import commands
from models.stats import StatsPage
from models.harm import HarmPage
from models.hx import HxPage
from models.moves import MovesPage
from models.improvements import ImprovementPage
from models.inventory import InventoryPage
from models.page_manager import PageManager
from models.playbook import Playbook
from models.new_character import NewCharacterPage, ChooseSetPage
from configs.database import Database
from config import TOKEN  # Import the bot token from the config module
import emojis

intents = dc.Intents.all()
bot = commands.Bot( command_prefix='!', intents=intents )
db = Database()

# @bot.command()
# async def checksheet(ctx):

    # embed=dc.Embed(title="Name: Dou", description="Playbook: The Angel", color=0xff3838)
    # embed.set_author(name=f'@user')
    # embed.set_thumbnail(url="https://i.imgur.com/fAi8DsQ.png")
    # embed.add_field(name="STATS", value="stats here\nfstsd", inline=True)

    # msg = await ctx.send( embed=embed )
    # await msg.add_reaction(emojis.EMOJI_LEFT)
    # await msg.add_reaction(emojis.EMOJI_RIGHT) 

    # def check(reaction, user):
    #     return reaction.message.id == msg.id and str(reaction.emoji) in [emojis.EMOJI_LEFT, emojis.EMOJI_RIGHT]

    # reaction, user = await bot.wait_for('reaction_add', check=check)
    # if str(reaction.emoji) == emojis.EMOJI_LEFT:
    #     await ctx.send(f'Thanks for the thumbs up, {user.mention}!')
    # elif str(reaction.emoji) == emojis.EMOJI_RIGHT:
    #     await ctx.send(f'Sorry you didn\'t like it, {user.mention}!')

@bot.command()
async def checksheet(ctx: commands.Context):
    
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

    await add_arrows(msg)

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in [emojis.EMOJI_LEFT, emojis.EMOJI_RIGHT]

    while True:
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)

            if str(reaction.emoji) == emojis.EMOJI_LEFT:
                pageManager.turn_page(-1)
            elif str(reaction.emoji) == emojis.EMOJI_RIGHT:
                pageManager.turn_page(1)

            embed = dc.Embed.from_dict(pageManager.get_embed_dict())
            await msg.edit(embed=embed)
            await msg.remove_reaction(reaction, user)
        except:
            break

@bot.command()
async def createsheet(ctx: commands.Context, name: str):

    playbooks = Playbook().get_playbooks()
    playbook_count = len(playbooks)
    pages = []

    for i in range(0, playbook_count, 10):
        # Extract the "name" element from each inner list and concatenate them into a string
        batch_playbooks = "\n".join(str(inner_list[1]) for inner_list in playbooks[i:i+10])
        # Makes a emoji string with the same size as the playbook list
        batch_emojis = "\n".join(emoji for emoji in emojis.EMOJI_LIST[0:batch_playbooks.count("\n")+1])
        pages.append( NewCharacterPage(batch_playbooks, batch_emojis) ) 

    pageManager = PageManager(f"Name: {name}", "Playbook: Choosing...", pages)

    embed = dc.Embed.from_dict(pageManager.get_embed_dict())
    msg = await ctx.reply(embed=embed)

    for i in emojis.EMOJI_LIST:
        await msg.add_reaction(i)
    
    await add_arrows(msg)


@bot.command()
async def snow(ctx):
    # user_id = str(ctx.author.id)
    test = db.insert('CHARACTERS (CHR_NAME, CHAR_TEST)', ['banana', 'pera'])
    await ctx.reply(f'{test}')
    # await ctx.reply(f'**teste** {ctx.message.author.mention} {user_id}')

async def add_arrows(message):
    await message.add_reaction(emojis.EMOJI_LEFT) # left arrow
    await message.add_reaction(emojis.EMOJI_RIGHT) # right arrow

bot.run( TOKEN )