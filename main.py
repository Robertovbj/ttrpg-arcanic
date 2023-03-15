import discord as dc
from tabulate import tabulate
from discord.ext import commands
from models.page import Page
from models.stats import StatsPage
from models.harm import HarmPage
from models.hx import HxPage
from models.moves import MovesPage, Moves
from models.improvements import ImprovementPage
from models.inventory import InventoryPage
from models.page_manager import PageManager
from models.playbook import Playbook
from models.stats_sets import StatsSets
from models.character import NewCharacterPage, ChooseSetPage, Character
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

# @bot.command()
# async def checksheet(ctx: commands.Context, tag: dc.User = None):
    
#     author = ''
#     server = str(ctx.guild.id)

#     try:
#         if tag is None:
#             author = str(ctx.author.id)
#         elif not isinstance(tag, dc.User):
#             await ctx.reply("To check someone's else sheet, please use ```/checksheet @user```")
#             return
#         else:
#             author = str(tag.id)
#     except commands.errors.UserNotFound:
#         print('test')
#         await ctx.reply("User not found.")
#         return

#     if not Character().check_if_exists(author, server):
#         await ctx.reply("No character found on this server.")
#         return
    
    

#     pages = [
#         StatsPage(),
#         HxPage(),
#         HarmPage(),
#         MovesPage(),
#         ImprovementPage(),
#         InventoryPage()
#     ]
#     page_manager = PageManager("Name: Dou", "Playbook: The Angel", pages)

#     embed = dc.Embed.from_dict(page_manager.get_embed_dict())
#     msg = await ctx.reply(embed=embed)

#     await add_arrows(msg)

#     while True:
#         try:
#             reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=lambda r, u: check(r, u, ctx, emojis.ARROWS_LIST))

#             await turn_pages(msg, reaction, user, page_manager)
#         except:
#             break

@bot.command()
async def createsheet(ctx: commands.Context, name: str):
    """Create a new character"""

    if Character().check_if_exists(str(ctx.author.id), str(ctx.guild.id)):
        await ctx.reply("You already have a character sheet created in this server.")
        return

    playbooks = Playbook().get_playbooks()
    playbook_count = len(playbooks)
    pages = []

    for i in range(0, playbook_count, 10):
        # Extract the "name" element from each inner list and concatenate them into a string
        batch_playbooks = "\n".join(str(inner_list[1]) for inner_list in playbooks[i:i+10])
        # Makes a emoji string with the same size as the playbook list
        batch_emojis = "\n".join(emoji for emoji in emojis.NUMBER_LIST[0:batch_playbooks.count("\n")+1])
        pages.append( NewCharacterPage(batch_playbooks, batch_emojis) ) 

    pageManager = PageManager(f"Name: {name}", pages, "Playbook: Choosing...")

    embed = dc.Embed.from_dict(pageManager.get_embed_dict())
    msg = await ctx.reply(embed=embed)

    # Adding emojis reactions
    for i in emojis.NUMBER_LIST:
        await msg.add_reaction(i)
    
    await add_arrows(msg)
    
    playbook_choice = -1

    while True:
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=lambda r, u: check_reaction(r, u, ctx, emojis.ARROWS_LIST + emojis.NUMBER_LIST))

            if str(reaction) in emojis.ARROWS_LIST:
                await turn_pages(msg, reaction, user, pageManager)
            elif str(reaction) in emojis.NUMBER_LIST:
                playbook_choice = (pageManager.get_current_page_index() * 10)+(emojis.NUMBER_LIST.index(str(reaction))+1)
                if playbook_choice > 18:
                    await ctx.reply("Please select a valid option")
                    await msg.remove_reaction(reaction, user)
                else:
                    break

        except:
            break
    
    if playbook_choice != -1:
        # Removes all reactions
        await msg.clear_reactions()

        # Gets sets and prepare them
        stats_sets = StatsSets().get_stats_sets_for_pb(playbook_choice)
        stats_list = []
        for i in range(len(stats_sets)):
            stats_list.append([emojis.NUMBER_LIST[i], stats_sets[i][1], stats_sets[i][2], stats_sets[i][3], stats_sets[i][4], stats_sets[i][5]])

        # Creates table for discord
        table = tabulate(stats_list, headers=[f"{emojis.INVISIBLE}", "Cool", "Hard", "Hot", "Sharp", "Weird"])
        pages = [ChooseSetPage(f"```{table}```")]

        # Resets pages, as they wont be used anymore
        pageManager = PageManager(f"{name}", pages, description=f"Playbook: {playbooks[playbook_choice-1][1]}", thumbnail=playbooks[playbook_choice-1][3])

        embed = dc.Embed.from_dict(pageManager.get_embed_dict())
        await msg.edit(embed=embed)

        # Adding emojis reactions
        for i in emojis.NUMBER_LIST[0:4]:
            await msg.add_reaction(i)
        
        set_choice = -1

        while True:
            try:
                reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=lambda r, u: check_reaction(r, u, ctx, emojis.NUMBER_LIST[0:4]))

                if str(reaction) in emojis.NUMBER_LIST[0:4]:
                    set_choice = emojis.NUMBER_LIST.index(str(reaction))+1
                    break

            except:
                break

        if set_choice != -1:

            data = {
                'name': name,
                'playbook': playbook_choice,
                'user': str(ctx.author.id),
                'server': str(ctx.guild.id),
                'image': str(playbooks[playbook_choice-1][3]),
                'stats': {
                    'cool': stats_sets[set_choice-1][1],
                    'hard': stats_sets[set_choice-1][2],
                    'hot': stats_sets[set_choice-1][3],
                    'sharp': stats_sets[set_choice-1][4],
                    'weird': stats_sets[set_choice-1][5]
                }
            }

            text = Character().create_new(data)

            await ctx.reply("Character created successfully" if text == None else text)

