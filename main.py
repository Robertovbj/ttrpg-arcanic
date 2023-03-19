import discord as dc
from tabulate import tabulate
import asyncio
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

PREFIX = '!'

intents = dc.Intents.all()
bot = commands.Bot( command_prefix=f'{PREFIX}', intents=intents )
bot.remove_command("help")
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

@bot.command(usage=f"{PREFIX}createsheet <name>")
async def createsheet(ctx: commands.Context, name: str):
    '''Create a new character with the specified name.
    To use two or more names, encase them with quotes.
    
    Example:
    `!createsheet "Will Smith"`'''

    character = Character(str(ctx.author.id), str(ctx.guild.id))

    if character.check_if_exists():
        await ctx.reply("You already have a character sheet created in this server.")
        return
    if character.check_if_exists_name(name):
        await ctx.reply(f"A character named {name} already exists on this server. Please use another name.")
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
            reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=lambda r, u: check_reaction(r, u, ctx, emojis.ARROWS_LIST + emojis.NUMBER_LIST))

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
                reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=lambda r, u: check_reaction(r, u, ctx, emojis.NUMBER_LIST[0:4]))

                if str(reaction) in emojis.NUMBER_LIST[0:4]:
                    set_choice = emojis.NUMBER_LIST.index(str(reaction))+1
                    break

            except:
                break

        if set_choice != -1:

            data = {
                'name': name,
                'playbook': playbook_choice,
                'image': str(playbooks[playbook_choice-1][3]),
                'stats': {
                    'cool': stats_sets[set_choice-1][1],
                    'hard': stats_sets[set_choice-1][2],
                    'hot': stats_sets[set_choice-1][3],
                    'sharp': stats_sets[set_choice-1][4],
                    'weird': stats_sets[set_choice-1][5]
                }
            }

            text = character.create_new(data)

            await ctx.reply("Character created successfully" if text == None else text)

