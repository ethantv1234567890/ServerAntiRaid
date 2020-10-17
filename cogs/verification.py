"""Verification Cog, verifies members upon joining the guild with a captcha."""

import asyncio
import json
import random
import string

from captcha.image import ImageCaptcha
import discord
from discord.ext import commands


class Verification(commands.Cog):
    """Helps verify members."""
    def __init__(self, bot):
        self.bot = bot
        self.blue = discord.Color.blue()
        self.captcha_in_progress = []

    img = ImageCaptcha()

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

    async def verify_captcha(self, member):
        """Creates, sends, and verifies a member with a captcha."""
        if member not in self.captcha_in_progress:
            guild = member.guild
            captcha_text = ''.join(random.choices(
                string.ascii_letters + string.digits, k=5  # captcha length
            ))
            captcha_img = self.img.generate(captcha_text)
            captcha_file = discord.File(
                fp=captcha_img,
                filename='captcha.png'  # file name cannot include underscores
            )

            captcha_embed = discord.Embed(
                title='Captcha Verification',
                description='Welcome! Please verify that you are not a robot!',
                color=self.blue
            )
            captcha_embed.set_image(url='attachment://captcha.png')
            captcha_embed.set_footer(text='Please type the text in the image!')
            await member.send(file=captcha_file, embed=captcha_embed)

            def check_captcha(msg):
                return msg.content == captcha_text and msg.author == member

            guild_key = str(guild.id)
            with open('./data/options.json', 'r') as options_file:
                options = json.load(options_file)

            try:
                self.captcha_in_progress.append(member)
                await self.bot.wait_for(
                    'message',
                    timeout=30,
                    check=check_captcha
                )
            except asyncio.TimeoutError:  # ran out of time
                self.captcha_in_progress.remove(member)
                await member.send('Captcha expired! Please do `.captcha`!')
            except discord.Forbidden:  # not allowed to DM
                # sends msg to moderators, does nothing if it cannot find them
                self.captcha_in_progress.remove(member)
                if guild_key in options:
                    private_log = options[guild_key]['private_log']
                    if private_log is not None:
                        private_log = guild.get_channel(private_log)
                        await private_log.send(
                            f'Sorry, I cannot DM and verify **{member}**!'
                        )
                    else:
                        pass
                else:
                    pass
            else:  # captcha solved
                self.captcha_in_progress.remove(member)
                # checks for Member role, gives to user if it exists
                await self.add_guild(guild)

                member_role = options[guild_key]['member_role']
                if member_role is not None:
                    member_role = guild.get_role(member_role)
                    await member.add_roles(
                        member_role,
                        reason='Captcha Verified!'
                    )
                    await member.send(f'Verified! Welcome to **{guild}**!')
                else:
                    await member.send(
                        'Sorry, there is no member role for this guild!'
                    )
        else:
            try:
                await member.send('You have an unsolved captcha!')
            except discord.Forbidden:  # not allowed to DM
                pass

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Attempts to verify member upon joining."""
        if not member.bot:
            await self.verify_captcha(member)

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def captcha(self, ctx, guild_id: int = None):
        """DMs captcha to the user for verification."""
        if ctx.guild is not None:  # command is in guild
            guild = ctx.guild
            member = ctx.author
        else:  # command is in DMs
            if guild_id is not None:  # guild ID is provided
                guild = self.bot.get_guild(guild_id)
                if guild is not None:  # a valid guild has been provided
                    member = guild.get_member(ctx.author.id)
                else:  # invalid guild
                    await ctx.send('Please provide a valid guild ID!')
                    return
            else:  # guild ID is not provided
                await ctx.send('Please provide a guild ID for verification!')
                return

        # checks if the "captcha" option is enabled for the guild
        guild_key = str(guild.id)
        with open('./data/options.json', 'r') as options_file:
            options = json.load(options_file)

        await self.add_guild(guild)

        if not options[guild_key]['captcha']:  # "captcha" disabled
            return

        await self.verify_captcha(member)

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.member)
    async def verify(self, ctx, member: discord.Member):
        """For moderators only, manually verify a user without captcha."""
        # checks if the "captcha" option is enabled for the guild
        guild_key = str(ctx.guild.id)
        with open('./data/options.json', 'r') as options_file:
            options = json.load(options_file)

        await self.add_guild(ctx.guild)

        if options[guild_key]['captcha']:  # "captcha" enabled
            member_role = options[guild_key]['member_role']
            if member_role is not None:
                member_role = ctx.guild.get_role(member_role)
                await member.add_roles(
                    member_role,
                    reason='Manually Verified!'
                )
                await member.send(f'Verified! Welcome to **{ctx.guild}**!')
            else:
                await ctx.send(
                    'Sorry, there is no member role for this guild!'
                )


def setup(bot):
    """Adds the Verification cog to the bot."""
    bot.add_cog(Verification(bot))
