import discord
from discord.ext import commands
from .utils.dataIO import fileIO
from .utils.chat_formatting import *
from random import randint
from __main__ import send_cmd_help
import datetime, heapq, time
import os
import aiohttp
import asyncio

__author__ = "Lunar Dust"
__version__ = "0.1"

'''
Key for rolling settings:
(of course you can add numbers as you please, this is just helpful for verifying rolls so no one cheats)
-Stat rolls have 3 normal settings:
    -4d6 drop lowest (default)
    -reroll 1s
    -5d6 drop lowest 2

    Special:
    -user defined roll (format: *d*b*)
'''

class Pathfinder:
    def __init__(self, bot):
        self.bot = bot
        self.settings = fileIO("data/pathfinder/settings.json", "load")
        self.messages = []
        self.bot.remove_command("roll")

    #Not sure what I did here...
    async def _clean(self, ctx, begins: str = None):
        if not self.messages:
            return
        if begins is None:
            await self.bot.delete_message(self.messages[-1])
            self.messages.pop()
        else:
            to_del = []
            for x in self.messages:
                msg = await self.bot.get_message(ctx.message.channel, x.id)
                if msg.content.startswith(begins):
                    to_del.append(msg)
            print(self.messages)
            if len(to_del) > 1:
                await self.bot.delete_messages(to_del)
                self.messages = [x for x in self.messages if x not in to_del]
            else:
                await self.bot.delete_message(to_del[0])
                self.messages.pop()

    async def _raw_roll(self, count, faces):
        results = []
        for i in range(0, count):
            x = randint(1, faces)
            results.append(x)
        results.sort(key=int)
        return results

    async def _ezconv(self, var, typ):
        #this is dumb
        thing = None
        try:
            thing = typ(var)
        except:
            return None
        return thing


    async def _roll(self, ctx, die: str):
        results = []
        count, faces, best = (None,)*3 #magic
        import re
        die = re.split('d|b', die)
        try:
            count = await self._ezconv(die[0], int)
            faces = await self._ezconv(die[1], int)
            best = await self._ezconv(die[2], int)
        except IndexError:
            pass
        if best is None:
            best = 0
        if count is None:
            count = 1
        try:
            if (count < 1 or count > 1000) or (faces < 1 or faces is None) or best < 0:
                pass
        except:
            return "{0.mention} Please use valid numbers. Format is `roll [number]d<number>`".format(ctx.message.author)
        for i in range(0, count):
            x = randint(1, faces)
            results.append(x)
        if best > 0:
            results = heapq.nlargest(best, results)
        results.sort(key=int)
        return results

    @commands.group(pass_context=True, no_pm=True, invoke_without_command=True)
    async def roll(self, ctx, die: str = None):
        """Roll a die with x sides; Has option for rolling x die.

        Examples:
        roll 5d20
        roll d10"""

        if die is not None:
            results = await self._roll(ctx, die)
            if str(results).startswith('['):
                sent = await self.bot.send_message(ctx.message.channel, ctx.message.author.mention + " rolled a " + str(results).strip('[]'))
            else:
                await self.bot.say(results)
        else:
            await self._clean(ctx, "```")
            pages = self.bot.formatter.format_help_for(ctx, ctx.command)
            for page in pages:
                sent = await self.bot.send_message(ctx.message.channel, page)
            self.messages.append(sent)

    @roll.command(pass_context=True, no_pm=True)
    async def stats(self, ctx, mode: str = None):
        """Roll stats based on chosen mode. Defaults to 4d6 drop lowest.
        Modes:
          4d6     Roll 4 d6's and drop the lowest roll
          5d6     Roll 5 d6's and drop the lowest two rolls
          re1s    Roll 4 d6's and reroll any 1's once"""
        server = ctx.message.server
        author = ctx.message.author

        if mode is None:
            try:
                mode = self.settings[server.id]["STATS"]
            except KeyError:
                self.settings[server.id] = {"STATS": "4d6"}
                mode = "4d6"

        stats = []

        if mode == "4d6":
            die = "4d6"
            for i in range(0, 7):
                results = await self._roll(ctx, die)
                lows = []
                lows.append(min(results))
                results.remove(min(results))
                stats.append(str(sum(results)).ljust(5) + (str(results).strip('[]')).ljust(13) + (str(lows).strip('[]')) )
        elif mode == "5d6":
            die = "5d6"
            for i in range(0, 7):
                results = await self._roll(ctx, die)
                lows = []
                for i in range(0, 2):
                    lows.append(min(results))
                    results.remove(min(results))
                stats.append(str(sum(results)).ljust(5) + (str(results).strip('[]')).ljust(13) + (str(lows).strip('[]')) )
        elif mode == "re1s":
            die = "4d6"
            for i in range(0, 7):
                results = []
                results = await self._roll(ctx, die)
                lows = []
                if(results.count(1) > 0):
                    count = results.count(1)
                    results = [x for x in results if x != 1]
                    thing = await self._raw_roll(count, 6)
                    for y in range(0, count):
                        results.append(thing[y])
                lows.append(min(results))
                results.remove(min(results))
                stats.append(str(sum(results)).ljust(5) + (str(results).strip('[]')).ljust(13) + (str(lows).strip('[]')) )
        else:
            die = str(mode)
            for i in range(0, 7):
                try:
                    results = await self._roll(ctx, die)
                    stats.append(str(sum(results)).ljust(5) + (str(results).strip('[]')).ljust(13) )
                except:
                    return
        await self.bot.say("{0.mention}'s stat roll:```\nStat           Total  Counted   Not counted\nStrength:\t\t{1}\nDexterity:\t   {2}\nConstitution:\t{3}\nIntelligence:\t{4}\nWisdom:\t\t  {5}\nCharisma:\t\t{6}```".format(author, stats[0], stats[1], stats[2], stats[3], stats[4], stats[5], stats[6]))

def check_folders():
    if not os.path.exists("data/pathfinder"):
        print("Creating data/pathfinder folder...")
        os.makedirs("data/pathfinder")

def check_files():
    f = "data/pathfinder/settings.json"
    if not fileIO(f, "check"):
        print("Creating pathfinder settings.json...")
        fileIO(f, "save", {})

def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(Pathfinder(bot))