@createsheet.error
async def create_sheet_error(ctx: commands.Context, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply(f'Please specify your character\'s name. Example: `{PREFIX}createsheet "Will Smith"`')

@bot.command(usage=f"{PREFIX}deletesheet")
async def deletesheet(ctx: commands.Context):
    """Delete your character **FOREVER**. 
    Will ask for confirmation to avoid accidents."""

    character = Character(str(ctx.author.id), str(ctx.guild.id))

    if not character.check_if_exists():
        await ctx.reply("No character found on this server.")
        return

    char_name = character.get_character_name()

    confirmation_bot = await ctx.reply(f'Are you sure you want to delete your character? This action is _**IRREVERSIBLE**_.\nType "{char_name}" to confirm.')

    try:
        confirm_message = await bot.wait_for('message', timeout=25.0, check= lambda m: check_confirm_message(m, ctx, char_name))
    except asyncio.TimeoutError:
        await confirmation_bot.edit(content='Confirmation timed out. Character not deleted.')
    else:
        try:
            character.delete_character()
            await ctx.send('Character deleted successfully.')
        except:
            await ctx.send('Something went wrong.')

@bot.command(brief = "Adds exp to your character", usage = f"{PREFIX}getexp <amount>")
async def getexp(ctx: commands.Context, amount):
    """Add specified amount of exp to your character.
    Also calculates and shows the amount of improvement points."""
    
    character = Character(str(ctx.author.id), str(ctx.guild.id))

    if not character.check_if_exists():
        await ctx.reply("No character found on this server.")
        return
    
    try:
        # Deals with the possibility of wrong user input
        amount = int(amount)
    except:
        await ctx.reply(f"To get exp, please follow the example: ```{PREFIX}getexp 2```")
        return
    
    try:
        imp = character.add_exp(amount)
    except:
        await ctx.reply(f'Sorry, something went wrong.')
        return
    else:
        imp_text = ""
        if imp > 0:
            imp_text = f" You have {imp} improvement points."
        await ctx.reply(f'{amount} points of exp added.{imp_text}')

@getexp.error
async def get_exp_error(ctx: commands.Context, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply(f"Please specify the amount of exp to get. Example: `{PREFIX}getexp 2`")

@bot.command(usage = f"{PREFIX}getbarter <amount>")
async def getbarter(ctx: commands.Context, amount):
    """Add specified amount of barter to your character."""
    
    character = Character(str(ctx.author.id), str(ctx.guild.id))

    if not character.check_if_exists():
        await ctx.reply("No character found on this server.")
        return
    
    try:
        # Deals with the possibility of wrong user input
        amount = int(amount)
    except:
        await ctx.reply(f"To get barter, please follow the example: `{PREFIX}getbarter 2`")
        return
    
    if amount < 1:
        await ctx.reply(f"Barter amount needs to be a positive integer.")
        return
    
    try:
        barter = character.add_barter(amount)
    except:
        await ctx.reply(f'Sorry, something went wrong.')
        return
    else:
        await ctx.reply(f'{amount}-barter added. You have now {barter}-barter.')

@getbarter.error
async def get_barter_error(ctx: commands.Context, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply(f"Please specify the amount of exp to get. Example: `{PREFIX}getbarter 2`")

@bot.command(usage = f"{PREFIX}usebarter <amount>")
async def usebarter(ctx: commands.Context, amount):
    """Spends specified amount of barter."""
    
    character = Character(str(ctx.author.id), str(ctx.guild.id))

    if not character.check_if_exists():
        await ctx.reply("No character found on this server.")
        return
    
    try:
        # Deals with the possibility of wrong user input
        amount = int(amount)
    except:
        await ctx.reply(f"To spend barter, please follow the example: `{PREFIX}usebarter 2`")
        return
    
    if amount < 1:
        await ctx.reply(f"Barter amount needs to be a positive integer.")
        return
    
    try:
        barter = character.add_barter(-amount)
    except:
        await ctx.reply(f'Sorry, something went wrong.')
        return
    else:
        if barter < 0:
            await ctx.reply(f"You can't have negative barter.")
        else:
            await ctx.reply(f'{amount}-barter spent. You have now {barter}-barter.')

@usebarter.error
async def use_barter_error(ctx: commands.Context, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply(f"Please specify the amount of exp to spend. Example: `{PREFIX}usebarter 2`")

@bot.command(usage = f"{PREFIX}moves")
async def moves(ctx: commands.Context):
    """Lists all moves available."""
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

@bot.command(usage = f"{PREFIX}mymoves")
async def mymoves(ctx: commands.Context):
    """Lists your character's moves."""
    character = Character(str(ctx.author.id), str(ctx.guild.id))

    if not character.check_if_exists():
        await ctx.reply("No character found on this server.")
        return
    
    moves, special = character.get_char_moves()
    playbooks = Playbook().get_names()
    playbooks.insert(0, (0, "Basic"))
    char_info = character.get_basic_profile()
    pages = []

    pages = iterate_moves(moves, playbooks, pages, special)

    pageManager = PageManager(f"Name: {char_info[1]}", pages, f"Playbook: {char_info[2]}", char_info[3])

    embed = dc.Embed.from_dict(pageManager.get_embed_dict())
    await ctx.reply(embed=embed)

@bot.command(usage = f"{PREFIX}harminfo")
async def harminfo(ctx: commands.Context):
    """Shows your character's harms and conditions."""

    character = Character(str(ctx.author.id), str(ctx.guild.id))

    if not character.check_if_exists():
        await ctx.reply("No character found on this server.")
        return

    harms = character.get_harms()
    char_info = character.get_basic_profile()

    pages = [HarmPage(harms)]

    pageManager = PageManager(f"Name: {char_info[1]}", pages, f"Playbook: {char_info[2]}", char_info[3])

    embed = dc.Embed.from_dict(pageManager.get_embed_dict())
    await ctx.reply(embed=embed)

@bot.command(usage = f"{PREFIX}takeharm <amount>")
async def takeharm(ctx: commands.Context, amount):
    """Add specified amount of harm to your character.
    Also calculates and gives you a warning if you're going to die."""
    character = Character(str(ctx.author.id), str(ctx.guild.id))

    if not character.check_if_exists():
        await ctx.reply("No character found on this server.")
        return
    
    try:
        # Deals with the possibility of wrong user input
        amount = int(amount)
    except:
        await ctx.reply(f"To take harm, please follow the example: ```{PREFIX}takeharm 2```")
        return
    
    if amount < 1:
        await ctx.reply(f"""Please use only positive numbers, as the following example: ```{PREFIX}takeharm 1```\nIf you want to heal your harms, use: ```{PREFIX}healharm [amount]``` """)
        return
    
    harms = character.get_harms()
    char_info = character.get_basic_profile()
    harm_total = harms[0] + amount
    how_dead = ''

    if harm_total > 6:
        how_dead = f"_You'll **die**_, and you **won't be able to be revived**, since your harm exceeds the limit by {harm_total - 6} extra points."
        harm_total = 6
    elif harm_total == 6:
        how_dead = f"_You'll **die**_, but **can still be revived**."

    harms = (harm_total,)+ harms[1:6]

    pages = [HarmPage(harms)]

    pageManager = PageManager(f"Name: {char_info[1]}", pages, f"Playbook: {char_info[2]}", char_info[3])

    embed = dc.Embed.from_dict(pageManager.get_embed_dict())
    confirmation_bot = await ctx.reply(content=f"This is how much harm you'll have after confirming. {how_dead} Type 'Confirm' to proceed.", embed=embed)

    try:
        confirm_message = await bot.wait_for('message', timeout=25.0, check= lambda m: check_confirm_message(m, ctx, "Confirm"))
    except asyncio.TimeoutError:
        await confirmation_bot.edit(content='Confirmation timed out. Harm not taken.')
    else:
        try:
            character.update_harm(harms[0])
        except:
            await ctx.reply(f'Sorry, something went wrong.')
            return
        else:
            await ctx.reply(f'You take {amount}-harm. Ouch!')

@takeharm.error
async def take_harm_error(ctx: commands.Context, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply(f"Please specify the amount of harm to take. Example: `{PREFIX}takeharm 2`")

@bot.command(usage = f"{PREFIX}healharm <amount>")
async def healharm(ctx: commands.Context, amount):
    """Heal specified amount of harm on your character."""
    character = Character(str(ctx.author.id), str(ctx.guild.id))

    if not character.check_if_exists():
        await ctx.reply("No character found on this server.")
        return
    
    try:
        # Deals with the possibility of wrong user input
        amount = int(amount)
    except:
        await ctx.reply(f"To heal harm, please follow the example: ```{PREFIX}healharm 2```")
        return
    
    if amount < 1:
        await ctx.reply(f"""Please use only positive numbers, as the following example: ```{PREFIX}healharm 1```\nIf you want to take harm, use: ```{PREFIX}takeharm [amount]``` """)
        return
    
    harms = character.get_harms()
    char_info = character.get_basic_profile()
    harm_total = harms[0] - amount

    if harm_total < 0:
        harm_total = 0

    harms = (harm_total,)+ harms[1:6]

    pages = [HarmPage(harms)]

    pageManager = PageManager(f"Name: {char_info[1]}", pages, f"Playbook: {char_info[2]}", char_info[3])

    embed = dc.Embed.from_dict(pageManager.get_embed_dict())
    confirmation_bot = await ctx.reply(content=f"This is how much harm you'll have after confirming. Type 'Confirm' to proceed.", embed=embed)

    try:
        confirm_message = await bot.wait_for('message', timeout=15.0, check= lambda m: check_confirm_message(m, ctx, "Confirm"))
    except asyncio.TimeoutError:
        await confirmation_bot.edit(content='Confirmation timed out. Harm not healed.')
    else:
        try:
            character.update_harm(harms[0])
        except:
            await ctx.reply(f'Sorry, something went wrong.')
            return
        else:
            await ctx.reply(f'You heal {amount}-harm. Nice.')

@healharm.error
async def heal_harm_error(ctx: commands.Context, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply(f"Please specify the amount of harm to heal. Example: `{PREFIX}healharm 2`")

@bot.command(usage = f"{PREFIX}fullheal")
async def fullheal(ctx: commands.Context):
    """Fully heals your character."""
    character = Character(str(ctx.author.id), str(ctx.guild.id))

    if not character.check_if_exists():
        await ctx.reply("No character found on this server.")
        return
    
    harms = character.get_harms()

    harms = (0,)+ harms[1:6]

    confirmation_bot = await ctx.reply(content=f"Confirming will fully heal your character (you keep your debilities). Type 'Confirm' to proceed.")

    try:
        confirm_message = await bot.wait_for('message', timeout=15.0, check= lambda m: check_confirm_message(m, ctx, "Confirm"))
    except asyncio.TimeoutError:
        await confirmation_bot.edit(content='Confirmation timed out. Harm not healed.')
    else:
        try:
            character.update_harm(harms[0])
        except:
            await ctx.reply(f'Sorry, something went wrong.')
            return
        else:
            await ctx.reply(f'You\'re now fully healed.')

@bot.command(usage = f"{PREFIX}fullhealc", hidden=True)
async def fullhealc(ctx: commands.Context):
    """Fully heals your character, including debilities."""
    character = Character(str(ctx.author.id), str(ctx.guild.id))

    if not character.check_if_exists():
        await ctx.reply("No character found on this server.")
        return

    harms = (0, 0, 0, 0, 0, 0)

    confirmation_bot = await ctx.reply(content=f"Confirming will fully heal your character, including debilities. Type 'Confirm' to proceed.")

    try:
        confirm_message = await bot.wait_for('message', timeout=15.0, check= lambda m: check_confirm_message(m, ctx, "Confirm"))
    except asyncio.TimeoutError:
        await confirmation_bot.edit(content='Confirmation timed out. Harm not healed.')
    else:
        try:
            character.update_dharms(harms)
        except:
            await ctx.reply(f'Sorry, something went wrong.')
            return
        else:
            await ctx.reply(f'You\'re now fully healed.')

@bot.command(usage = f"{PREFIX}hxinfo [name]")
async def hxinfo(ctx: commands.Context, name: str = None):
    """Lists all HX info from your character. If a character's name
    is used as argument, it lists only the HX towards that character.
    
    Examples:
    `!hxinfo` - Shows all HX info
    `!hxinfo \"Will Smith\"` - Shows the HX towards Will Smith"""

    author = str(ctx.author.id)
    server = str(ctx.guild.id)

    character = Character(author, server)
    char_info = character.get_basic_profile()

    if not character.check_if_exists():
        await ctx.reply("No character found on this server.")
        return

    pages = []
    if name is None:
        hx = character.get_hx_list()
        pages = [HxPage(hx)]
    else: 
        if not character.check_if_exists_name(name):
            await ctx.reply(f"No character named {name} found on this server.")
            return
        hx = character.get_hx_ind(name)
        if not len(hx) == 0 and not hx[0][2] == 0:
            pages = [HxPage(hx)]
        else:
            await ctx.reply(content="You don't seem to have any HX with this character.")
            return

    page_manager = PageManager(f"Name: {char_info[1]}", pages, f"Playbook: {char_info[2]}", char_info[3])

    embed = dc.Embed.from_dict(page_manager.get_embed_dict())
    await ctx.reply(embed=embed)

@bot.command(usage = f"{PREFIX}hxinfo <name> <amount> [| <name> <amount>]...")
async def hxadjust(ctx: commands.Context, *args: str):
    """Adjusts HX towards other characters. Can specify
    multiple characters at once by separating the \"character name, value\"
    pair with \"|\". If the amount is -4 or 4, it will set to 
    -1 and 1 respectively, and _warn_ you that you can get exp points
    for that (it will not give you exp automatically).
    
    Example:
    !hxadjust "Will Smith" 1 - Set HX towards Will Smith to 1.
    !hxadjust "Will Smith" 1 | "Leonardo Dicaprio" 3 - Set HX 
        towards Will Smith to 1 and 3 towards Leonardo Dicaprio."""

    if not args:
        await ctx.reply("Please provide at least one pair of character_name and number to adjust HX.")
        return

    character = Character(str(ctx.author.id), str(ctx.guild.id))

    if not character.check_if_exists():
        await ctx.reply("No character found on this server.")
        return

    args_pairs = []
    exp_message = ""

    try:
        for i in range(0, len(args), 3):
            value = int(args[i+1])
            name = args[i]
            if not character.check_if_exists_name(name):
                await ctx.reply(f"No character named {name} found on this server.")
                return
            if value > 4 or value < -4:
                await ctx.reply(f"The HX value should be between -4 and 4.")
                return
            if value == -4:
                exp_message += f"you achieved -4 HX with {name}\n"
                value = -1
            if value == 4:
                exp_message += f"you achieved 4 HX with {name}\n"
                value = 1
            args_pairs.append([name, value])
    except:
        await ctx.reply(content=f'Sorry, something went wrong. Please check your command syntax, it should look like this: ```{PREFIX}hxadjust "character name 1" 2 | "character name 2" 1```')
        return

    message = character.update_hx(args_pairs)

    if message is None:
        if not exp_message == "":
            exp_message = " You also got 1 exp for each of the following:\n" + exp_message + "All values were reseted to -1 or 1 accordingly. (You need to get your exp manually. This is just a warning)"
        await ctx.reply(f"HX adjusted successfully.{exp_message}")
    else:
        await ctx.reply(message)

@bot.command()
async def learnmoves(ctx: commands.Context, *args: str):

    character = Character(str(ctx.author.id), str(ctx.guild.id))

    if not character.check_if_exists():
        await ctx.reply("No character found on this server.")
        return
    
    # Makes a string like 'Move 1|Move 2|Move 3' and then splits it on '|'s
    # returning a list
    arg_list = "".join(args).split("|")
    # for arg in arg_list:
    #     await ctx.send(f"Argument is: {arg}")

@bot.command(usage = f"{PREFIX}myimprovements")
async def myimprovements(ctx: commands.Context):
    """Lists your character's improvements."""
    character = Character(str(ctx.author.id), str(ctx.guild.id))

    if not character.check_if_exists():
        await ctx.reply("No character found on this server.")
        return
    
    improvements = character.get_improvements()
    char_info = character.get_basic_profile()
    exp, imp_points = character.get_exp()
    pages = [ImprovementPage(exp, imp_points, improvements)]

    pageManager = PageManager(f"Name: {char_info[1]}", pages, f"Playbook: {char_info[2]}", char_info[3])

    embed = dc.Embed.from_dict(pageManager.get_embed_dict())
    await ctx.reply(embed=embed)

@bot.command(usage = f"{PREFIX}improve <number> [| <number>]...")
async def improve(ctx: commands.Context, *args: str):
    """Get the specified improvement. Can specify
    multiple improvements at once by separating the \"value\"
    with \"|\". The number must be between 1 and 16 (both included).
    It will **_NOT_** add the stats to your sheet if the improvement
    says you should, it must be done manually.
    
    Example:
    !improve 1 - Get the first improvement.
    !improve 1 | 3 - Get the first and the third improvements."""

    if not args:
        await ctx.reply("Please provide at least one improvement to add.")
        return

    character = Character(str(ctx.author.id), str(ctx.guild.id))

    if not character.check_if_exists():
        await ctx.reply("No character found on this server.")
        return

    args_imp = []
    my_improvements = character.get_improvements()
    _, imp_points = character.get_exp()

    try:
        for i in range(0, len(args), 2):
            value = int(args[i])
            if value < 1 or value > 16:
                await ctx.reply(f"The improvement number must between 1 and 16 (both included).")
                return
            if my_improvements[value-1][0] == 1:
                await ctx.reply(f"You already have the '{my_improvements[value-1][1]}' improvement.")
                return
            args_imp.append(my_improvements[value-1][2])
    except:
        await ctx.reply(content=f'Sorry, something went wrong. Please check your command syntax, it should look like this: ```{PREFIX}improve 1 | 2```')
        return

    message = ''

    confirmation_bot = await ctx.reply(content=f"Please check if you typed the right improvements and confirm 'Confirm' to proceed.")

    try:
        confirm_message = await bot.wait_for('message', timeout=25.0, check= lambda m: check_confirm_message(m, ctx, "Confirm"))
    except asyncio.TimeoutError:
        await confirmation_bot.edit(content='Confirmation timed out. Action canceled.')
    else:
        if len(args_imp) > imp_points:
            await ctx.reply("Sorry, it seems you don't have enough improvement points.")
        else:
            message = character.add_improvement(args_imp)

        if message is None:
            await ctx.reply(f"You improved successfully (Remember to add the stat to your sheet if thats the case, this action is **_NOT_** done automatically).")
        else:
            await ctx.reply(message)

@bot.command(usage = f"{PREFIX}removeimprovement <number> [| <number>]...")
async def removeimprovement(ctx: commands.Context, *args: str):
    """Remove the specified improvement. Can specify
    multiple improvements at once by separating the \"value\"
    with \"|\". The number must be between 1 and 16 (both included).
    It will **_NOT_** remove the stats from your sheet if the improvement
    was about adding it, it must be done manually.
    
    Example:
    !removeimprovement 1 - Remove the first improvement.
    !removeimprovement 1 | 3 - Remove the first and the third improvements."""

    if not args:
        await ctx.reply("Please provide at least one improvement to remove.")
        return

    character = Character(str(ctx.author.id), str(ctx.guild.id))

    if not character.check_if_exists():
        await ctx.reply("No character found on this server.")
        return

    args_imp = []
    my_improvements = character.get_improvements()

    try:
        for i in range(0, len(args), 2):
            value = int(args[i])
            if value < 1 or value > 16:
                await ctx.reply(f"The improvement number must between 1 and 16 (both included).")
                return
            if my_improvements[value-1][0] != 1:
                await ctx.reply(f"You don't have the '{my_improvements[value-1][1]}' improvement.")
                return
            args_imp.append(my_improvements[value-1][2])
    except:
        await ctx.reply(content=f'Sorry, something went wrong. Please check your command syntax, it should look like this: ```{PREFIX}removeimprovement 1 | 2```')
        return

    confirmation_bot = await ctx.reply(content=f"This action should only be used in case of error while getting a improvement. You'll also get your improvement points back. Type 'Confirm' to proceed.")

    try:
        confirm_message = await bot.wait_for('message', timeout=25.0, check= lambda m: check_confirm_message(m, ctx, "Confirm"))
    except asyncio.TimeoutError:
        await confirmation_bot.edit(content='Confirmation timed out. Action canceled.')
    else:
        message = character.remove_improvement(args_imp)

        if message is None:
            await ctx.reply(f"Improvements removed successfully. {len(args_imp)} improvement points added back to your sheet. (Remember to remove the stat from your sheet if thats the case, this action is **_NOT_** done automatically).")
        else:
            await ctx.reply(message)


@bot.command()
async def snow(ctx):
    """Test command. Should be removed for release"""
    print('@' + str(ctx.author.name))
    await ctx.send(content=f'@{ctx.author.name}')

@bot.command(usage=f"{PREFIX}help [command]")
async def help(ctx: commands.Context, cmd = None):
    """Shows this command."""

    if not cmd:
        # Show help message for all available commands
        cmd_names = ' '.join(f"`{cmd.name}`" for cmd in bot.commands)
        em = dc.Embed(title="Help", description=f"Use `{PREFIX}help <command>` extended information on a command.", color=ctx.author.color)
        em.add_field(name="Commands", value=f"{cmd_names}")
        await ctx.reply(embed = em)
    else:
        # Show help message for a specific command
        cmd_obj = bot.get_command(cmd)
        if not cmd_obj:
            em = dc.Embed(title="Help", description=f"Use `{PREFIX}help <command>` extended information on a command.", color=ctx.author.color)
            em.add_field(name="Error", value=f'Command `{cmd}` not found.')
            await ctx.reply(embed = em)
        else:
            em = dc.Embed(title=f"**{cmd_obj.name}**", description=f"{cmd_obj.help}")
            em.add_field(name="**Syntax**", value=f"`{cmd_obj.usage}`")
            await ctx.send(embed=em)

# Helper functions
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

def check_confirm_message(message: dc.Message, ctx: commands.Context, text: str):
    return message.content == text and message.channel == ctx.channel and message.author == ctx.author

def iterate_moves(moves: list[tuple], playbooks: list[tuple], pages: list, special: str = None) -> list[Page]:
    """Iterate through the moves list, adding which type
    of move it is before the list of moves of the same type,
    creating a new page for each 20 moves. Return the list of MovesPage
    created."""
    if len(moves) == 0:
        pages.append(MovesPage('', special))
        return pages
    
    for i in range(0, len(moves), 20):
        batch_moves = "\n".join(str(moves[j][1]) if moves[j-1][2] == moves[j][2] else f"\n**{playbooks[moves[j][2]][1]}**\n{moves[j][1]}" for j in range(i, len(moves[i:i+20])+i))
        if i == 0:
            print(f"{batch_moves} \n\n {special}")
            pages.append(MovesPage(batch_moves, special))
        else:
            pages.append(MovesPage(batch_moves))
    return pages

bot.run( TOKEN )