@bot.command()
async def moves(ctx: commands.Context):
    """Command to list all moves stored in the database"""
    moves = Moves().get_all_moves()
    playbooks = Playbook().get_names()
    playbooks.insert(0, (0, "Basic"))
    pages = []

    pages = iterate_moves(moves, playbooks, pages)

    page_manager = PageManager("Moves list", pages)

    embed = dc.Embed.from_dict(page_manager.get_embed_dict())
    msg = await ctx.reply(embed=embed)

    await add_arrows(msg)

    while True:
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=lambda r, u: check_reaction(r, u, ctx, emojis.ARROWS_LIST))

            await turn_pages(msg, reaction, user, page_manager)
        except:
            break

@bot.command()
async def snow(ctx):
    """Test command. Should be removed for release"""
    server_id = str(ctx.guild.id)
    await ctx.reply(f'{server_id}')
    # await ctx.reply(f'**teste** {ctx.message.author.mention} {user_id}')

async def add_arrows(message: dc.Message):
    """Add arrow_lef and arrow_right to the message. Useful for paging"""
    await message.add_reaction(emojis.EMOJI_LEFT) # left arrow
    await message.add_reaction(emojis.EMOJI_RIGHT) # right arrow

async def turn_pages(message: dc.Message, reaction: dc.Reaction, user: dc.User | dc.Member, page_manager: PageManager):
    """Turn pages on a discord embed."""
    if str(reaction.emoji) == emojis.EMOJI_LEFT:
        page_manager.turn_page(-1)
    elif str(reaction.emoji) == emojis.EMOJI_RIGHT:
        page_manager.turn_page(1)

    embed = dc.Embed.from_dict(page_manager.get_embed_dict())
    await message.edit(embed=embed)
    await message.remove_reaction(reaction, user)

def check_reaction(reaction: dc.Reaction, user: dc.User | dc.Member, ctx: commands.Context, emojis_list: list[str]) -> bool:
    """Checks if it was the message author that reacted to 
    the message, and if the reaction is on the valid reactions list."""
    return user == ctx.author and str(reaction.emoji) in emojis_list

def iterate_moves(moves: list[tuple], playbooks: list[tuple], pages: list, special: str = None) -> list[Page]:
    """Iterate through the moves list, adding which type
    of move it is before the list of moves of the same type,
    creating a new page for each 20 moves. Return the list of MovesPage
    created."""
    for i in range(0, len(moves), 20):
        batch_moves = "\n".join(str(moves[j][1]) if moves[j-1][2] == moves[j][2] else f"\n**{playbooks[moves[j][2]][1]}**\n{moves[j][1]}" for j in range(i, len(moves[i:i+20])+i))
        pages.append(MovesPage(batch_moves, special))
    return pages

bot.run( TOKEN )