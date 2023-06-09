import discord as dc
from tabulate import tabulate
import asyncio
import re
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
from models.character import NewCharacterPage, ChooseSetPage, Character, AllCharacters
from configs.database import Database
from config import TOKEN  # Import the bot token from the config module
import emojis

PREFIX = '!'

intents = dc.Intents.all()
bot = commands.Bot( command_prefix=f'{PREFIX}', intents=intents )
bot.remove_command("help")
db = Database()

def lowercase_converter(arg: str) -> str:
    return arg.lower()

@bot.command(usage=f"{PREFIX}checksheet [name]", aliases=['sheet'])
async def checksheet(ctx: commands.Context, char: str = None):
    """Check your character's full sheet.
    If a name is passed as argument, will show
    the named character's sheet instead.
    
    Examples:
    `!checksheet` - Shows your character's full sheet
    `!checksheet "Will Smith"` - Shows Will Smith's full sheet"""
    
    character = Character(str(ctx.author.id), str(ctx.guild.id))

    if char is None: # Checking for author's character
        if not character.check_if_exists():
            await ctx.reply("No character found on this server.")
            return
    else:
        if not character.check_if_exists_name(char):
            await ctx.reply(f"No character named {char} found on this server.")
            return
        character.change_user_by_name(char)
    
    char_info = character.get_basic_profile()

    # Gets this character moves and sets it
    moves, special = character.get_char_moves()
    playbooks = Playbook().get_names()
    playbooks.insert(0, (0, "Basic"))

    moves_txt = ''
    
    for i in range(len(moves)):
        moves_txt += f"{moves[i][1]}\n" if moves[i-1][2] == moves[i][2] and i != 0 else f"\n**{playbooks[moves[i][2]][1]}**\n{moves[i][1]}\n"

    pages = [
        StatsPage(character.get_stats()),
        HxPage(character.get_hx_list()),
        HarmPage(character.get_harms()),
        MovesPage(moves_txt, special),
        ImprovementPage(*character.get_exp(), character.get_improvements()),
        InventoryPage(character.get_inventory(), character.get_barter())
    ]

    page_manager = PageManager(f"Name: {char_info[1]}", pages, f"Playbook: {char_info[2]}", char_info[3])

    embed = dc.Embed.from_dict(page_manager.get_embed_dict())
    msg = await ctx.reply(embed=embed)

    await add_arrows(msg)

    while True:
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=lambda r, u: check_reaction(r, u, ctx, emojis.ARROWS_LIST, msg))

            await turn_pages(msg, reaction, user, page_manager)
        except:
            break

