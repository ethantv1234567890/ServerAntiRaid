"""Moderation Cog, typical moderation commands."""

import json

import discord
from discord.ext import commands


class Moderation(commands.Cog):
    """Typical moderation commands."""
    def __init__(self, bot):
        self.bot = bot
        self.blue = discord.Color.blue()
        self.user_conv = commands.UserConverter()

    async def create_muted_role(self, guild):
        """Create a role that denies permission to send messages."""
        muted_role = await guild.create_role(
            name='Muted',
            color=discord.Color.light_gray(),
            hoist=True,
            mentionable=True,
            reason='No muted role detected, so I automatically created one!'
        )
        return muted_role

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.member)
    async def warn(self, ctx, member: discord.Member, *, reason='No reason.'):
        """
        Issues a warn to a user.

        **Example:** `.warn @ACPlayGames being bad`
        """
        await ctx.message.delete()

        # add warn to user
        with open('./data/warns.json', 'r') as warns_file:
            warns = json.load(warns_file)

        guild_key = str(ctx.guild.id)
        member_key = str(member.id)

        if guild_key not in warns:
            warns[guild_key] = {}
        if member_key not in warns[guild_key]:
            warns[guild_key][member_key] = []
        warns[guild_key][member_key].append(reason)

        with open('./data/warns.json', 'w') as warns_file:
            json.dump(warns, warns_file, indent=2)

        await ctx.send(f'**{member}** has been warned!')

        # check for the public_log channel
        with open('./data/options.json', 'r') as options_file:
            options = json.load(options_file)

        if guild_key not in options:
            return

        channel = options[guild_key]['public_log']

        if not channel:
            return

        channel = ctx.guild.get_channel(channel)

        # creating & sending the embed message
        warn_embed = discord.Embed(
            title='Warning',
            description='Warns a user for their misconducts!',
            color=self.blue
        )
        warn_embed.set_author(
            name=member,
            icon_url=member.avatar_url
        )
        warn_embed.add_field(
            name='User',
            value=member,
            inline=False
        )
        warn_embed.add_field(
            name='Moderator',
            value=ctx.author,
            inline=False
        )
        warn_embed.add_field(
            name='Reason',
            value=reason,
            inline=False
        )

        await channel.send(embed=warn_embed)

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.member)
    async def warnings(self, ctx, member: discord.Member):
        """
        Lists the warnings that the user has.

        **Example:** `.warnings @ACPlayGames`
        """
        # gets the warns of the user & parses them
        with open('./data/warns.json', 'r') as warns_file:
            warns = json.load(warns_file)

        guild_key = str(ctx.guild.id)
        member_key = str(member.id)

        warns_length = 0
        warns_plural = 'warnings'

        if guild_key in warns and member_key in warns[guild_key]:
            warns_length = len(warns[guild_key][member_key])
            if warns_length == 1:
                warns_plural = 'warning'

        warns_msg = f'**{member}** has {warns_length} {warns_plural}!'

        # creating & sending Embed
        warnings_embed = discord.Embed(
            title='Warnings',
            description=warns_msg,
            color=self.blue
        )
        warnings_embed.set_author(
            name=member,
            icon_url=member.avatar_url
        )
        for i in range(warns_length):
            warnings_embed.add_field(
                name=f'Warning #{i + 1}',
                value=warns[guild_key][member_key][i],
                inline=False
            )

        await ctx.send(embed=warnings_embed)

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.member)
    async def clearwarn(self, ctx, member: discord.Member, warn_id: int):
        """
        Clears a warn from a user.

        **Example:** `.clearwarn @ACPlayGames 1`
        """
        await ctx.message.delete()

        with open('./data/warns.json', 'r') as warns_file:
            warns = json.load(warns_file)

        guild_key = str(ctx.guild.id)
        member_key = str(member.id)

        if guild_key in warns and member_key in warns[guild_key]:
            member_warns = warns[guild_key][member_key]

            if len(member_warns) >= warn_id > 0:
                member_warns.pop(warn_id - 1)
                await ctx.send(f'Warn #{warn_id} has been cleared!')

                with open('./data/warns.json', 'w') as warns_file:
                    json.dump(warns, warns_file, indent=2)
            else:
                await ctx.send('Invalid ID!')
        else:
            await ctx.send('This user has no warns!')

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.member)
    async def mute(self, ctx, member: discord.Member, *, reason='No reason.'):
        """
        Mutes a user.

        **Example:** `.mute @ACPlayGames bad`
        """
        await ctx.message.delete()

        # check for a Muted role, creates one if not found
        with open('./data/options.json', 'r') as options_file:
            options = json.load(options_file)

        guild_key = str(ctx.guild.id)
        member_key = str(member.id)

        if guild_key in options:
            muted_role = options[guild_key]['muted_role']
            muted_role = ctx.guild.get_role(muted_role)
            muted_role = muted_role or await self.create_muted_role(ctx.guild)
        else:
            muted_role = await self.create_muted_role(ctx.guild)
            options[guild_key] = {
                'prefix': '.',
                'public_log': None,
                'private_log': None,
                'mod_role': None,
                'muted_role': None
            }  # append default values

        options[guild_key]['muted_role'] = muted_role.id

        with open('./data/options.json', 'w') as options_file:
            json.dump(options, options_file, indent=2)

        # remembers & removes current roles, gives Muted role
        with open('./data/mutes.json', 'r') as mutes_file:
            mutes = json.load(mutes_file)

        roles = member.roles
        roles.remove(ctx.guild.default_role)

        if guild_key not in mutes:
            mutes[guild_key] = {}

        if member_key in mutes[guild_key]:
            await ctx.send('This person is already muted!')
            return

        await member.edit(roles=[muted_role], reason='Muted')

        await ctx.send(f'**{member}** has been muted!')

        mutes[guild_key][member_key] = [role.id for role in roles]

        with open('./data/mutes.json', 'w') as mutes_file:
            json.dump(mutes, mutes_file, indent=2)

        # check for the public_log channel
        with open('./data/options.json', 'r') as options_file:
            options = json.load(options_file)

        if guild_key not in options:
            return

        channel = options[guild_key]['public_log']

        if not channel:
            return

        channel = ctx.guild.get_channel(channel)

        # creating & sending the embed message
        mute_embed = discord.Embed(
            title='Mute',
            description='Mutes a user for their misconducts!',
            color=self.blue
        )
        mute_embed.set_author(
            name=member,
            icon_url=member.avatar_url
        )
        mute_embed.add_field(
            name='User',
            value=member,
            inline=False
        )
        mute_embed.add_field(
            name='Moderator',
            value=ctx.author,
            inline=False
        )
        mute_embed.add_field(
            name='Reason',
            value=reason,
            inline=False
        )

        await channel.send(embed=mute_embed)

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.member)
    async def unmute(self, ctx, member: discord.Member, *,
                     reason='No reason.'):
        """
        Unmutes a user.

        **Example:** `.unmute @ACPlayGames good`
        """
        await ctx.message.delete()

        guild_key = str(ctx.guild.id)
        member_key = str(member.id)

        # removes Muted role, returns original roles
        with open('./data/mutes.json', 'r') as mutes_file:
            mutes = json.load(mutes_file)

        if guild_key not in mutes:
            await ctx.send('No one has been muted before!')
            return
        if member_key not in mutes[guild_key]:
            await ctx.send('This person is not muted!')
            return

        role_ids = mutes[guild_key][member_key]
        roles = [ctx.guild.get_role(role_id) for role_id in role_ids]

        mutes[guild_key].pop(member_key)

        with open('./data/mutes.json', 'w') as mutes_file:
            json.dump(mutes, mutes_file, indent=2)

        await member.edit(roles=roles, reason='Unmuted')

        await ctx.send(f'**{member}** has been unmuted!')

        # check for the public_log channel
        with open('./data/options.json', 'r') as options_file:
            options = json.load(options_file)

        if guild_key not in options:
            return

        channel = options[guild_key]['public_log']

        if not channel:
            return

        channel = ctx.guild.get_channel(channel)

        # creating & sending the embed message
        unmute_embed = discord.Embed(
            title='Unmute',
            description='Unmutes a user for serving their sentence!',
            color=self.blue
        )
        unmute_embed.set_author(
            name=member,
            icon_url=member.avatar_url
        )
        unmute_embed.add_field(
            name='User',
            value=member,
            inline=False
        )
        unmute_embed.add_field(
            name='Moderator',
            value=ctx.author,
            inline=False
        )
        unmute_embed.add_field(
            name='Reason',
            value=reason,
            inline=False
        )

        await channel.send(embed=unmute_embed)

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.member)
    async def kick(self, ctx, member: discord.Member, *, reason='No reason.'):
        """
        Removes a user from the current guild.

        **Example:** `.kick @ACPlayGames annoying`
        """
        await ctx.message.delete()
        await member.kick(reason=reason)

        await ctx.send(f'**{member}** has been kicked!')

        guild_key = str(ctx.guild.id)

        # check for the public_log channel
        with open('./data/options.json', 'r') as options_file:
            options = json.load(options_file)

        if guild_key not in options:
            return

        channel = options[guild_key]['public_log']

        if not channel:
            return

        channel = ctx.guild.get_channel(channel)

        # creating & sending the embed message
        kick_embed = discord.Embed(
            title='Kick',
            description='Goodbye!',
            color=self.blue
        )
        kick_embed.set_author(
            name=member,
            icon_url=member.avatar_url
        )
        kick_embed.add_field(
            name='User',
            value=member,
            inline=False
        )
        kick_embed.add_field(
            name='Moderator',
            value=ctx.author,
            inline=False
        )
        kick_embed.add_field(
            name='Reason',
            value=reason,
            inline=False
        )

        await channel.send(embed=kick_embed)

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.member)
    async def ban(self, ctx, user, *, reason='No reason.'):
        """
        Strikes a user with a ban hammer.

        **Example:** `.ban @ACPlayGames raiding`
        """
        await ctx.message.delete()

        try:
            member = await self.user_conv.convert(ctx, user)
        except commands.UserNotFound:
            await ctx.send('Please provide a valid user!')
            return

        await ctx.guild.ban(member, reason=reason)
        await ctx.send(f'**{member}** has been banned!')

        guild_key = str(ctx.guild.id)

        # check for the public_log channel
        with open('./data/options.json', 'r') as options_file:
            options = json.load(options_file)

        if guild_key not in options:
            return

        channel = options[guild_key]['public_log']

        if not channel:
            return

        channel = ctx.guild.get_channel(channel)

        # creating & sending the embed message
        ban_embed = discord.Embed(
            title='Ban',
            description='Goodbye forever, loser!',
            color=self.blue
        )
        ban_embed.set_author(
            name=member,
            icon_url=member.avatar_url
        )
        ban_embed.add_field(
            name='User',
            value=member,
            inline=False
        )
        ban_embed.add_field(
            name='Moderator',
            value=ctx.author,
            inline=False
        )
        ban_embed.add_field(
            name='Reason',
            value=reason,
            inline=False
        )

        await channel.send(embed=ban_embed)

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.member)
    async def bans(self, ctx):
        """Retrieves all bans in the guild."""
        bans = await ctx.guild.bans()

        bans_plural = 'bans'
        if len(bans) == 1:
            bans_plural = 'ban'

        bans_msg = f'There are {len(bans)} {bans_plural} in this guild!'

        bans_embed = discord.Embed(
            title='Bans',
            description=bans_msg,
            color=self.blue
        )
        for ban in bans:
            bans_embed.add_field(
                name=ban.user,
                value=ban.reason,
                inline=False
            )

        await ctx.send(embed=bans_embed)

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.member)
    async def unban(self, ctx, user, *, reason='No reason.'):
        """
        Reverses the effects of the ban hammer.

        **Example:** `.unban @ACPlayGames forgiven`
        """
        await ctx.message.delete()

        try:
            member = await self.user_conv.convert(ctx, user)
        except commands.UserNotFound:
            await ctx.send('Please provide a valid user!')
            return

        await ctx.guild.unban(member, reason=reason)
        await ctx.send(f'**{member}** has been unbanned!')

        guild_key = str(ctx.guild.id)

        # check for the public_log channel
        with open('./data/options.json', 'r') as options_file:
            options = json.load(options_file)

        if guild_key not in options:
            return

        channel = options[guild_key]['public_log']

        if not channel:
            return

        channel = ctx.guild.get_channel(channel)

        # creating & sending the embed message
        unban_embed = discord.Embed(
            title='Unban',
            description='Welcome back! Perhaps I treated you too harshly.',
            color=self.blue
        )
        unban_embed.set_author(
            name=member,
            icon_url=member.avatar_url
        )
        unban_embed.add_field(
            name='User',
            value=member,
            inline=False
        )
        unban_embed.add_field(
            name='Moderator',
            value=ctx.author,
            inline=False
        )
        unban_embed.add_field(
            name='Reason',
            value=reason,
            inline=False
        )

        await channel.send(embed=unban_embed)


def setup(bot):
    """Adds the Moderation cog to the bot."""
    bot.add_cog(Moderation(bot))
