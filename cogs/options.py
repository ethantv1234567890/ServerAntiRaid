"""Options Cog, allows for customizable options for each guild."""

import json

import discord
from discord.ext import commands


class Options(commands.Cog):
    """Customizable options for the bot."""
    def __init__(self, bot):
        self.bot = bot
        self.blue = discord.Color.blue()
        self.accepted_values = {
            'prefix': 'Anything',
            'captcha': '`True` or `False`',
            'public_log': 'Any text channel',
            'private_log': 'Any text channel',
            'mod_role': 'Any role',
            'muted_role': 'Any role',
            'member_role': 'Any role'
        }  # text used for an embed
        self.tc_conv = commands.TextChannelConverter()
        self.role_conv = commands.RoleConverter()

    async def get_prefix(self, message):
        """Returns the appropriate prefix for the bot."""
        with open('./data/options.json', 'r') as options_file:
            options_dict = json.load(options_file)

        if message.guild and str(message.guild.id) in options_dict:
            return options_dict[str(message.guild.id)]['prefix']
        return '.'

    async def add_guild(self, guild):
        """If the guild options does not exist, add it to the dictionary."""
        with open('./data/options.json', 'r') as options_file:
            options = json.load(options_file)

        guild_key = str(guild.id)

        if guild_key not in options:
            options[guild_key] = {
                'prefix': '.',
                'captcha': True,
                'public_log': None,
                'private_log': None,
                'mod_role': None,
                'muted_role': None,
                'member_role': None
            }  # append default values

        with open('./data/options.json', 'w') as options_file:
            json.dump(options, options_file, indent=2)

    async def change_option(self, ctx, option, *, new_option):
        """Change an option with the 'settings' command."""
        guild_key = str(ctx.guild.id)

        with open('./data/options.json', 'r') as options_file:
            options = json.load(options_file)

        # String
        if option == 'prefix':
            options[guild_key]['prefix'] = new_option

        # Boolean
        elif option == 'captcha':
            if new_option.lower() in ('true', 'yes', 'on'):
                options[guild_key][option] = True
            elif new_option.lower() in ('false', 'no', 'off'):
                options[guild_key][option] = False
            else:
                raise commands.errors.BadArgument(
                    message='Invalid response! Use `True` or `False`!'
                )

        # discord.TextChannel
        elif option in ('public_log', 'private_log'):
            text_channel = await self.tc_conv.convert(ctx, new_option)
            options[guild_key][option] = text_channel.id

        # discord.Role
        elif option in ('mod_role', 'muted_role', 'member_role'):
            role = await self.role_conv.convert(ctx, new_option)
            options[guild_key][option] = role.id

        with open('./data/options.json', 'w') as options_file:
            json.dump(options, options_file, indent=2)

        await ctx.send(
            f'**{option}** is now **{new_option}**',
            allowed_mentions=discord.AllowedMentions(roles=False)
        )

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """Determines what to do when joining a guild."""
        await self.add_guild(guild)

        # Creating the embed
        welcome_embed = discord.Embed(
            title='Thank you for inviting this bot!',
            description='Do `.settings` to get started!',
            color=self.blue
        )
        if guild.mfa_level == 0:
            welcome_embed.add_field(
                name='2FA',
                value='2FA is disabled in this guild. Consider enabling it!',
                inline=False
            )
        if guild.verification_level == discord.VerificationLevel.none:
            welcome_embed.add_field(
                name='Verification Level',
                value='There is no verification. Consider selecting one!',
                inline=False
            )
        if guild.explicit_content_filter != discord.ContentFilter.all_members:
            welcome_embed.add_field(
                name='Explicit Content Filter',
                value='ECF is not enabled for everyone. Please enable it!',
                inline=False
            )

        # Checking the channels and sending it
        if guild.public_updates_channel is not None:
            await guild.public_updates_channel.send(embed=welcome_embed)
        else:
            for text_channel in guild.text_channels:
                if text_channel.is_news():
                    continue
                if text_channel == guild.system_channel:
                    continue
                if text_channel == guild.rules_channel:
                    continue
                try:
                    await text_channel.send(embed=welcome_embed)
                    break
                except discord.Forbidden:
                    continue

    @commands.command(aliases=['options'])
    @commands.cooldown(1, 1, commands.BucketType.guild)
    async def settings(self, ctx, option=None, new_option=None):
        """Configure customizable settings."""
        if option is None:  # sends info about all the options
            prefix = await self.get_prefix(ctx.message)
            settings_embed = discord.Embed(
                title='Customizable Settings',
                description=f'Run `{prefix}settings <option> <new_option>`!',
                color=self.blue
            )
            settings_embed.add_field(
                name='prefix',
                value='Sets the prefix of the bot for the guild.',
                inline=False
            )
            settings_embed.add_field(
                name='captcha',
                value='Toggles the captcha feature upon member join.',
                inline=False
            )
            settings_embed.add_field(
                name='public_log',
                value='Selects public channel (warns, mutes, kicks, bans).',
                inline=False
            )
            settings_embed.add_field(
                name='private_log',
                value='Selects private channel (important information).',
                inline=False
            )
            settings_embed.add_field(
                name='mod_role',
                value='Selects the moderator role for the bot.',
                inline=False
            )
            settings_embed.add_field(
                name='muted_role',
                value='Selects mute role to be given to muted users.',
                inline=False
            )
            settings_embed.add_field(
                name='member_role',
                value='Selects the Membership role for verified users.',
                inline=False
            )
            await ctx.send(embed=settings_embed)
        elif option.lower() in (
            'prefix', 'captcha', 'public_log', 'private_log',
            'mod_role', 'muted_role', 'member_role'
        ):
            option = option.lower()
            guild_key = str(ctx.guild.id)
            await self.add_guild(ctx.guild)

            with open('./data/options.json', 'r') as options_file:
                options = json.load(options_file)

            if new_option is None:  # sends info about selected option
                current_value = options[guild_key][option]
                if current_value is not None:
                    if option in ('public_log', 'private_log'):
                        current_value = ctx.guild.get_channel(current_value)
                        current_value = current_value.mention
                    elif option in ('mod_role', 'muted_role', 'member_role'):
                        current_value = ctx.guild.get_role(current_value)
                        current_value = current_value.mention

                option_embed = discord.Embed(
                    title=option,
                    description='Run `.settings <option> <new_option>`!',
                    color=self.blue
                )
                option_embed.add_field(
                    name='Current Value',
                    value=current_value,
                    inline=False
                )
                option_embed.add_field(
                    name='Accepted Types of Value',
                    value=self.accepted_values[option],
                    inline=False
                )
                await ctx.send(embed=option_embed)
            else:  # change an option
                await self.change_option(ctx, option, new_option=new_option)
        else:
            await ctx.send('That is not an option!')


def setup(bot):
    """Adds the Options cog to the bot."""
    bot.add_cog(Options(bot))
