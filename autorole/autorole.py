import discord
from discord.ext import commands
from cogs.utils import checks
from __main__ import send_cmd_help
from .utils.dataIO import dataIO
from .utils.chat_formatting import *
import random
import string
import os


class PermissionsError:
    print("Bot probably doesn't have permissions to manage roles."
          "Check your discord server permissions.\n")


class Autorole:
    """Autorole commands."""

    def __init__(self, bot):
        self.bot = bot
        self.file_path = "data/autorole/settings.json"
        self.settings = dataIO.load_json(self.file_path)
        self.users = {}
        self.messages = {}

    def _get_server_from_id(self, serverid):
        return discord.utils.get(self.bot.servers, id=serverid)

    def _set_default(self, server):
        self.settings[server.id] = {}
        self.settings[server.id]["ENABLED"] = False
        self.settings[server.id]["ROLE"] = None
        self.settings[server.id]["AGREE_CHANNEL"] = None
        dataIO.save_json(self.file_path, self.settings)

    async def on_message(self, message):
        server = message.server
        user = message.author
        try:
            if server.id not in self.settings:
                self._set_default(server)

            ch = discord.utils.get(
                self.bot.get_all_channels(),
                id=self.settings[server.id]["AGREE_CHANNEL"])

            if message.channel != ch:
                return
        except:
            return

        if message.content == self.users[user.id]:
            roleid = self.settings[server.id]["ROLE"]
            try:
                roles = server.roles
            except AttributeError:
                print("Server roles not found, what did you even do?\n")
                return

            role = discord.utils.get(roles, id=roleid)
            try:
                await self.bot.add_roles(user, role)
                await self.bot.delete_message(message)
                if user.id in self.messages:
                    self.messages.pop(user.id, None)

            except discord.Forbidden:
                raise PermissionError

    async def _give_role(self, member):
        server = member.server
        if server.id not in self.settings:
            self._set_default(server)

        if self.settings[server.id]["ENABLED"] is True:
            if self.settings[server.id]["AGREE_CHANNEL"] is not None:
                # <3 Stackoverflow http://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python/23728630#23728630
                key = ''.join(random.choice(string.ascii_uppercase +
                                            string.digits) for _ in range(6))
                self.users[member.id] = key

                ch = discord.utils.get(
                    self.bot.get_all_channels(),
                    id=self.settings[server.id]["AGREE_CHANNEL"])

                _temp_msg = ("{.name}, please enter {} "
                             "to accept these rules".format(member, key))
                try:
                    await self.bot.send_message(member, _temp_msg)
                except:
                    msg = await self.bot.send_message(ch, _temp_msg)
                    self.messages[member.id] = msg
            else:
                roleid = self.settings[server.id]["ROLE"]
                try:
                    roles = server.roles
                except AttributeError:
                    print("Server roles not found, what did you even do?\n")
                    return

                role = discord.utils.get(roles, id=roleid)
                try:
                    await self.bot.add_roles(member, role)

                except discord.Forbidden:
                    raise PermissionError

    @commands.group(name="autorole", pass_context=True, no_pm=True)
    async def autorole(self, ctx):
        """Change settings for autorole

        Requires the manage roles permission"""
        server = ctx.message.server
        if server.id not in self.settings:
            self.settings[server.id] = {}
            self.settings[server.id]["ENABLED"] = False
            self.settings[server.id]["ROLE"] = None
            self.settings[server.id]["AGREE_CHANNEL"] = None
            dataIO.save_json(self.file_path, self.settings)

        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
            await self.bot.say("```Current autorole state: {}```".format(
                self.settings[server.id]["ENABLED"]))

    @autorole.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def toggle(self, ctx):
        """Enables/Disables autorole"""
        server = ctx.message.server
        if self.settings[server.id]["ROLE"] is None:
            await self.bot.say("You haven't set a role to give to new users! "
                               "Use `{}autorole role \"role\"` to set it!"
                               .format(ctx.prefix))
        else:
            if self.settings[server.id]["ENABLED"] is True:
                self.settings[server.id]["ENABLED"] = False
                await self.bot.say("Autorole is now disabled.")
                dataIO.save_json(self.file_path, self.settings)
            else:
                self.settings[server.id]["ENABLED"] = True
                await self.bot.say("Autorole is now enabled.")
                dataIO.save_json(self.file_path, self.settings)

    @autorole.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def role(self, ctx, role: discord.Role):
        """Set role for autorole to assign.

        Use quotation marks around the role if it contains spaces."""
        server = ctx.message.server
        self.settings[server.id]["ROLE"] = role.id
        await self.bot.say("Autorole set to " + role.name)
        dataIO.save_json(self.file_path, self.settings)

    @autorole.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def channel(self, ctx, channel: str):
        """Set the channel that will be used for accepting the rules.

        Entering only \"#\" will disable this."""
        server = ctx.message.server
        if channel.startswith("#"):
            channel = channel[1:]
        if channel == "":
            self.settings[server.id]["AGREE_CHANNEL"] = None
            await self.bot.say("Agreement channel cleared")
        for x in ctx.message.server.channels:
            if x.name == channel:
                self.settings[server.id]["AGREE_CHANNEL"] = x.id
                await self.bot.say("Agreement channel "
                                   "set to {}".format(x.name))
        dataIO.save_json(self.file_path, self.settings)


def check_folders():
    if not os.path.exists("data/autorole"):
        print("Creating data/autorole folder...")
        os.makedirs("data/autorole")


def check_files():

    f = "data/autorole/settings.json"
    if not dataIO.is_valid_json(f):
        print("Creating default autorole's settings.json...")
        dataIO.save_json(f, {})


def setup(bot):
    check_folders()
    check_files()

    n = Autorole(bot)
    bot.add_cog(n)
    bot.add_listener(n._give_role, "on_member_join")
