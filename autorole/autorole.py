import discord
from discord.ext import commands
from cogs.checks import *
from JSONman import JMan
import random
import string


class Autorole:
    """Autorole commands."""

    def __init__(self, bot):
        self.bot = bot
        self.data = JMan("data")
        self.users = {}
        self.messages = {}

    def _get_server_from_id(self, serverid):
        return discord.utils.get(self.bot.servers, id=serverid)

    def _set_default(self, server):
        self.data[server.id] = {
            "ENABLED": False,
            "ROLE": None,
            "AGREE_CHANNEL": None,
            "AGREE_MSG": None
        }
        self.data.save()

    async def _no_perms(self, server):
        m = ("It appears that you haven't given this "
             "bot enough permissions to use autorole. "
             "The bot requires the \"Manage Roles\" and "
             "the \"Manage Messages\" permissions in"
             "order to use autorole. You can change the "
             "permissions in the \"Roles\" tab of the "
             "server settings.")
        await self.bot.send_message(server, m)

    async def on_message(self, message):
        server = message.server
        user = message.author
        if server is None:
            return
        if server.id not in self.data:
            self._set_default(server)
            return
        try:
            if self.data[server.id]["AGREE_CHANNEL"] is not None:
                pass
            else:
                return
        except:
            return

        try:
            if message.content == self.users[user.id]:
                roleid = self.data[server.id]["ROLE"]
                try:
                    roles = server.roles
                except AttributeError:
                    print("This server has no roles... what even?\n")
                    return

                role = discord.utils.get(roles, id=roleid)
                try:
                    await self.bot.add_roles(user, role)
                    await self.bot.delete_message(message)
                    if user.id in self.messages:
                        self.messages.pop(user.id, None)
                except discord.Forbidden:
                    if server.id in self.data:
                        await self._no_perms(server)
        except KeyError:
            return

    async def _agree_maker(self, member):
        server = member.server
        self.last_server = server
        await self._verify_json(None)
        key = ''.join(random.choice(string.ascii_uppercase +
                                    string.digits) for _ in range(6))
        # <3 Stackoverflow http://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python/23728630#23728630
        self.users[member.id] = key
        ch = discord.utils.get(
            self.bot.get_all_channels(),
            id=self.data[server.id]["AGREE_CHANNEL"])
        msg = self.data[server.id]["AGREE_MSG"]
        try:
            msg = msg.format(key=key,
                             member=member,
                             name=member.name,
                             mention=member.mention,
                             server=server.name)
        except:
            pass

        try:
            msg = await self.bot.send_message(member, msg)
        except discord.Forbidden:
            msg = await self.bot.send_message(ch, msg)
        self.messages[member.id] = msg

    async def _auto_give(self, member):
        server = member.server
        try:
            roleid = self.data[server.id]["ROLE"]
            roles = server.roles
        except KeyError:
            return
        except AttributeError:
            print("This server has no roles... what even?\n")
            return
        role = discord.utils.get(roles, id=roleid)
        try:
            await self.bot.add_roles(member, role)
        except discord.Forbidden:
            if server.id in self.data:
                await self._no_perms(server)

    async def _verify_json(self, e, *a, **k):
        s = self.last_server
        if len(self.data[s.id].keys()) >= 4:
            return
        try:
            _d = self.data[s.id]
        except KeyError:
            self._set_default(s)
        _k = _d.keys()

        # Fix any potential JSON issues because I break things a lot
        if "ENABLED" not in _k:
            self._set_default(s)
            print("Please stop messing with the autorole JSON\n")
            return
        if "ROLE" not in _k:
            self._set_default(s)
            print("Please stop messing with the autorole JSON\n")
            return
        if "AGREE_CHANNEL" not in _k:
            self.data[s.id]["AGREE_CHANNEL"] = None
        if "AGREE_MSG" not in _k:
            self.data[s.id]["AGREE_MSG"] = None

    async def _roler(self, member):
        server = member.server
        self.last_server = server  # In case something breaks
        if server.id not in self.data:
            self._set_default(server)

        if self.data[server.id]["ENABLED"] is True:
            if self.data[server.id]["AGREE_CHANNEL"] is not None:
                await self._agree_maker(member)
            else:  # Immediately give the new user the role
                await self._auto_give(member)

    @commands.group(name="autorole", pass_context=True, no_pm=True)
    async def autorole(self, ctx):
        """Change settings for autorole

        Requires the manage roles permission"""
        server = ctx.message.server
        if server.id not in self.data:
            self.data[server.id] = {
                "ENABLED": False,
                "ROLE": None,
                "AGREE_CHANNEL": None,
                "AGREE_MSG": None
            }
            self.data.save()
        if "AGREE_MSG" not in self.data[server.id].keys():
            self.data[server.id]["AGREE_MSG"] = None
            self.data.save()

        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)
            try:
                await self.bot.say("```Current autorole state: {}```".format(
                    self.data[server.id]["ENABLED"]))
            except KeyError:
                self._set_default(server)

    @autorole.command(pass_context=True, no_pm=True)
    @has_permissions(manage_roles=True)
    async def toggle(self, ctx):
        """Enables/Disables autorole"""
        server = ctx.message.server
        if self.data[server.id]["ROLE"] is None:
            await self.bot.say("You haven't set a role to give to new users! "
                               "Use `{}autorole role \"role\"` to set it!"
                               .format(ctx.prefix))
        else:
            if self.data[server.id]["ENABLED"] is True:
                self.data[server.id]["ENABLED"] = False
                await self.bot.say("Autorole is now disabled.")
                self.data.save()
            else:
                self.data[server.id]["ENABLED"] = True
                await self.bot.say("Autorole is now enabled.")
                self.data.save()

    @autorole.command(pass_context=True, no_pm=True)
    @has_permissions(manage_roles=True)
    async def role(self, ctx, role: discord.Role=None):
        """Set role for autorole to assign.

        Use quotation marks around the role if it contains spaces."""
        if role is None:
            await self.bot.send_cmd_help(ctx)
        server = ctx.message.server
        self.data[server.id]["ROLE"] = role.id
        await self.bot.say("Autorole set to " + role.name)
        self.data.save()

    @autorole.command(pass_context=True, no_pm=True)
    @has_permissions(manage_roles=True)
    async def agreement(self, ctx, *, msg: str):
        """Set the channel that will be used for accepting the rules.
        This is not needed and is completely optional

        Entering only \"#\" will disable this."""
        server = ctx.message.server
        channel = msg.split(" ")[0]
        msg = msg.split(" ")[1:]
        msg = ' '.join(msg)
        ch = None

        if channel.startswith("<#"):
            channel = channel[2:]
            channel = int(channel[:-1])
        if channel == "#":  # yes, I know this could break- but it's not my fault if the user is dumb enough to break it
            self.data[server.id]["AGREE_CHANNEL"] = None
            await self.bot.say("Agreement channel cleared")
            return
        else:
            if type(channel) == str:
                ch = discord.utils.get(server.channels, name=channel)
            else:
                ch = discord.utils.get(server.channels, id=str(channel))
            try:
                self.data[server.id]["AGREE_CHANNEL"] = ch.id
            except AttributeError as e:
                await self.bot.say("Channel not found!")
            if not msg:
                msg = "{name} please enter this code: {key}"
            self.data[server.id]["AGREE_MSG"] = msg
            await self.bot.say("Agreement channel "
                               "set to {}".format(ch.name))
        self.data.save()


def setup(bot):
    n = Autorole(bot)
    bot.add_cog(n)
    bot.add_listener(n._roler, "on_member_join")
    bot.add_listener(n._verify_json, "on_error")
