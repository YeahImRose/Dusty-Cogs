import discord


def default_check(reaction, user):
    if user.bot:
        return False
    else:
        return True

# Feel free to override this in your cog if you need to
emoji = {
    0: "0⃣",
    1: "1⃣",
    2: "2⃣",
    3: "3⃣",
    4: "4⃣",
    5: "5⃣",
    6: "6⃣",
    7: "7⃣",
    8: "8⃣",
    9: "9⃣",
    10: "🔟",
    "next": "➡",
    "back": "⬅",
    "yes": "✅",
    "no": "❌"
}


class menu_info(object):
    def __init__(self,
                 page: int=0,
                 timeout: int=15,
                 check=default_check,
                 is_open: bool=False,
                 _emoji=emoji,
                 message=None,
                 loop: bool=False):
        self.page = page
        self.timeout = timeout
        self.check = check
        self.is_open = is_open
        self.emoji = _emoji
        self.message = message
        self.loop = loop


class Menu():
    def __init__(self, bot):
        self.bot = bot

    def perms(self, ctx):
        user = ctx.message.server.get_member(self.bot.user.id)
        return ctx.message.channel.permissions_for(user)

    async def _add_reactions(self,
                             choices: list,
                             info: menu_info):
        pages = [choices[x:x + 10] for x in range(0, len(choices), 10)]
        _emoji = info.emoji
        if info.page > len(pages):
            info.page = 0
        if info.page:
            await self.bot.add_reaction(info.message, str(_emoji['back']))
        for idx, i in enumerate(pages[info.page], 1):
            await self.bot.add_reaction(info.message, str(_emoji[idx]))

        is_last = (info.page == len(pages) - 1)
        if not is_last or (is_last and info.loop):
            await self.bot.add_reaction(info.message, str(_emoji['next']))
        return

    async def menu(self, ctx,
                   _type: int,
                   messages,
                   choices: int = 1,
                   info: menu_info = None):
        """Creates and manages a new menu

        Required arguments:
            Type:
                1- number menu
                2- confirmation menu
                3- info menu (basically menu pagination)

            Messages:
                Strings or embeds to use for the menu.
                Pass as a list for number menu

        Optional agruments:
            page (Defaults to 0):
                The message in messages that will be displayed

            timeout (Defaults to 15):
                The number of seconds until the menu automatically expires

            check (Defaults to default_check):
                The same check that wait_for_reaction takes

            is_open (Defaults to False):
                Whether or not the menu can take input from any user

            emoji (Decaults to self.emoji):
                A dictionary containing emoji to use for the menu.
                If you pass this, use the same naming scheme as self.emoji

            message (Defaults to None):
                The discord.Message to edit if present

            loop (Defaults to False):
                Whether or not the pages loop to the first page at the end"""
        result = None
        if info is None:
            info = menu_info()
        if _type == 1:
            result = await self._number_menu(ctx, messages, choices, info)
        if _type == 2:
            result = await self._confirm_menu(ctx, messages, info)
        if _type == 3:
            result = await self._info_menu(ctx, messages, info)

        return result

    async def show_menu(self, ctx, message, messages):
        if message:
            if type(messages) == discord.Embed:
                await self.bot.edit_message(message, embed=messages)
            else:
                await self.bot.edit_message(message, messages)
        else:
            if type(messages) == discord.Embed:
                return await self.bot.send_message(ctx.message.channel,
                                                   embed=messages)
            else:
                return await self.bot.say(messages)

    async def _number_menu(self, ctx, messages, choices, info: menu_info):
        info.message = await self.show_menu(ctx, info.message, messages)

        await self._add_reactions(choices, info)

        r = await self.bot.wait_for_reaction(
            emoji=list(info.emoji.values()),
            message=info.message,
            user=ctx.message.author,
            check=info.check,
            timeout=info.timeout)
        if r is None:
            return None

        reacts = {v: k for k, v in info.emoji.items()}
        react = reacts[r.reaction.emoji]

        if react == "next":
            info.page += 1
        elif react == "back":
            info.page -= 1
        else:
            return react

        try:
            await self.bot.remove_reaction(info.message,
                                           info.emoji[react], r.user)
        except discord.Forbidden:
            await self.bot.delete_message(info.message)
            info.message = None

        return await self._number_menu(
            ctx, messages,
            choices, info)

    async def _confirm_menu(self, ctx, info: menu_info):
        await self.bot.add_reaction(info.message, str(info.emoji['yes']))
        await self.bot.add_reaction(info.message, str(info.emoji['no']))

        r = await self.bot.wait_for_reaction(
            message=info.message,
            check=info.check,
            user=ctx.message.author,
            timeout=info.timeout)
        if r is None:
            return None

        reacts = {v: k for k, v in info.emoji.items()}
        react = reacts[r.reaction.emoji]

        if react == "no":
            return False
        else:
            return True

    async def _info_menu(self, ctx, messages, info: menu_info):
        choices = len(messages)

        await self.show_menu(ctx, info.message, messages)

        await self.bot.add_reaction(info.message, str(info.emoji['back']))
        await self.bot.add_reaction(info.message, str(info.emoji['no']))
        await self.bot.add_reaction(info.message, str(info.emoji['next']))

        r = await self.bot.wait_for_reaction(
            message=info.message,
            user=ctx.message.author,
            check=info.check,
            timeout=info.timeout)
        if r is None:
            return [None, info.message]

        reacts = {v: k for k, v in info.emoji.items()}
        react = reacts[r.reaction.emoji]

        if react == "next":
            info.page += 1
        if react == "back":
            info.page -= 1
        if react == "no":
            return ["no", info.message]

        if info.page < 0:
            info.page = choices - 1

        if info.page == choices:
            info.page = 0

        if self.perms(ctx).manage_messages:
            await self.bot.remove_reaction(info.message,
                                           info.emoji[react], r.user)
        else:
            await self.bot.delete_message(info.message)
            info.message = None

        return await self._info_menu(
            ctx, messages, info)
