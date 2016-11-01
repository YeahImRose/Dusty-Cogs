import discord
from discord.ext import commands
from .utils.dataIO import dataIO
from __main__ import send_cmd_help
from .utils.chat_formatting import *
from cogs.utils import checks
import os, io
import aiohttp
import asyncio

class desutils:
    def __init__(self, bot):
        self.bot = bot

    @checks.mod_or_permissions(manage_roles=True)
    @commands.command(pass_context=True, no_pm=True)
    async def roles(self, ctx):
        roles = ""
        for x in ctx.message.server.roles:
            roles += ((str(x.name).ljust(30)) + str(x.id) + "\n")
        await self.bot.say("```{0}```".format(roles))

    @checks.is_owner()
    @commands.command(pass_context=True, no_pm=True)
    async def sendcog(self, ctx, filepath: str):
        fp = "cogs/{0}.py".format(filepath)
        if os.path.exists(fp):
            await self.bot.send_file(ctx.message.channel, fp)
        else:
            await self.bot.say("Cog not found!")

    @checks.mod_or_permissions(manage_messages=True)
    @commands.command(pass_context=True)
    async def pin(self, ctx, text: str, user: discord.User = None):
        """Pin a recent message, useful on mobile.

        Usage:
            pin word
            pin "More than one word"
            pin "More than one word but said by" @someone """
        channel = ctx.message.channel
        if not text:
            return await send_cmd_help(ctx)
        else:
            #logs = yield from self.bot.logs_from(ctx.message.channel)
            if user and text:
                async for x in self.bot.logs_from(channel):
                    if x.content.startswith(text) and x.author.id == user.id:
                        return await self.bot.pin_message(x)
            elif text:
                async for x in self.bot.logs_from(channel):
                    if x.content.startswith(text):
                        return await self.bot.pin_message(x)
            else:
                await self.bot.say("AAAAAAAAAAAAAAAA SOMETHING WENT WRONG THAT SHOULDN'T HAVE!!!!!!!")

    @checks.mod_or_permissions(manage_messages=True)
    @commands.command(pass_context=True)
    async def unpin(self, ctx, text: str, user: discord.User = None):
        """Unpin a message pinned in the current channel.

        Usage is the same as the pin command"""

        channel = ctx.message.channel
        if not text:
            return await send_cmd_help(ctx)
        for x in (await self.bot.pins_from(channel)):
            if text and user:
                if x.content.startswith(text) and x.author == user:
                    return await self.bot.unpin_message(x)
            elif text and x.content.startswith(text):
                return await self.bot.unpin_message(x)

    async def prefixes(self, message):
        if message.content == "prefixes":
            await self.bot.send_message(message.channel, "```{0}```".format(', '.join([x for x in self.bot.command_prefix])))

    @checks.is_owner()
    @commands.command(pass_context=True, no_pm=True)
    async def listcogs(self, ctx):
        """Shows the status of cogs.

        + means the cog is loaded
        - means the cog is unloaded
        ? means the cog couldn't be found(it was probably removed manually)"""

        all_cogs = dataIO.load_json("data/red/cogs.json")
        loaded, unloaded, other = ("",)*3
        cogs = self.bot.cogs['Owner']._list_cogs()

        for x in all_cogs:
            if all_cogs.get(x):
                if x in cogs:
                    loaded += "+\t{0}\n".format(x.split('.')[1])
                else:
                    other += "?\t{0}\n".format(x.split('.')[1])
            elif x in cogs:
                unloaded += "-\t{0}\n".format(x.split('.')[1])
        await self.bot.say("```diff\n{0}{1}{2}```".format(loaded, unloaded, other))

    @checks.is_owner()
    @commands.command(pass_context=True, no_pm=True)
    async def perms(self, ctx, user: discord.Member):
        perms = iter(ctx.message.channel.permissions_for(user))
        perms_we_have = "```diff\n"
        perms_we_dont = ""
        for x in perms:
            if "True" in str(x):
                perms_we_have += "+\t{0}\n".format(str(x).split('\'')[1])
            else:
                perms_we_dont += ("-\t{0}\n".format(str(x).split('\'')[1]))
        await self.bot.say("{0}{1}```".format(perms_we_have, perms_we_dont))

    @checks.mod_or_permissions(manage_roles=True)
    @commands.command(pass_context=True, no_pm=True)
    async def roles(self, ctx):
        roles = ""
        for x in ctx.message.server.roles:
            roles += x.name + '\n'
        await self.bot.say("```{0}```".format(roles))

def setup(bot):
    n = desutils(bot)
    bot.add_listener(n.prefixes, 'on_message')
    bot.add_cog(n)
