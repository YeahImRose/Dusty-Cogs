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

    def _set_default(self, id):
        self.settings[id] = {
            "ROLES": [],
            "ENABLED": False
        }
        dataIO.save_json(self.path, self.settings)

    @commands.command(name="request", pass_context=True, no_pm=True)
    async def _request(self, ctx, role: str):
        """Gain the requested role if available."""
        user = ctx.message.author
        server = ctx.message.server
        add = None
        if not self.settings[server.id]["ENABLED"]:
            return

        if role.lower() in self.settings[server.id]["ROLES"]:
            try:
                role = role.lower()
                r = [x for x in server.roles if x.name.lower() == role][0]
                if r:
                    add = r
            except IndexError:
                await self.bot.say("Role not found/not requestable!")
                return

        if add:
            await self.bot.add_roles(user, add)

    @commands.group(no_pm=True, pass_context=True)
    async def rset(self, ctx):
        """Change various settings for Requester"""
        server = ctx.message.server
        if server.id not in self.settings.keys():
            self._set_default(server.id)
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @rset.command(no_pm=True, pass_context=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def toggle(self, ctx, state: str):
        """Changes or displays the state of requesting roles"""
        trues = ["true", "on", "enabled", "enable", "1"]
        falses = ["false", "off", "disabled", "disable", "0"]
        server = ctx.message.server

        s = self.settings[server.id]["ENABLED"]

        if state.lower() in trues:
            s = True
        elif state.lower() in falses:
            s = False
        else:
            await self.bot.say("Current state: {}".format(str(s).lower()))
            return

        self.settings[server.id]["ENABLED"] = s
        dataIO.save_json(self.path, self.settings)
        await self.bot.say("Set toggle state to {}".format(str(s).lower()))

    @rset.command(no_pm=True, pass_context=True)
    @checks.mod_or_permissions(manage_roles=True)
    async def addrole(self, ctx, role: str):
        """Add a role to the list of requestable roles"""
        server = ctx.message.server
        try:
            roles = self.settings[server.id]["ROLES"]
        except KeyError:
            roles = []
        role = role.lower()
        if roles:
            if [x for x in server.roles if x.name.lower() == role]:
                roles.append(role)
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
            await self.bot.say("You haven't added any roles!")
            return

        if roles:  # You can never be too safe
            if role in roles:
                roles.remove(role.lower())

        self.settings[server.id]["ROLES"] = roles
        dataIO.save_json(self.path, self.settings)
        await self.bot.say("Role {} removed.".format(role))

    @rset.command(no_pm=True, pass_context=True,
                  name="list")
    async def _list(self, ctx):
        """Lists all requestable roles"""
        server = ctx.message.server
        try:
            roles = self.settings[server.id]["ROLES"]
        except KeyError:
            roles = []

        roles = '\n'.join(roles)
        await self.bot.say("Requestable roles:\n{}".format(roles))


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
