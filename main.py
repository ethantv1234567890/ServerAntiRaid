"""Server Anti-Raid, developed by ACPlayGames!"""

import json

import discord
from discord.ext import commands


async def get_prefix(bot_, message):
    """Returns the appropriate prefix for the bot."""
    with open('./data/options.json', 'r') as options_file:
        options_dict = json.load(options_file)

    if message.guild and str(message.guild.id) in options_dict:
        prefixes = options_dict[str(message.guild.id)]['prefix']
    else:
        prefixes = '.'

    return commands.when_mentioned_or(*prefixes)(bot_, message)

bot = commands.Bot(command_prefix=get_prefix, case_insensitive=True)


@bot.event
async def on_ready():
    """Tells the bot what to do when it is ready."""
    await bot.change_presence(
        status=discord.Status.dnd,
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name='your every move...'
        )
    )
    print(
        '\nBot Ready!\n',
        f'\nClient User: {bot.user.name}#{bot.user.discriminator}',
        f'\nUser ID: {bot.user.id}',
        f'\nDiscord Library Version: {discord.__version__} ' +
        f'{discord.version_info.releaselevel}\n'
    )


@bot.event
async def on_command_error(ctx, error):
    """Handles any errors raised by the commands extension."""
    if isinstance(error, commands.CommandNotFound):
        pass
    elif isinstance(error, commands.NoPrivateMessage):
        await ctx.send('Commands will not work in DMs! Please use a guild!')
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send('Sorry, I do not have administrator permission!')
    elif isinstance(error, commands.CheckFailure):
        await ctx.send('You are not allowed to use this bot! Shoo!')
    elif isinstance(error, commands.CommandOnCooldown):
        seconds = round(error.retry_after, 1)
        await ctx.send(f'Woah, slow down! Please wait `{seconds}` seconds!')
    elif isinstance(error, commands.CommandInvokeError):
        await ctx.send('Uh oh! Something went wrong!')
    else:
        await ctx.send(error)


@bot.check
async def global_check(ctx):
    """Bot checks for permissions and the location of the message."""
    # check for bot permissions
    bot_perms = commands.bot_has_guild_permissions(administrator=True)

    # check if command is the Captcha command
    captcha_command = ctx.command.name == 'captcha'

    if not captcha_command:
        # check if command is not in DMs
        guild_only = await commands.guild_only().predicate(ctx)

        # check for user permissions in guild
        author = ctx.author
        with open('./data/options.json', 'r') as options_file:
            options = json.load(options_file)

        if guild_only:
            guild_key = str(ctx.guild.id)
            if guild_key not in options:
                mod_role = None
            else:
                mod_role = options[guild_key]['mod_role']
                mod_role = ctx.guild.get_role(mod_role)

            mod_only = mod_role in author.roles or author == ctx.guild.owner
        else:
            mod_only = False

        return bot_perms and guild_only and mod_only
    return bot_perms

bot.load_extension('cogs.captcha_')
bot.load_extension('cogs.lockdown')
bot.load_extension('cogs.moderation')
bot.load_extension('cogs.options')

bot.run('TOKEN HERE')
