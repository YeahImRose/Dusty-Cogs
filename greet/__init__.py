import discord
from discord.ext import commands
from redbot.core.utils.dataIO import dataIO
from redbot.core.utils import checks
from __main__ import send_cmd_help
from pathlib import Path
import os
import asyncio
import subprocess



def setup(bot):
    if youtube_dl is None:
        print("Sorry, you need youtube_dl to use the Greet cog")
        print("Please run 'pip3 install youtube_dl'")
    check_folders()
    check_files()
    n = Greet(bot, check_avconv_ffmpeg())
    bot.add_cog(n)
