import discord
import os
from cogs.utils.dataIO import dataIO
from discord.ext import commands
from cogs.utils import checks
from __main__ import send_cmd_help


class Requester:
    def __init__(self, bot):
        self.bot = bot
        self.path = "data/requester/settings.json"
        self.settings = dataIO.load_json(self.path)

    @commands.command(name="request", pass_context=True, no_pm=True)
    async def _request(self, ctx, role: str):
        """Gain the role of the requested role if it is included in the role list."""
        user = ctx.message.author
        server = ctx.message.server
        add = None
        if not self.settings[server.id]["ENABLED"]:
            return

        if role.lower() in self.settings[server.id]["ROLES"]:
            r = [x for x in server.roles if x.name.lower() == role.lower()][0]
            if r:
                add = r

        if add:
            await self.bot.add_roles(user, add)

    @commands.group(pass_context=True)
    async def rset(self, ctx):
        """Change various settings for Requester"""
        server = ctx.message.server
        try:
            x = self.settings[server.id]
        except:
            self.settings[server.id] = {}
        if self.settings[server.id] is None:
            self.settings[server.id] = {"ROLES": [],
                                        "ENABLED": False}
        if ctx.invoked_subcommand is None:
            return await send_cmd_help(ctx)

    @rset.command(no_pm=True, pass_context=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def toggle(self, ctx, state: str):
        """Changes or displays the state of requesting roles"""
        trues = ["true", "on", "enabled", "enable", "1"]
        falses = ["false", "off", "disabled", "disable", "0"]
        server = ctx.message.server

        try:
            s = self.settings[server.id]["ENABLED"]
        except KeyError:
            s = False

        if state.lower() in trues:
            s = True
        elif state.lower() in falses:
            s = False
        else:
            return await self.bot.say("Current state: {}".format(str(s).lower()))

        self.settings[server.id]["ENABLED"] = bool(s)
        dataIO.save_json(self.path, self.settings)
        await self.bot.say("State set toggle {}".format(str(s).lower()))

    @rset.command(no_pm=True, pass_context=True)
    @checks.mod_or_permissions(manage_roles=True)
    async def addrole(self, ctx, role: str):
        """Add a role to the list of requestable roles"""
        server = ctx.message.server
        try:
            roles = self.settings[server.id]["ROLES"]
        except KeyError:
            roles = []

        if roles:
            if [x for x in server.roles if x.name == role]:
                roles.append(role.lower())
        else:
            roles = [role]

        self.settings[server.id]["ROLES"] = roles
        dataIO.save_json(self.path, self.settings)
        await self.bot.say("Role {} added.".format(role))

    @rset.command(no_pm=True, pass_context=True)
    @checks.mod_or_permissions(manage_roles=True)
    async def delrole(self, ctx, role: str):
        """Remove a role from the list of requestable roles"""
        server = ctx.message.server
        try:
            roles = self.settings[server.id]["ROLES"]
        except KeyError:
            roles = []

        if roles:
            if role in roles:
                roles.remove(role.lower())

        self.settings[server.id]["ROLES"] = roles
        dataIO.save_json(self.path, self.settings)
        await self.bot.say("Role {} removed.".format(role))


def check_folders():
    if not os.path.exists("data/requester"):
        print("Creating data/requester folder...")
        os.makedirs("data/requester")


def check_files():
    f = "data/requester/settings.json"
    if not dataIO.is_valid_json(f):
        print("Creating default requester's settings.json...")
        dataIO.save_json(f, {})


def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(Requester(bot))
