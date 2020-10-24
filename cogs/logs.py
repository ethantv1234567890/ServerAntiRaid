"""Logs Cog, detects deleted and edited messages."""

import json

import discord
from discord.ext import commands


class Logs(commands.Cog):
    """Detects deleted and edited messages."""
    def __init__(self, bot):
        self.bot = bot
        self.blue = discord.Color.blue()

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """Calls when a message is deleted in the cache."""
        # checks for the private_log channel
        with open('./data/options.json', 'r') as options_file:
            options = json.load(options_file)

        if not message.guild:
            return

        guild_key = str(message.guild.id)

        if guild_key not in options:
            return

        channel = options[guild_key]['private_log']

        if not channel:
            return

        channel = message.guild.get_channel(channel)

        # creating & sending the embed message
        delete_embed = discord.Embed(
            title='Message Deleted',
            color=self.blue
        )
        delete_embed.set_author(
            name=message.author,
            icon_url=message.author.avatar_url
        )
        delete_embed.add_field(
            name='Message',
            value=message.content,
            inline=False
        )
        delete_embed.add_field(
            name='Channel',
            value=message.channel.mention,
            inline=False
        )

        await channel.send(embed=delete_embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """Calls when a message is edited in the cache."""
        # checks for the private_log channel
        with open('./data/options.json', 'r') as options_file:
            options = json.load(options_file)

        if not after.guild:
            return

        if not(before.content and after.content):  # message empty
            return

        guild_key = str(after.guild.id)

        if guild_key not in options:
            return

        channel = options[guild_key]['private_log']

        if not channel:
            return

        channel = after.guild.get_channel(channel)

        # creating & sending the embed message
        edit_embed = discord.Embed(
            title='Message Edited',
            color=self.blue
        )
        edit_embed.set_author(
            name=after.author,
            icon_url=after.author.avatar_url
        )
        edit_embed.add_field(
            name='Message Before',
            value=before.content,
            inline=False
        )
        edit_embed.add_field(
            name='Message After',
            value=after.content,
            inline=False
        )
        edit_embed.add_field(
            name='Channel',
            value=after.channel.mention,
            inline=False
        )

        await channel.send(embed=edit_embed)


def setup(bot):
    """Adds the Logs cog to the bot."""
    bot.add_cog(Logs(bot))