@bot.command(usage=f"{PREFIX}createsheet <name>", aliases=['csheet'])
async def createsheet(ctx: commands.Context, name: str):
    '''Create a new character with the specified name.
    To use two or more names, encase them with quotes.
    Only **ONE** character is allowed per server.
    
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
            reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=lambda r, u: check_reaction(r, u, ctx, emojis.ARROWS_LIST + emojis.NUMBER_LIST, msg))

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
                reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=lambda r, u: check_reaction(r, u, ctx, emojis.NUMBER_LIST[0:4], msg))

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
            quarantine = '' if playbook_choice != 15 else ' and, since you\'re a Quarantine, to set your "Weird" stats manually.'

            await ctx.reply(f"Character created successfully. Don't forget to get your skills{quarantine}." if text == None else text)

@createsheet.error
async def create_sheet_error(ctx: commands.Context, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply(f'Please specify your character\'s name. Example: `{PREFIX}createsheet "Will Smith"`')

@bot.command(usage=f"{PREFIX}deletesheet", aliases=['dsheet'])
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
        confirmation_bot = await ctx.reply(f'Last chance. Type \'Confirm\' to continue.')

        try:
            confirm_message = await bot.wait_for('message', timeout=25.0, check= lambda m: check_confirm_message(m, ctx, "Confirm"))
        except asyncio.TimeoutError:
            await confirmation_bot.edit(content='Confirmation timed out. Character not deleted.')
        else:
            try:
                character.delete_character()
                await ctx.send('Character deleted successfully.')
            except:
                await ctx.send('Something went wrong.')

@bot.command(usage=f"{PREFIX}highlight <stat1> <stat2>", aliases=['hl'])
async def highlight(ctx: commands.Context, stat_one: lowercase_converter, stat_two: lowercase_converter):
    """Highlights the two specified stats. Must inform both by name.
    
    Example:
    `!highlight Cool Weird` - Highlights Cool and Weird stats."""

    character = Character(str(ctx.author.id), str(ctx.guild.id))

    if not character.check_if_exists():
        await ctx.reply("No character found on this server.")
        return
    
    possible_stats = ['cool', 'hard', 'hot', 'sharp', 'weird']
    if stat_one not in possible_stats:
        await ctx.reply(f"There's no stat named {stat_one}.")
        return
    if stat_two not in possible_stats:
        await ctx.reply(f"There's no stat named {stat_two}.")
        return
    
    error = character.highlight(possible_stats.index(stat_one)+1, possible_stats.index(stat_two)+1)

    if error is None:
        await ctx.reply(f'Stats {stat_one} and {stat_two} are now highlighted.')
    else:
        await ctx.reply(f"{error}")

@highlight.error
async def highlight_error(ctx: commands.Context, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply(f'Please specify both stats to highlight as the following example: `{PREFIX}highlight Cool Weird`')

@bot.command(usage=f"{PREFIX}adjuststats <name> <value> [| <name> <value>]...", aliases=['astats'])
async def adjuststats(ctx: commands.Context, *args: str):
    """Adjust stats to specified number. Can specify
    multiple stats at once by separating the "stat, value"
    pair with "|".
    
    Example:
    `!adjuststats Cool 1` - Set Cool to 1.
    `!adjuststats Cool 1 | Hot 3` - Set Cool to 1 and Hot to 3."""

    if not args:
        await ctx.reply("Please provide at least one pair of stat_name and value to adjust stats.")
        return

    character = Character(str(ctx.author.id), str(ctx.guild.id))

    if not character.check_if_exists():
        await ctx.reply("No character found on this server.")
        return

    stats = []
    values = []
    possible_stats = ['cool', 'hard', 'hot', 'sharp', 'weird']

    try:
        for i in range(0, len(args), 3):
            value = int(args[i+1])
            name = lowercase_converter(args[i])
            if name not in possible_stats:
                await ctx.reply(f"There's no stat named {name}.")
                return
            stats.append(possible_stats.index(name)+1)
            values.append(value)
    except:
        await ctx.reply(content=f'Sorry, something went wrong. Please check your command syntax, it should look like this: ```{PREFIX}adjuststats Cool 2 | Weird 1```')
        return

    message = character.adjust_stats(stats, values)

    if message is None:
        await ctx.reply(f"Stats adjusted successfully.")
    else:
        await ctx.reply(message)

@bot.command(usage=f"{PREFIX}image <imgur_link>")
async def image(ctx: commands.Context, link: str):
    """Changes your character image to a new one provided by
    the user. The link should be a imgur link like the following:
    <https://i.imgur.com/JOf48jt.jpeg>"""

    character = Character(str(ctx.author.id), str(ctx.guild.id))

    if not character.check_if_exists():
        await ctx.reply("No character found on this server.")
        return
    
    if is_imgur_url(link):
        character.set_image(link)
        await ctx.reply("Image changed successfully.")
        return
    else:
        await ctx.reply(f"""It seems your URL is wrong. Be sure to get the URL to the _image_ not to the _gallery_.\nIt should look like this: <https://i.imgur.com/JOf48jt.jpeg>""")
        return

@image.error
async def image_error(ctx: commands.Context, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply(f'Please provide a imgur link. Example: `{PREFIX}image https://i.imgur.com/JOf48jt.jpeg`')

@bot.command(usage=f"{PREFIX}resetimage", aliases=['rimage'])
async def resetimage(ctx: commands.Context):
    """Resets your character's image. Will ask for confirmation."""

    character = Character(str(ctx.author.id), str(ctx.guild.id))

    if not character.check_if_exists():
        await ctx.reply("No character found on this server.")
        return
    
    confirmation_bot = await ctx.reply(content=f"This action requires confirmation since it will wipe your atual image **for good*. Type 'Confirm' to proceed.")

    try:
        confirm_message = await bot.wait_for('message', timeout=25.0, check= lambda m: check_confirm_message(m, ctx, "Confirm"))
    except asyncio.TimeoutError:
        await confirmation_bot.edit(content='Confirmation timed out. Action canceled.')
    else:
        character.reset_image()
        await ctx.reply("Image reseted to default.")

@bot.command(brief = "Adds exp to your character", usage = f"{PREFIX}addexp <amount>", aliases=['xp'])
async def addexp(ctx: commands.Context, amount):
    """Add specified amount of exp to your character. The amount can
    be negative in case of the need of exp removal.
    Also calculates and shows the amount of improvement points."""
    
    character = Character(str(ctx.author.id), str(ctx.guild.id))

    if not character.check_if_exists():
        await ctx.reply("No character found on this server.")
        return
    
    try:
        # Deals with the possibility of wrong user input
        amount = int(amount)
    except:
        await ctx.reply(f"To get exp, please follow the example: ```{PREFIX}addexp 2```")
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

@addexp.error
async def add_exp_error(ctx: commands.Context, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply(f"Please specify the amount of exp to get. Example: `{PREFIX}addexp 2`")

@bot.command(usage = f"{PREFIX}addbarter <amount>")
async def addbarter(ctx: commands.Context, amount):
    """Adds specified amount of barter to your character."""
    
    character = Character(str(ctx.author.id), str(ctx.guild.id))

    if not character.check_if_exists():
        await ctx.reply("No character found on this server.")
        return
    
    try:
        # Deals with the possibility of wrong user input
        amount = int(amount)
    except:
        await ctx.reply(f"To get barter, please follow the example: `{PREFIX}addbarter 2`")
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

@addbarter.error
async def get_barter_error(ctx: commands.Context, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply(f"Please specify the amount of exp to get. Example: `{PREFIX}addbarter 2`")

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

@bot.command(usage =f"givebarter <name> <amount>")
async def givebarter(ctx: commands.Context, name: str,  amount):
    """Gives the named character specified amount of 
    barter."""
    
    character = Character(str(ctx.author.id), str(ctx.guild.id))

    if not character.check_if_exists():
        await ctx.reply("No character found on this server.")
        return
    
    id_char = character.check_if_exists_name(name)
    if not id_char:
        await ctx.reply(f"No character named {name} found on this server.")
        return
    
    try:
        # Deals with the possibility of wrong user input
        amount = int(amount)
    except:
        await ctx.reply(f'To give barter, please follow the example: `{PREFIX}givebarter "Will Smith" 2`')
        return
    
    if amount < 1:
        await ctx.reply(f"Barter amount needs to be a positive integer.")
        return
    
    confirmation_bot = await ctx.reply(content=f"You're about to give {name} {amount}-barter. Type 'Confirm' to proceed.")

    try:
        confirm_message = await bot.wait_for('message', timeout=25.0, check= lambda m: check_confirm_message(m, ctx, "Confirm"))
    except asyncio.TimeoutError:
        await confirmation_bot.edit(content='Confirmation timed out. Action canceled.')
    else:
        try:
            barter = character.add_barter(-amount)
        except:
            await ctx.reply(f'Sorry, something went wrong.')
            return
        else:
            if barter < 0:
                await ctx.reply(f"You can't have negative barter.")
            else:
                try:
                    character.change_user_by_name(name)
                    barter = character.add_barter(amount)
                except:
                    await ctx.reply(f'Sorry, something went wrong. Please check sender\'s barter.')
                    return
                else:
                    await ctx.reply(f'Transaction complete. You gave {name} {amount}-barter.')

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
            reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=lambda r, u: check_reaction(r, u, ctx, emojis.ARROWS_LIST, msg))

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

    page_manager = PageManager(f"Name: {char_info[1]}", pages, f"Playbook: {char_info[2]}", char_info[3])

    embed = dc.Embed.from_dict(page_manager.get_embed_dict())
    msg = await ctx.reply(embed=embed)

    await add_arrows(msg)

    while True:
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=lambda r, u: check_reaction(r, u, ctx, emojis.ARROWS_LIST, msg))

            await turn_pages(msg, reaction, user, page_manager)
        except:
            break

@bot.command(usage = f"{PREFIX}harminfo", aliases=['charm'])
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

@bot.command(usage = f"{PREFIX}takeharm <amount>", aliases=['harm'])
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

@bot.command(usage = f"{PREFIX}takedebility <name>", aliases=['d'])
async def takedebility(ctx: commands.Context, name: lowercase_converter):
    """Marks a debility for your character. Remember,
    debilities are **PERMANENT**. Valid options are: 
    `shattered` `crippled` `disfigured` `broken`"""

    character = Character(str(ctx.author.id), str(ctx.guild.id))

    if not character.check_if_exists():
        await ctx.reply("No character found on this server.")
        return
    
    possible_debilities = ['shattered', 'crippled', 'disfigured', 'broken']

    if name not in possible_debilities:
        await ctx.reply(f"There's no debility named {name}.")
        return
    
    possible_columns = ['CHR_SHATTERED', 'CHR_CRIPPLED', 'CHR_DISFIGURED', 'CHR_BROKEN']
    column_name = possible_columns[possible_debilities.index(name)]

    if character.check_for_debility(column_name):
        await ctx.reply(f"You already are {name}.")
        return

    confirmation_bot = await ctx.reply(content=f"Taking a debility is a _**PERMANENT**_ decision. Type 'Confirm' to proceed.")

    try:
        confirm_message = await bot.wait_for('message', timeout=15.0, check= lambda m: check_confirm_message(m, ctx, "Confirm"))
    except asyncio.TimeoutError:
        await confirmation_bot.edit(content='Confirmation timed out. Action canceled.')
    else:
        message = character.add_debility(column_name)
        
        if message is None:
            await ctx.reply('Debility taken successfully.')
        else:
            await ctx.reply(message)

@takedebility.error
async def take_debility_error(ctx: commands.Context, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply(f"Please specify the debility to take. Example: `{PREFIX}takedebility Crippled`")

@bot.command(usage = f"{PREFIX}healharm <amount>", aliases=['heal'])
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

@bot.command(usage = f"{PREFIX}noharm")
async def noharm(ctx: commands.Context):
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

@bot.command(usage = f"{PREFIX}fullheal", hidden=True)
async def fullheal(ctx: commands.Context):
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

@bot.command(usage = f'{PREFIX}stabilize')
async def stabilize(ctx: commands.Context):
    """Adds or removes the _stabilized_ status from your character."""

    character = Character(str(ctx.author.id), str(ctx.guild.id))

    if not character.check_if_exists():
        await ctx.reply("No character found on this server.")
        return
    
    status = character.stabilize()

    if status == 0:
        await ctx.reply('You lose the "Stabilized" status.')
    else:
        await ctx.reply('You\'re now "Stabilized".')

@bot.command(usage = f"{PREFIX}hxinfo [name]", aliases=['h'])
async def hxinfo(ctx: commands.Context, name: str = None):
    """Lists all HX info from your character. If a character's name
    is used as argument, it lists only the HX towards that character.
    
    Examples:
    `!hxinfo` - Shows all HX info
    `!hxinfo "Will Smith"` - Shows the HX towards Will Smith"""

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
    multiple characters at once by separating the "character name, value"
    pair with "|". If the amount is -4 or 4, it will set to 
    -1 and 1 respectively, and _warn_ you that you can get exp points
    for that (it will not give you exp automatically).
    
    Example:
    `!hxadjust "Will Smith" 1` - Set HX towards Will Smith to 1.
    `!hxadjust "Will Smith" 1 | "Leonardo Dicaprio" 3` - Set HX 
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

@bot.command(usage=f"{PREFIX}learnmoves <move> [| <move>]...")
async def learnmoves(ctx: commands.Context, *args: str):
    """Learns named moves. To specify the move to learn,
    use `/moves`, copy it's name and paste it between double quotes.
    Can specify multiple moves at once by separating their names
    with "|".
    
    Examples:
    `!learnmoves "Sixth sense"` - Adds the move Sixth sense to your sheet.
    `!learnmoves "Sixth sense" | "Reality's fraying edge"` - Adds the moves
    Sixth sense and Reality's fraying edge to your sheet."""

    if not args:
        await ctx.reply("Please provide at least one move to learn.")
        return

    character = Character(str(ctx.author.id), str(ctx.guild.id))

    if not character.check_if_exists():
        await ctx.reply("No character found on this server.")
        return
    
    # Makes a string like 'Move 1|Move 2|Move 3' and then splits it on '|'s
    # returning a list
    arg_list = "".join(args).split("|")
    id_list = []

    for arg in arg_list:
        id = Moves().get_id_by_name(arg)
        if not id:
            await ctx.reply(f"Sorry, it seems the move {arg} doesn't exists.")
            return
        if character.has_the_moves(id):
            await ctx.reply(f"It seems you already have the move {arg}.")
            return
        id_list.append(id)
    
    message = character.add_moves(id_list)

    if message is None:
        await ctx.reply("Moves learned successfully.")
    else:
        await ctx.reply(message)

@bot.command(usage=f"{PREFIX}removemoves <move> [| <move>]...", aliases=['rmoves'])
async def removemoves(ctx: commands.Context, *args: str):
    """Removes named moves from your sheet. To specify the move to remove,
    use `/moves`, copy it's name and paste it between double quotes.
    Can specify multiple moves at once by separating their names
    with "|".
    
    Examples:
    `!removemoves "Sixth sense"` - Removes the move Sixth sense from your sheet.
    `!removemoves "Sixth sense" | "Reality's fraying edge"` - Removes the moves
    Sixth sense and Reality's fraying edge from your sheet."""

    if not args:
        await ctx.reply("Please provide at least one move to remove.")
        return

    character = Character(str(ctx.author.id), str(ctx.guild.id))

    if not character.check_if_exists():
        await ctx.reply("No character found on this server.")
        return
    
    # Makes a string like 'Move 1|Move 2|Move 3' and then splits it on '|'s
    # returning a list
    arg_list = "".join(args).split("|")
    id_list = []

    for arg in arg_list:
        id = Moves().get_id_by_name(arg)
        if not id:
            await ctx.reply(f"Sorry, it seems the move {arg} doesn't exists.")
            return
        chm_id = character.has_the_moves(id)
        if not chm_id:
            await ctx.reply(f"It seems you don't have the move {arg}.")
            return
        id_list.append(chm_id)
    
    confirmation_bot = await ctx.reply(content=f"This action should only be used in case of error while getting a move. Type 'Confirm' to proceed.")

    try:
        confirm_message = await bot.wait_for('message', timeout=25.0, check= lambda m: check_confirm_message(m, ctx, "Confirm"))
    except asyncio.TimeoutError:
        await confirmation_bot.edit(content='Confirmation timed out. Action canceled.')
    else:
        message = character.delete_moves(id_list)

        if message is None:
            await ctx.reply("Moves removed successfully.")
        else:
            await ctx.reply(message)

@bot.command(usage = f"{PREFIX}myimprovements", aliases=['myimp'])
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

@bot.command(usage = f"{PREFIX}improve <number> [| <number>]...", aliases=['imp'])
async def improve(ctx: commands.Context, *args: str):
    """Get the specified improvement. Can specify
    multiple improvements at once by separating the "value"
    with "|". The number must be between 1 and 16 (both included), 
    and can't be 12, 13 and 14 (check `finaladvance` and `newtype`
    commands). It will **_NOT_** add the stats to your sheet if the
    improvement says you should, it must be done manually.
    
    Example:
    `!improve 1` - Get the first improvement.
    `!improve 1 | 3` - Get the first and the third improvements."""

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

    # In case the character changed type
    if len(my_improvements) == 26:
        my_improvements = my_improvements[-10:] + my_improvements[10:-10] + my_improvements[:10]

    try:
        for i in range(0, len(args), 2):
            value = int(args[i])
            if value < 1 or value > 16 or value in [12, 13, 14]:
                await ctx.reply(f"The improvement number must between 1 and 16 (both included), and can't be 12, 13 and 14 (check `finaladvance` and `newtype` commands).")
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

@bot.command(usage = f"{PREFIX}removeimprovement <number> [| <number>]...", aliases=['rimp'])
async def removeimprovement(ctx: commands.Context, *args: str):
    """Remove the specified improvement. Can specify
    multiple improvements at once by separating the "value"
    with "|". The number must be between 1 and 16 (both included), 
    and can't be 12, 13 and 14 (check `finaladvance` and `newtype` 
    commands). It will **_NOT_** remove the stats from your sheet 
    if the improvement was about adding it, it must be done manually.
    
    Example:
    `!removeimprovement 1` - Remove the first improvement.
    `!removeimprovement 1 | 3` - Remove the first and the third improvements."""

    if not args:
        await ctx.reply("Please provide at least one improvement to remove.")
        return

    character = Character(str(ctx.author.id), str(ctx.guild.id))

    if not character.check_if_exists():
        await ctx.reply("No character found on this server.")
        return

    args_imp = []
    my_improvements = character.get_improvements()

    # In case the character changed type
    if len(my_improvements) == 26:
        my_improvements = my_improvements[-10:] + my_improvements[10:-10] + my_improvements[:10]

    try:
        for i in range(0, len(args), 2):
            value = int(args[i])
            if value < 1 or value > 16:
                await ctx.reply(f"The improvement number must between 1 and 16 (both included).")
                return
            if my_improvements[value-1][0] != 1:
                await ctx.reply(f"You don't have the '{my_improvements[value-1][1]}' improvement.")
                return
            if value in [12, 13, 14]:
                await ctx.reply(f"You can't remove the '{my_improvements[value-1][1]}' improvement.")
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

@bot.command(usage = f"{PREFIX}additem <amount> <name> <description> [| <amount> <name> <description>]...")
async def additem(ctx: commands.Context, *args: str):
    """Adds items to your inventory. Can specify multiple
    items at once by separating the "amount, name, description"
    group with "|". If the item already exists on your inventory,
    it will add it's amount and **keep** the old description (meaning
    it's good to keep item's names unique for each description).
    
    Example:
    `!additem 1 "Potion 1" "Heals 1 harm"` - Adds 1 "Potion 1" that
        "Heals 1 harm" to your inventory.
    `!additem 2 "Potion 1" "Heals 1 harm" | 1 "Potion 2" "Heals 2 harm"` 
        - Adds 2 "Potion 1" that "Heals 1 harm" and 1 "Potion 2" that 
        "Heals 2 harm" to your inventory."""

    if not args or len(args) < 3:
        await ctx.reply("Please provide at least one group of amount, item name and description to add.")
        return

    character = Character(str(ctx.author.id), str(ctx.guild.id))

    if not character.check_if_exists():
        await ctx.reply("No character found on this server.")
        return

    args_pairs = []

    try:
        for i in range(0, len(args), 4):
            value = int(args[i])
            name = args[i+1].capitalize()
            description = args[i+2]
            args_pairs.append([value, name, description])
    except:
        await ctx.reply(content=f'Sorry, something went wrong. Please check your command syntax, it should look like this: ```{PREFIX}additem 1 "Potion 1" "Heals 1 harm" | 1 "Handgun" "Deals 2 harm"```')
        return

    message = character.insert_item(args_pairs)

    if message is None:
        await ctx.reply(f"Items added successfully.")
    else:
        await ctx.reply(message)

@bot.command(usage = f"{PREFIX}removeitem <amount> <name> [| <amount> <name>]...", aliases=['ritem'])
async def removeitem(ctx: commands.Context, *args: str):
    """Removes items from your inventory. Can specify multiple
    items at once by separating the "amount, name"
    group with "|".
    
    Example:
    `!removeitem 1 "Potion 1"` - Removes 1 "Potion 1" from your 
        inventory.
    `!removeitem 2 "Potion 1" | 1 "Potion 2"` - Removes 2 
        "Potion 1" and 1 "Potion 2" from your inventory."""

    if not args or len(args) < 2:
        await ctx.reply("Please provide at least one pair of amount and item name to remove.")
        return

    character = Character(str(ctx.author.id), str(ctx.guild.id))

    if not character.check_if_exists():
        await ctx.reply("No character found on this server.")
        return

    args_pairs = []

    try:
        for i in range(0, len(args), 3):
            value = int(args[i])
            name = args[i+1].capitalize()
            existing_item = character.check_for_item(name)
            if not existing_item:
                await ctx.reply(f"There's no item named {name} in your inventory.")
                return
            new_value = existing_item[1] - value
            if new_value < 0:
                await ctx.reply(f"You can't remove {value}x {name} since you only have {existing_item[1]} on your inventory.")
                return
            args_pairs.append([new_value, name, existing_item[2]])
    except:
        await ctx.reply(content=f'Sorry, something went wrong. Please check your command syntax, it should look like this: ```{PREFIX}removeitem 1 "Potion 1" | 1 "Handgun"```')
        return

    character.remove_item(args_pairs)

    await ctx.reply(f"Items removed successfully.")

@bot.command(usage = f"{PREFIX}itemdescription <name> <description> [| <name> <description>]...", aliases=['item'])
async def itemdescription(ctx: commands.Context, *args: str):
    """Edits the description of items on your inventory. 
    Can specify multiple items at once by separating the 
    "name, description" pair with "|".
    
    Example:
    `!itemdescription "Potion 1" "Heals 2 harm"` - Changes
        the description of "Potion 1" to "Heals 2 harm".
    `!itemdescription "Potion 1" "Heals 2 harm" | "Potion 2" "Heals 3 harms"`
        - Changes the description of "Potion 1" to "Heals 2 harm" and
        of "Potion 2" to "Heals 3 harms"."""

    if not args or len(args) < 2:
        await ctx.reply("Please provide at least one pair of item name and description to edit.")
        return

    character = Character(str(ctx.author.id), str(ctx.guild.id))

    if not character.check_if_exists():
        await ctx.reply("No character found on this server.")
        return

    args_pairs = []

    try:
        for i in range(0, len(args), 3):
            name = args[i].capitalize()
            description = args[i+1]
            try:
                if args[i+2] != "|":
                    await ctx.reply(content=f'Sorry, something went wrong. Please check your command syntax, it should look like this: ```{PREFIX}itemdescription "Potion 1" "Heals 2 harm" | "Potion 2" "Heals 3 harms"```')
                    return
            except:
                pass
            existing_item = character.check_for_item(name)
            if not existing_item:
                await ctx.reply(f"There's no item named {name} in your inventory.")
                return
            args_pairs.append([description, existing_item[2]])
    except:
        await ctx.reply(content=f'Sorry, something went wrong. Please check your command syntax, it should look like this: ```{PREFIX}itemdescription "Potion 1" "Heals 2 harm" | "Potion 2" "Heals 3 harms"```')
        return

    message = character.edit_description(args_pairs)

    if message is None:
        await ctx.reply(f"Items edited successfully.")
    else:
        await ctx.reply(message)

@bot.command(usage = f"{PREFIX}inventory", aliases=['inv'])
async def inventory(ctx: commands.Context):
    """Lists your character's the inventory."""
    
    character = Character(str(ctx.author.id), str(ctx.guild.id))
    char_info = character.get_basic_profile()

    if not character.check_if_exists():
        await ctx.reply("No character found on this server.")
        return

    pages = []

    hx = character.get_inventory()
    barter = character.get_barter()
    pages = [InventoryPage(hx, barter)]

    page_manager = PageManager(f"Name: {char_info[1]}", pages, f"Playbook: {char_info[2]}", char_info[3])

    embed = dc.Embed.from_dict(page_manager.get_embed_dict())
    await ctx.reply(embed=embed)

@bot.command(usage =f"give <name> <amount> <item> [| <amount> <item>]...")
async def give(ctx: commands.Context, name: str,  *args: str):
    """Gives the named character specified amount of 
    some item. Can specify multiple items at once by 
    separating the "amount, item name" pair with "|".
    
    Example:
    `!give "Will Smith" 1 "Potion"` - Gives Will Smith
        1 Potion.
    `!give "Will Smith" 1 "Potion" | 2 "Potion 2"` - Gives
        Will Smith 1 Potion and 2 "Potion 2"."""
    
    if not args or len(args) < 2:
        await ctx.reply("Please provide at least one pair of amount and item name to edit.")
        return

    character = Character(str(ctx.author.id), str(ctx.guild.id))

    if not character.check_if_exists():
        await ctx.reply("No character found on this server.")
        return
    
    id_char = character.check_if_exists_name(name)
    if not id_char:
        await ctx.reply(f"No character named {name} found on this server.")
        return
    
    args_pairs = []
    items = ""

    try:
        for i in range(0, len(args), 3):
            value = int(args[i])
            name = args[i+1].capitalize()
            existing_item = character.check_for_item(name)
            if not existing_item:
                await ctx.reply(f"There's no item named {name} in your inventory.")
                return
            new_value = existing_item[1] - value
            if new_value < 0:
                await ctx.reply(f"You can't give {value}x {name} since you only have {existing_item[1]} on your inventory.")
                return
            args_pairs.append([name, value, new_value, existing_item[3], existing_item[2]])
            items += f"{value}x {name}\n"
    except:
        await ctx.reply(content=f'Sorry, something went wrong. Please check your command syntax, it should look like this: ```{PREFIX}!give "Will Smith" 1 "Potion" | 2 "Potion 2"```')
        return
    
    confirmation_bot = await ctx.reply(content=f"You're about to give {name}:\n{items}Type 'Confirm' to proceed.")

    try:
        confirm_message = await bot.wait_for('message', timeout=25.0, check= lambda m: check_confirm_message(m, ctx, "Confirm"))
    except asyncio.TimeoutError:
        await confirmation_bot.edit(content='Confirmation timed out. Action canceled.')
    else:
        message = character.give_item(id_char, args_pairs)

        if message is None:
            await ctx.reply("Transaction completed.")
        else:
            await ctx.reply(f"{message} Please check both inventories if any item is missing and try again.")

@bot.command(usage=f"{PREFIX}equip <name>")
async def equip(ctx: commands.Context, name: str):
    """Equips or unequips specified item."""

    character = Character(str(ctx.author.id), str(ctx.guild.id))

    if not character.check_if_exists():
        await ctx.reply("No character found on this server.")
        return
    
    name = name.capitalize()
    existing_item = character.check_for_item(name)
    if not existing_item:
        await ctx.reply(f"There's no item named {name} in your inventory.")
        return
    
    if existing_item[4] == 0:
        character.equip((existing_item[2], 1))
        await ctx.reply(f"{name} equipped successfully.")
    else:
        character.equip((existing_item[2], 0))
        await ctx.reply(f"{name} unequipped successfully.")

@equip.error
async def equip_error(ctx: commands.Context, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply(f"Please specify the item to equip. Example: `{PREFIX}equip \"Handgun\"`")

@bot.command(usage=f"{PREFIX}finaladvance", aliases=['delete'])
async def finaladvance(ctx: commands.Context):
    """Will **DELETE** your sheet but will save it's 
    name, playbook and stats for consulting. It's the 
    equivalent of getting the 'create a second character to play' 
    and 'retire your character (to safety)' improvements."""

    character = Character(str(ctx.author.id), str(ctx.guild.id))

    if not character.check_if_exists():
        await ctx.reply("No character found on this server.")
        return
    
    char_name = character.get_character_name()
    
    confirmation_bot = await ctx.reply(content=f"_**WARNING:**_ Advancing in this command will wipe your character. You will be able to check it's name, playbook and stat later, but will **NOT** be able to use it. Type '{char_name}' to proceed.")

    try:
        confirm_message = await bot.wait_for('message', timeout=25.0, check= lambda m: check_confirm_message(m, ctx, char_name))
    except asyncio.TimeoutError:
        await confirmation_bot.edit(content='Confirmation timed out. Action canceled.')
    else:
        confirmation_bot = await ctx.reply(content=f"Last chance. Type 'Confirm' to continue.")

        try:
            confirm_message = await bot.wait_for('message', timeout=25.0, check= lambda m: check_confirm_message(m, ctx, "Confirm"))
        except asyncio.TimeoutError:
            await confirmation_bot.edit(content='Confirmation timed out. Action canceled.')
        else:
            try:
                character.final_advance()
                character.delete_character()
                await ctx.send('Character retired successfully.')
            except:
                await ctx.send('Something went wrong.')

@bot.command(usage=f"{PREFIX}allcharacters", aliases=['char'])
async def allcharacters(ctx: commands.Context):
    """Lists all active characters."""

    character = Character(str(ctx.author.id), str(ctx.guild.id))

    characters = character.get_players()

    pages = []

    if len(characters) == 0:
        pages.append(AllCharacters('No characters found on this server'))
    else:
        for i in range(0, len(characters), 20):
            txt = "\n".join(str(char[0]) for char in characters[i:i+20])
            pages.append(AllCharacters(txt))

    page_manager = PageManager(f"All Characters", pages)

    embed = dc.Embed.from_dict(page_manager.get_embed_dict())
    msg = await ctx.reply(embed=embed)

    await add_arrows(msg)

    while True:
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=lambda r, u: check_reaction(r, u, ctx, emojis.ARROWS_LIST, msg))

            await turn_pages(msg, reaction, user, page_manager)
        except:
            break

@bot.command(usage=f"{PREFIX}retired")
async def retired(ctx: commands.Context):
    """Lists all retired characters."""

    character = Character(str(ctx.author.id), str(ctx.guild.id))

    characters = character.get_retired()

    pages = []

    if len(characters) == 0:
        pages.append(AllCharacters('No retired characters found on this server'))
    else:
        for i in range(0, len(characters), 20):
            txt = "\n".join(f"{char[2]} [{char[3]}] - Stats: {char[4]} / {char[5]} / {char[6]} / {char[7]} / {char[8]}" for char in characters[i:i+20])
            pages.append(AllCharacters(txt))

    page_manager = PageManager(f"All Characters", pages)

    embed = dc.Embed.from_dict(page_manager.get_embed_dict())
    msg = await ctx.reply(embed=embed)

    await add_arrows(msg)

    while True:
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=lambda r, u: check_reaction(r, u, ctx, emojis.ARROWS_LIST, msg))

            await turn_pages(msg, reaction, user, page_manager)
        except:
            break

@bot.command(usage=f"{PREFIX}newtype <playbook>")
async def newtype(ctx: commands.Context, new_pb: str):
    """Change your character to a new type. It's the equivalent 
    of getting the 'change your character to a new type' improvement. 
    Valid options are:
    `Angel` `Battlebabe` `Brainer` `Chopper` `Driver` `Gunlugger` 
    `Hardholder` `Hocus` `Operator` `Savyhead` `Skinner` `Child-thing` 
    `Faceless` `News` `Quarantine` `Show` `Waterbearer` `Landfall Marine`"""

    character = Character(str(ctx.author.id), str(ctx.guild.id))

    if not character.check_if_exists():
        await ctx.reply("No character found on this server.")
        return
    
    if character.is_new_type():
        await ctx.reply("You can't change types twice.")
        return

    playbooks = ["Angel","Battlebabe","Brainer","Chopper","Driver","Gunlugger",
    "Hardholder","Hocus","Operator","Savyhead","Skinner","Child-thing",
    "Faceless","News","Quarantine","Show","Waterbearer","Landfall Marine"]

    if new_pb not in playbooks:
        await ctx.reply(f"No playbook named {new_pb} found. Check `{PREFIX}help newtype` to see the valid options.")
        return
    
    char_name = character.get_character_name()
    
    confirmation_bot = await ctx.reply(content=f"_**WARNING:**_ This will change your playbook to {new_pb}, and while you keep your old improvements, you'll **NOT** be able to improve the ones you left behind. Type '{char_name}' to proceed.")

    try:
        confirm_message = await bot.wait_for('message', timeout=25.0, check= lambda m: check_confirm_message(m, ctx, char_name))
    except asyncio.TimeoutError:
        await confirmation_bot.edit(content='Confirmation timed out. Action canceled.')
    else:
        character.new_type(playbooks.index(new_pb) + 1)
        await ctx.reply(f"You are now a {new_pb}.")

@newtype.error
async def newtype_error(ctx: commands.Context, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply(f"Please specify the playbook to change. Example: `{PREFIX}newtype \"Angel\"`")

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
            if cmd_obj.aliases:
                em.add_field(name="**Aliases**", value=" ".join(f"`{alias}`" for alias in cmd_obj.aliases))
            em.set_footer(text="<> means it's required, [] means it's optional")
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

def check_reaction(reaction: dc.Reaction, user: dc.User | dc.Member, ctx: commands.Context, emojis_list: list[str], message: dc.Message) -> bool:
    """Checks if it was the message author that reacted to 
    the message, and if the reaction is on the valid reactions list."""
    return user == ctx.author and str(reaction.emoji) in emojis_list and reaction.message.id == message.id

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
            pages.append(MovesPage(batch_moves, special))
        else:
            pages.append(MovesPage(batch_moves))
    return pages

def is_imgur_url(url):
    pattern = r'^https?://i\.imgur\.com/(\w+)(\.\w+)?$'
    match = re.match(pattern, url)
    return match is not None

bot.run( TOKEN )