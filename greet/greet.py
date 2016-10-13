import discord
from discord.ext import commands
from .utils.dataIO import dataIO
from .utils import checks
from __main__ import send_cmd_help
import os
from pathlib import Path
import asyncio

class Greet:
    """Plays a sound effect when a user joins a channel"""

    def __init__(self, bot):
        self.bot = bot
        self.file_path = "data/greet/settings.json"
        self.settings = dataIO.load_json(self.file_path)

    def voice_client(self, server):
        return self.bot.voice_client_in(server)

    async def _join_voice_channel(self, channel):
        server = channel.server
        try:
            await self.bot.join_voice_channel(channel)
        except asyncio.futures.TimeoutError as e:
            print(e)
            raise ConnectTimeout("We timed out connecting to a voice channel")

    async def _create_ffmpeg_player(self, server, filename, local=False):
        """This function will guarantee we have a valid voice client,
            even if one doesn't exist previously."""
        voice_client = self.voice_client(server)
        voice_channel_id = voice_client.channel.id

        if voice_client is None:
            to_connect = self.bot.get_channel(voice_channel_id)
            if to_connect is None:
                pass
            await self._join_voice_channel(to_connect)  # SHIT
        elif voice_client.channel.id != voice_channel_id:
            print("reconnect chan id for sid {} is wrong, fixing".format(server.id))

        # Okay if we reach here we definitively have a working voice_client
        song_filename = os.path.join("data/greet/sounds", filename)

        use_avconv = False
        options = '-b:a 64k -bufsize 64k'

        try:
            voice_client.audio_player.process.kill()
            #print("killed old player")
        except AttributeError:
            pass
        except ProcessLookupError:
            pass

        voice_client.audio_player = voice_client.create_ffmpeg_player(song_filename, use_avconv=use_avconv, options=options)
        voice_client.audio_player.volume = 50
        return voice_client  # Just for ease of use, it's modified in-place


    @commands.group(pass_context=True, no_pm=True)
    async def greetset(self, ctx):
        """Sets welcome module settings"""
        if not ctx.message.author.bot:
            server = ctx.message.server
            if str(server.id) not in self.settings:
                self.settings[server.id] = {"ENABLED": False}
                dataIO.save_json(self.file_path, self.settings)
            if ctx.invoked_subcommand is None:
                await send_cmd_help(ctx)

    @greetset.command(pass_context=True)
    async def sound(self, ctx, path, user: discord.Member = None):
        """Set the sound file to play when a specific user joins a voice channel."""
        server = ctx.message.server
        if user is not None:
            if str(user.id) not in self.settings[server.id]:
                self.settings[server.id][user.id] = [False,""]
        else:
            user = ctx.message.author
            if str(user.id) not in self.settings[server.id]:
                self.settings[server.id][ctx.message.author.id] = [False,""]
        temppath = os.path.join("data/greet/sounds", path)
        temppath = Path(temppath)
        if ctx.message.author == user or checks.mod_or_permissions(mute_members=True):
            if not temppath.is_file():
                self.bot.say("File does not exist! Make sure the file is in the `data/greet/sounds` folder and you are including the file extension.")
            else:
                if user == None:
                    self.settings[server.id][ctx.message.author.id][1] = str(path)
                else:
                    self.settings[server.id][user.id][1] = str(path)
                dataIO.save_json(self.file_path, self.settings)
                await self.bot.say("Set sound effect for " + user.name)

    #This is horrific, sorry
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
        if mode == "server":
            if checks.mod_or_permissions(mute_members=True):
                try:
                    self.settings[server.id]["ENABLED"] = not self.settings[server.id]["ENABLED"]
                except:
                    self.settings[server.id]["ENABLED"] = True
                await self.bot.say("Toggled server-wide join sounds to {0}".format(self.settings[server.id]["ENABLED"]))
                dataIO.save_json(self.file_path, self.settings)
        if mode == "user":
            if user == None:
                await self.bot.say("Please specifiy a user.")
                return
            if ctx.message.author == user or checks.mod_or_permissions(mute_members=True):
                try:
                    self.settings[server.id][user.id][0] = not self.settings[server.id][user.id][0]
                except:
                    self.settings[server.id][user.id][0] = True
                await self.bot.say("Toggled sound for {0.name} to {1}.".format(user, self.settings[server.id][user.id][0]))
                dataIO.save_json(self.file_path, self.settings)

    async def user_join(self, before, after):
        audio = self.bot.get_cog('Audio')
        channel = after.voice_channel
        server = after.server
        bot_chan = self.bot.voice_client_in(server)
        if after is None:
            return
        if before.voice_channel == after.voice_channel:
            return

        if after.id == self.bot.user.id:
            return
        if str(server.id) not in self.settings:
            return
        if not self.settings[server.id]["ENABLED"]:
            return
        if not self.settings[server.id][after.id][0]:
            return
        if audio.is_playing(server):
            return
        try:
            #    await audio._stop_and_disconnect(server)
            #    await self._join_voice_channel(channel)
            voice_client = await self._create_ffmpeg_player(server, str(self.settings[server.id][after.id][1]), local=True)
            voice_client.audio_player.start()
        except:
            print("Something went very wrong...")


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

def setup(bot):
    check_folders()
    check_files()
    n = Greet(bot)
    bot.add_listener(n.user_join, "on_voice_state_update")
    bot.add_cog(n)
