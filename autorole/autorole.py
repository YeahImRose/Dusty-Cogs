import discord
from discord.ext import commands
from cogs.utils import checks
from __main__ import set_cog, send_cmd_help, settings
from .utils.dataIO import fileIO
from .utils.chat_formatting import *
import aiohttp
import asyncio
import os

class Autorole:
    """Autorole commands."""

    def __init__(self, bot):
        self.bot = bot
        self.settings = fileIO("data/autorole/settings.json", "load")

    def _get_server_from_id(self, serverid):
        return discord.utils.get(self.bot.servers, id=serverid)

    async def _give_role(self, member):
        server = member.server
        if self.settings[server.id]["ENABLED"] is True:
            roleid = self.settings[server.id]["ROLE"]
            try:
                roles = server.roles
            except AttributeError:
                server = self._get_server_from_id(server)
                try:
                    roles = server.roles
                except AttributeError:
                    raise RoleNotFound(server, roleid)

            role = discord.utils.get(roles, id=roleid)
            try:
                await self.bot.add_roles(member, role)


            except discord.Forbidden:
                print("An error has occured. User that joined: {0.name}".format(member))
                print("Bot probably doesn't have permissions to manage roles. Check your discord server permissions.")
            #    print("Or you manually edited the JSON...")

    @commands.group(name="autorole", pass_context=True, no_pm=True)
    async def autorole(self, ctx):
        """ Change settings for autorole

        Requires the manage roles permission"""
        server = ctx.message.server
        if server.id not in self.settings:
            self.settings[server.id] = {}
            self.settings[server.id]["ENABLED"] = False
            self.settings[server.id]["ROLE"] = None
            fileIO("data/autorole/settings.json", "save", self.settings)

        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
            await self.bot.say("```Current autorole state: " + str(self.settings[server.id]["ENABLED"]) + " ```")

    @autorole.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def toggle(self, ctx):
        """ Enables/Disables autorole"""
        server = ctx.message.server
        if self.settings[server.id]["ROLE"] is None:
            await self.bot.say("You haven't set a role to assign to new users! Use `" + ctx.prefix + "autorole role \"role\"` to set it!")
        else:
            if self.settings[server.id]["ENABLED"] is True:
                self.settings[server.id]["ENABLED"] = False
                await self.bot.say("Autorole is now disabled.")
                fileIO("data/autorole/settings.json", "save", self.settings)
            else:
                self.settings[server.id]["ENABLED"] = True
                await self.bot.say("Autorole is now enabled.")
                fileIO("data/autorole/settings.json", "save", self.settings)

    @autorole.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def role(self, ctx, role: discord.Role):
        """ Set role for autorole to assign """
        server = ctx.message.server
        self.settings[server.id]["ROLE"] = role.id
        await self.bot.say("Autorole set to " + role.name)
        fileIO("data/autorole/settings.json", "save", self.settings)

def check_folders():
    if not os.path.exists("data/autorole"):
        print("Creating data/autorole folder...")
        os.makedirs("data/autorole")

def check_files():

    f = "data/autorole/settings.json"
    if not fileIO(f, "check"):
        print("Creating default autorole's settings.json...")
        fileIO(f, "save", {})

def setup(bot):
    check_folders()
    check_files()

    n = Autorole(bot)
    bot.add_cog(n)
    bot.add_listener(n._give_role, "on_member_join")
