import discord as dc
from discord.ext import commands
from models.field import Field
from models.page import Page
from config import TOKEN  # Import the bot token from the config module

intents = dc.Intents.all()
bot = commands.Bot( command_prefix='^', intents=intents )

@bot.command()
async def checksheet(ctx):

    embed=dc.Embed(title="Name: Dou", description="Playbook: The Angel", color=0xff3838)
    embed.set_author(name="@Haku")
    embed.set_thumbnail(url="https://i.imgur.com/fAi8DsQ.png")
    embed.add_field(name="STATS", value="stats here\nfstsd", inline=True)

    msg = await ctx.send( embed=embed )
    await msg.add_reaction('\U0001F44D')
    await msg.add_reaction('\U0001F44E') 

    def check(reaction, user):
        return reaction.message.id == msg.id and str(reaction.emoji) in ['\U0001F44D', '\U0001F44E']

    reaction, user = await bot.wait_for('reaction_add', check=check)
    if str(reaction.emoji) == '\U0001F44D':
        await ctx.send(f'Thanks for the thumbs up, {user.mention}!')
    elif str(reaction.emoji) == '\U0001F44E':
        await ctx.send(f'Sorry you didn\'t like it, {user.mention}!')

@bot.command()
async def embed(ctx):
    pages = [
        Page('This is the first page.', [
            Field('Field 1', 'This is field 1.'),
            Field('Field 2', 'This is field 2.')
        ]),
        Page('This is the second page.', [
            Field('Field 3', 'This is field 3.'),
            Field('Field 4', 'This is field 4.')
        ]),
        Page('This is the third page.', [
            Field('Field 5', 'This is field 5.'),
            Field('Field 6', 'This is field 6.')
        ])
    ]
    page_number = 0

    embed = dc.Embed.from_dict(pages[page_number].to_dict())
    embed.set_footer(text=f'Page {page_number + 1} of {len(pages)}')
    msg = await ctx.send(embed=embed)

    await msg.add_reaction('\u25c0') # left arrow
    await msg.add_reaction('\u25b6') # right arrow

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ['\u25c0', '\u25b6']

    while True:
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)

            if str(reaction.emoji) == '\u25c0':
                page_number = (page_number - 1) % len(pages)
            elif str(reaction.emoji) == '\u25b6':
                page_number = (page_number + 1) % len(pages)

            embed_dict = pages[page_number].to_dict()
            embed = dc.Embed.from_dict(embed_dict)
            embed.set_footer(text=f'Page {page_number + 1} of {len(pages)}')
            await msg.edit(embed=embed)
            await msg.remove_reaction(reaction, user)
        except:
            break

bot.run( TOKEN )