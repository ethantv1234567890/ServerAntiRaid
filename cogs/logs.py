"""Logs Cog, detects deleted and edited messages."""

from datetime import datetime
import json

import discord
from discord.ext import commands


class Logs(commands.Cog):
    """Detects deleted and edited messages."""
    def __init__(self, bot):
        self.bot = bot
        self.blue = discord.Color.blue()

    async def is_alt(self, user: discord.User):
        """
        Function that checks if a user is an alt.

        Uses a points system from 0 to 5.
        A score of 0-1 means the user is very unlikely to be an alt.
        A score of 2-3 means the user may or may not be an alt.
        A score of 4-5 means the user is very likely to be an alt.
        """
        score = 0

        age = datetime.utcnow() - user.created_at

        if age.days <= 7:  # created within a week ago
            score += 3
        if user.avatar is None:  # default avatar
            score += 1
        if not user.public_flags.all():
            score += 1

        return score

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.member)
    async def check(self, ctx, user: discord.User):
        """
        Checks if a user is an alt.

        **Example:** `.check @ACPlayGames`
        """
        if user.bot:
            await ctx.send('Please input a user, not a bot!')
        else:
            user_score = await self.is_alt(user)
            alt_footer = 'Check if the user has Nitro or Connected Accounts!'

            if 0 <= user_score <= 1:
                alt_title = 'Safe!'
                alt_description = 'This user is most likely safe!'
            elif 2 <= user_score <= 3:
                alt_title = 'Caution!'
                alt_description = 'This user is potentially an alt!'
            elif 4 <= user_score <= 5:
                alt_title = 'Warning!'
                alt_description = 'This user is most likely an alt!'

            alt_embed = discord.Embed(
                title=alt_title,
                description=alt_description,
                color=self.blue
            )
            alt_embed.set_author(
                name=user,
                icon_url=user.avatar_url
            )
            alt_embed.set_footer(text=alt_footer)
            await ctx.send(embed=alt_embed)

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

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Automatically flag any suspicious members."""
        # checks for the private_log channel
        with open('./data/options.json', 'r') as options_file:
            options = json.load(options_file)

        if not member.guild:
            return

        guild_key = str(member.guild.id)

        if guild_key not in options:
            return

        channel = options[guild_key]['private_log']

        if not channel:
            return

        channel = member.guild.get_channel(channel)

        # checks if the user is an alt
        user_score = await self.is_alt(member)
        if 3 <= user_score <= 5:
            # creating & sending the embed message
            check_embed = discord.Embed(
                title='Potential Alt!',
                color=self.blue
            )
            check_embed.set_author(
                name=member,
                icon_url=member.avatar_url
            )
            check_embed.add_field(
                name='User in Question',
                value=member.mention,
                inline=False
            )
            check_embed.add_field(
                name='Score (0 through 5)',
                value=user_score,
                inline=False
            )
            check_embed.set_footer(
                text='0-1: safe; 2-3: caution; 4-5: alt'
            )

            await channel.send(embed=check_embed)


def setup(bot):
    """Adds the Logs cog to the bot."""
    bot.add_cog(Logs(bot))
