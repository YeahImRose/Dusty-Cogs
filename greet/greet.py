import discord
from discord.ext import commands
from .utils.dataIO import dataIO
from .utils import checks
from __main__ import send_cmd_help
from pathlib import Path
import os
import asyncio
import subprocess

try:
    import youtube_dl
except:
    youtube_dl = None

ydl_opts = {
    'source_address': '0.0.0.0',
    'format': 'bestaudio/best',
    'extractaudio': True,
    'audioformat': "mp3",
    'outtmpl': '%(id)s',
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': True,
    'quiet': True,
    'no_warnings': True,
    'outtmpl': "data/greet/sounds/%(id)s",
    'default_search': 'auto'
}


class Greet:
    """Plays a sound effect when a user joins a channel"""

    def __init__(self, bot, player):
        self.bot = bot
        self.file_path = "data/greet/settings.json"
        self.settings = dataIO.load_json(self.file_path)
        self.player = player

    def voice_client(self, server):
        return self.bot.voice_client_in(server)

    async def _join_voice_channel(self, channel):
        try:
            await self.bot.join_voice_channel(channel)
        except asyncio.futures.TimeoutError as e:
            print(e)
            print("We timed out connecting to a voice channel")

    async def _create_ffmpeg_player(self, server, channel,
                                    filename, local=False):
        """This function will guarantee we have a valid voice client,
            even if one doesn't exist previously."""
        voice_client = self.voice_client(server)

        if voice_client is None:
            await self._join_voice_channel(channel)

        # Okay if we reach here we definitively have a working voice_client
        song_filename = os.path.join("data/greet/sounds", filename)

        use_avconv = False
        if self.player == "avconv":
            use_avconv = True
        options = '-b:a 64k -bufsize 64k'

        try:
            voice_client.audio_player.process.kill()
            # print("killed old player")
        except AttributeError:
            pass
        except ProcessLookupError:
            pass

        voice_client.audio_player = voice_client.create_ffmpeg_player(song_filename,
                                                                      use_avconv=use_avconv,
                                                                      options=options)
        voice_client.audio_player.volume = 50
        return voice_client

    @commands.group(pass_context=True, no_pm=True)
    async def greetset(self, ctx):
        """Sets welcome module settings"""
        if ctx.message.author.bot:
            return
        server = ctx.message.server
        if str(server.id) not in self.settings.keys():
            self.settings[server.id] = {"ENABLED": False}
            dataIO.save_json(self.file_path, self.settings)
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @greetset.command(pass_context=True)
    async def sound(self, ctx,
                    user: discord.Member = None,
                    path_or_url: str = None):
        """Set the sound file to play when a user joins a voice channel."""
        server = ctx.message.server
        songinfo = None
        temppath = None
        if user is not None:
            if user.id not in self.settings[server.id]:
                self.settings[server.id][user.id] = [False, ""]
        else:
            user = ctx.message.author
            if user.id not in self.settings[server.id]:
                self.settings[server.id][ctx.message.author.id] = [False, ""]
            await send_cmd_help(ctx)
            return

        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                songinfo = ydl.extract_info(path_or_url, download=False)
        except:
            pass

        if songinfo is not None:
            try:
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([path_or_url])
            except:
                await self.bot.say("Invalid URL or issue downloading video!")
                return
            temppath = os.path.join("data/greet/sounds", songinfo["id"])
            temppath = Path(temppath)
            path_or_url = songinfo['id']
        else:
            temppath = os.path.join("data/greet/sounds", path_or_url)
            temppath = Path(temppath)

        if ctx.message.author == user or checks.mod_or_permissions(mute_members=True):
            if not temppath.is_file():
                self.bot.say("File does not exist! Make sure the file is in "
                             "the `data/greet/sounds` folder and you are "
                             "including the file extension.")
            else:
                if user is None:
                    self.settings[server.id][ctx.message.author.id][1] = str(path_or_url)
                else:
                    self.settings[server.id][user.id][1] = str(path_or_url)
                dataIO.save_json(self.file_path, self.settings)
                await self.bot.say("Set sound effect for " + user.name)

    # This is horrific, sorry
    @greetset.command(pass_context=True)
    async def toggle(self, ctx, mode: str, user: discord.Member = None):
        """Turns on/off sounds for a user or a server

        Modes:
        server:\ttoggle join sounds for the server on/off
        user:\ttoggle join sounds for a specific user"""
        server = ctx.message.server
        if user is not None:
            if str(user.id) not in self.settings[server.id]:
                self.settings[server.id][user.id] = [False, ""]
        else:
            user = ctx.message.author
            if str(user.id) not in self.settings[server.id]:
                self.settings[server.id][ctx.message.author.id] = [False, ""]
        if mode is None:
            return
        if mode == "server" and checks.mod_or_permissions(mute_members=True):
            try:
                self.settings[server.id]["ENABLED"] = not self.settings[server.id]["ENABLED"]
            except:
                self.settings[server.id]["ENABLED"] = True
            await self.bot.say("Toggled server-wide join sounds to {0}".format(self.settings[server.id]["ENABLED"]))
            dataIO.save_json(self.file_path, self.settings)
        if mode == "user":
            if user is None:
                await self.bot.say("Please specifiy a user.")
                return
            if ctx.message.author == user or checks.mod_or_permissions(mute_members=True):
                try:
                    self.settings[server.id][user.id][0] = not self.settings[server.id][user.id][0]
                except:
                    self.settings[server.id][user.id][0] = True
                await self.bot.say("Toggled sound for {0.name} to {1}.".format(user,
                                                                               self.settings[server.id][user.id][0]))
                dataIO.save_json(self.file_path, self.settings)

    async def on_voice_state_update(self, before, after):
        audio = self.bot.get_cog('Audio')
        # channel = after.voice_channel
        server = after.server
        if server.id not in self.settings.keys():
            return
        if not self.settings[server.id]["ENABLED"]:
            return
        if after.voice is None:
            return
        #if before.voice_channel == after.voice_channel:
        #    return
        if after.id == self.bot.user.id:
            return
        if str(server.id) not in self.settings.keys():
            return
        if not self.settings[server.id][after.id][0]:
            return
        if audio.is_playing(server):
            return
        #bot_channel = self.bot.voice_client_in(server)
        #if bot_channel != after.voice_channel:
        #    if bot_channel is not None:
        try:
            #    await audio._stop_and_disconnect(server)
            #    await self._join_voice_channel(channel)
            voice_client = await self._create_ffmpeg_player(server,
                                                            after.voice_channel,
                                                            str(self.settings[server.id][after.id][1]),
                                                            local=True)
            voice_client.audio_player.start()
        except Exception as e:
            print("Something went very wrong...\n{}".format(e))


def check_folders():
    if not os.path.exists("data/greet"):
        print("Creating data/greet folder...")
        os.makedirs("data/greet")

    if not os.path.exists("data/greet/sounds"):
        print("Creating data/greet/sounds folder...")
        os.makedirs("data/greet/sounds")


def check_files():
    f = "data/greet/settings.json"
    if not dataIO.is_valid_json(f):
        print("Creating welcome settings.json...")
        dataIO.save_json(f, {})


def check_avconv_ffmpeg():
    try:
        subprocess.call(["ffmpeg", "-version"], stdout=subprocess.DEVNULL)
    except FileNotFoundError:
        pass
    else:
        return "ffmpeg"

    try:
        subprocess.call(["avconv", "-version"], stdout=subprocess.DEVNULL)
    except FileNotFoundError:
        return False
    else:
        return "avconv"


def setup(bot):
    if youtube_dl is None:
        print("Sorry, you need youtube_dl to use the Greet cog")
        print("Please run 'pip3 install youtube_dl'")
    check_folders()
    check_files()
    n = Greet(bot, check_avconv_ffmpeg())
    bot.add_cog(n)
