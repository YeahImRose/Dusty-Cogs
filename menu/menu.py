import discord


def default_check(reaction, user):
    if user.bot:
        return False
    else:
        return True


class Menu():
    def __init__(self, bot):
        self.bot = bot

        # Feel free to override this in your cog if you need to
        self.emoji = {
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

    def perms(self, ctx):
        user = ctx.message.server.get_member(self.bot.user.id)
        return ctx.message.channel.permissions_for(user)

    async def _add_reactions(self, message,
                             choices: list,
                             page, emoji,
                             loop=False):
        pages = [choices[x:x + 10] for x in range(0, len(choices), 10)]
        if page > len(pages):
            page = 0
        if page:
            await self.bot.add_reaction(message, str(emoji['back']))
        for idx, i in enumerate(pages[page], 1):
            await self.bot.add_reaction(message, str(emoji[idx]))

        is_last = (page < len(pages) - 1)
        if not is_last or (is_last and loop):
            await self.bot.add_reaction(message, str(emoji['next']))
        return

    async def menu(self, ctx,
                   _type: int,
                   messages,
                   choices: int = 1,
                   **kwargs):
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
        if _type == 1:
            result = await self._number_menu(ctx, messages, choices, **kwargs)
        if _type == 2:
            result = await self._confirm_menu(ctx, messages, **kwargs)
        if _type == 3:
            result = await self._info_menu(ctx, messages, **kwargs)

        return result

    async def show_menu(self,
                        ctx,
                        message,
                        messages):
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

    async def _number_menu(self, ctx, messages, choices, **kwargs):
        page = kwargs.get('page', 0)
        timeout = kwargs.get('timeout', 15)
        check = kwargs.get('check', default_check)
        is_open = kwargs.get('is_open', False)
        emoji = kwargs.get('emoji', self.emoji)
        message = kwargs.get('message', None)
        loop = kwargs.get('loop', False)

        message = await self.show_menu(ctx, message, messages)

        await self._add_reactions(message, choices, page, emoji, loop)

        r = await self.bot.wait_for_reaction(
            emoji=list(emoji.values()),
            message=message,
            user=ctx.message.author,
            check=check,
            timeout=timeout)
        if r is None:
            return None

        reacts = {v: k for k, v in emoji.items()}
        react = reacts[r.reaction.emoji]

        if react == "next":
            page += 1
        elif react == "back":
            page -= 1
        else:
            return react

        try:
            await self.bot.remove_reaction(message, emoji[react], r.user)
        except discord.Forbidden:
            await self.bot.delete_message(message)
            message = None

        return await self._number_menu(
            ctx, message,
            choices, **kwargs)

    async def _confirm_menu(self, ctx, message, **kwargs):
        timeout = kwargs.get('timeout', 15)
        check = kwargs.get('check', default_check)
        emoji = kwargs.get('emoji', self.emoji)

        await self.bot.add_reaction(message, str(emoji['yes']))
        await self.bot.add_reaction(message, str(emoji['no']))

        r = await self.bot.wait_for_reaction(
            message=message,
            check=check,
            user=ctx.message.author,
            timeout=timeout)
        if r is None:
            return None

        reacts = {v: k for k, v in emoji.items()}
        react = reacts[r.reaction.emoji]

        if react == "no":
            return False
        else:
            return True

    async def _info_menu(self, ctx, messages, **kwargs):
        page = kwargs.get("page", 0)
        timeout = kwargs.get("timeout", 15)
        is_open = kwargs.get("is_open", False)
        check = kwargs.get("check", default_check)
        emoji = kwargs.get("emoji", self.emoji)
        message = kwargs.get("message", None)
        choices = len(messages)

        await self.show_menu(ctx, message, messages)

        await self.bot.add_reaction(message, str(emoji['back']))
        await self.bot.add_reaction(message, str(emoji['no']))
        await self.bot.add_reaction(message, str(emoji['next']))

        r = await self.bot.wait_for_reaction(
            message=message,
            user=ctx.message.author,
            check=default_check,
            timeout=timeout)
        if r is None:
            return [None, message]

        reacts = {v: k for k, v in emoji.items()}
        react = reacts[r.reaction.emoji]

        if react == "next":
            page += 1
        if react == "back":
            page -= 1
        if react == "no":
            return ["no", message]

        if page < 0:
            page = choices - 1

        if page == choices:
            page = 0

        if self.perms(ctx).manage_messages:
            await self.bot.remove_reaction(message, emoji[react], r.user)
        else:
            await self.bot.delete_message(message)
            message = None

        return await self._info_menu(
            ctx, messages,
            page=page,
            timeout=timeout,
            check=check, is_open=is_open,
            emoji=emoji, message=message)
