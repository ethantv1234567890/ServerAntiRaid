"""Lockdown Cog, commands executed by the moderator to combat a raid."""

import asyncio
import json

import discord
from discord.ext import commands


class Lockdown(commands.Cog):
    """Moderator commands to combat a raid."""
    def __init__(self, bot):
        self.bot = bot
        self.blue = discord.Color.blue()

    async def lock_channel(self, channel):
        """Function used to lock a channel."""
        # Saves previous channel overwrites
        guild_key = str(channel.guild.id)
        channel_key = str(channel.id)

        with open('./data/channels.json', 'r') as channels_file:
            ow_dict = json.load(channels_file)

        if guild_key not in ow_dict:
            ow_dict[guild_key] = {}
        ow_dict[guild_key][channel_key] = {}

        channel_ow = channel.overwrites

        if not channel_ow:  # empty dict
            target = channel.guild.default_role
            overwrite = channel.overwrites_for(target)
            channel_ow[target] = overwrite

        for target, overwrite in channel_ow.items():
            target_key = str(target.id)
            ow_dict[guild_key][channel_key][target_key] = dict(iter(overwrite))

        with open('./data/channels.json', 'w') as channels_file:
            json.dump(ow_dict, channels_file, indent=2)

        # Locks channel
        new_ow = {}

        for target, overwrite in channel_ow.items():
            overwrite.send_messages = False
            new_ow[target] = overwrite

        await channel.edit(overwrites=new_ow)

    async def unlock_channel(self, channel):
        """Function used to unlock a channel."""
        # Access previous channel overwrites
        guild = channel.guild
        guild_key = str(guild.id)
        channel_key = str(channel.id)

        with open('./data/channels.json', 'r') as channels_file:
            ow_dict = json.load(channels_file)

        new_ow = {}

        for target_id, overwrite in ow_dict[guild_key][channel_key].items():
            target_id = int(target_id)

            target = guild.get_role(target_id) or guild.get_member(target_id)

            new_ow[target] = discord.PermissionOverwrite(**overwrite)

        # Clears data from channels.json
        ow_dict[guild_key].pop(channel_key)

        if not ow_dict[guild_key]:  # guild_key dict is empty
            ow_dict.pop(guild_key)

        with open('./data/channels.json', 'w') as channels_file:
            json.dump(ow_dict, channels_file, indent=2)

        # Unlocks channel
        await channel.edit(overwrites=new_ow)

    @commands.command()
    async def lock(self, ctx, channel: discord.TextChannel = None):
        """
        Prevents users from talking in a text channel.

        **Example:** `.lock #general`
        """
        channel = channel or ctx.channel
        guild_key = str(ctx.guild.id)
        channel_key = str(channel.id)

        with open('./data/channels.json', 'r') as channels_file:
            ow_dict = json.load(channels_file)

        if guild_key not in ow_dict:
            ow_dict[guild_key] = {}
        if channel_key in ow_dict[guild_key]:
            await ctx.send('This channel is already locked!')
        else:
            await self.lock_channel(channel)
            await ctx.send(f'{channel.mention} has been locked!')

    @commands.command()
    async def unlock(self, ctx, channel: discord.TextChannel = None):
        """
        Lifts the lock for a text channel.

        **Example:** `.unlock #general`
        """
        channel = channel or ctx.channel
        guild_key = str(ctx.guild.id)
        channel_key = str(channel.id)

        with open('./data/channels.json', 'r') as channels_file:
            ow_dict = json.load(channels_file)

        if channel_key not in ow_dict[guild_key]:
            await ctx.send('This channel is not locked!')
        else:
            await self.unlock_channel(channel)
            await ctx.send(f'{channel.mention} has been unlocked!')

    @commands.command()
    async def lockall(self, ctx):
        """Prevents users from talking in all text channels."""
        guild_key = str(ctx.guild.id)

        with open('./data/channels.json', 'r') as channels_file:
            ow_dict = json.load(channels_file)

        if guild_key not in ow_dict:
            ow_dict[guild_key] = {}

        for channel in ctx.guild.text_channels:
            if channel == ctx.guild.public_updates_channel:
                continue
            if channel.is_news():
                continue
            if channel == ctx.guild.system_channel:
                continue
            if channel == ctx.guild.rules_channel:
                continue

            channel_key = str(channel.id)

            if channel_key not in ow_dict[guild_key]:
                await self.lock_channel(channel)
                await ctx.send(f'{channel.mention} has been locked!')
                await asyncio.sleep(1)

    @commands.command()
    async def unlockall(self, ctx):
        """Lifts the lock for all text channels."""
        guild_key = str(ctx.guild.id)

        with open('./data/channels.json', 'r') as channels_file:
            ow_dict = json.load(channels_file)

        for channel in ctx.guild.text_channels:
            channel_key = str(channel.id)

            if channel_key not in ow_dict[guild_key]:
                continue
            await self.unlock_channel(channel)
            await ctx.send(f'{channel.mention} has been unlocked!')
            await asyncio.sleep(1)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def purge(self, ctx, messages: int):
        """
        Delete messages from the current channel.

        **Example:** `.purge 100`
        """
        if messages >= 1:
            await ctx.message.delete()
            await ctx.channel.purge(limit=messages)

            if messages == 1:
                await ctx.send('Successfully purged 1 message!')
            else:
                await ctx.send(f'Successfully purged {messages} messages!')
        else:
            await ctx.send('Invalid number of messages to purge!')

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def slowmode(self, ctx, seconds: int):
        """
        Implements slowmode in the current channel.

        **Example:** `.slowmode 5`
        """
        await ctx.message.delete()
        if 0 <= seconds <= 21600:
            await ctx.channel.edit(slowmode_delay=seconds)

            if seconds == 1:
                await ctx.send('Slowmode set to 1 second!')
            else:
                await ctx.send(f'Slowmode set to {seconds} seconds!')
        else:
            await ctx.send('Seconds must be between `0` and `21600`!')


def setup(bot):
    """Adds the Lockdown cog to the bot."""
    bot.add_cog(Lockdown(bot))
