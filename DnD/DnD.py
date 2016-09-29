import discord
from discord.ext import commands
from .utils.dataIO import fileIO
from .utils.chat_formatting import *
from random import randint
import datetime
import time
import os
import aiohttp
import asyncio

'''
Key for rolling settings:
(of course you can add numbers as you please, this is just helpful for verifying rolls so no one cheats)
-Stat rolls have 2 settings:
    -xdx
    -reroll 1s
-Attack rolls have 1 setting:
    -xdx
-Skill rolls have 1 setting:
    -1d20
'''

class DnD:
    def __init__(self, bot):
        self.bot = bot
        self.settings = fileIO("data/DnD/settings.json", "load")
        self.rolls = {"STR" : ""}
        self.bot.remove_command("roll")

    async def _roll(self, die: str):
        print("yes")
        results = []
        die = die.split('d')
        try:
            count = int(die[0])
            faces = int(die[1])
        except:
            return "Please use valid numbers. Format is `roll (number)d(number)`"
        for i in range(0, count):
            #try:
            x = randint(1, faces)
            #except:
                #await self.bot.say("Use valid numbers please. Format for rolling is ")
                #return "Please use valid numbers."
            results.append(x)
        results.sort(key=int)
        return results

    @commands.command(pass_context=True, no_pm=True)
    async def roll(self, ctx, die, text=None):
        """Roll a number of die of a type. You can also specify a reason

        Example:
        roll 1d6
        roll 5d20
        roll 5d6 strength"""
        author = ctx.message.author

        if die is None:
            return
        results = await self._roll(die)
        await self.bot.say(results)


def check_folders():
    if not os.path.exists("data/DnD"):
        print("Creating data/DnD folder...")
        os.makedirs("data/DnD")

def check_files():
    f = "data/DnD/settings.json"
    if not fileIO(f, "check"):
        print("Creating DnD settings.json...")
        fileIO(f, "save", {})

def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(DnD(bot))
