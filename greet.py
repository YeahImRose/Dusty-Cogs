import discord
from discord.ext import commands
from .utils.dataIO import fileIO
from .utils import checks
from __main__ import send_cmd_help
import os
from pathlib import Path
import asyncio

try:
    if not discord.opus.is_loaded():
        discord.opus.load_opus('libopus-0.dll')
except OSError:  # Incorrect bitness
    opus = False
except:  # Missing opus
    opus = None
else:
    opus = True

default_settings = {"ON": False}

class Greet:
    """Plays a sound effect when a user joins a channel"""

    def __init__(self, bot):
        self.bot = bot
        self.settings = fileIO("data/greet/settings.json", "load")

    def voice_client(self, server):
        return self.bot.voice_client_in(server)

    async def _join_voice_channel(self, channel):
        server = channel.server
        if True:
            njsfnskjdfnsjfnks = 1
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

        #print("making player on sid {}".format(server.id))

        voice_client.audio_player = voice_client.create_ffmpeg_player(song_filename, use_avconv=use_avconv, options=options)

        # Set initial volume
        vol = 50
        voice_client.audio_player.volume = vol

        return voice_client  # Just for ease of use, it's modified in-place


    @commands.group(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_server=True)
    async def greetset(self, ctx):
        """Sets welcome module settings"""
        server = ctx.message.server
        if server.id not in self.settings:
            self.settings[server.id] = default_settings
            fileIO("data/greet/settings.json","save",self.settings)
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @greetset.command(pass_context=True)
    async def sound(self, ctx, user: discord.Member, path):
        """Set the sound file to play when a specific user joins a voice channel."""
        server = ctx.message.server
        temppath = os.path.join("data/greet/sounds", path)
        temppath = Path(temppath)
        if not temppath.is_file():
            self.bot.say("File does not exist! Make sure the file is in the `data/greet/sounds` folder and you are including the file extension.")
        else:
            self.settings[server.id][user.id] = str(path)
            fileIO("data/greet/settings.json", "save", self.settings)
            await self.bot.say("Set sound effect for a user.")

    @greetset.command(pass_context=True)
    async def toggle(self, ctx):
        """Turns on/off sounds for a user or a server"""
        server = ctx.message.server
        self.settings[server.id]["ON"] = not self.settings[server.id]["ON"]
        if self.settings[server.id]["ON"]:
            await self.bot.say("I will now play channel join sounds.")
        else:
            await self.bot.say("I will no longer play channel join sounds.")
        fileIO("data/greet/settings.json", "save", self.settings)

    async def user_join(self, before, after):
        channel = after.voice_channel
        server = after.server
        if after is None:
            return
        if after.id == self.bot.user.id:
            return
        if server.id not in self.settings:
            pass
            self.settings[server.id] = default_settings
            fileIO("data/greet/settings.json","save",self.settings)
        if not self.settings[server.id]["ON"]:
            return
        if server == None:
            print("AAAAAAAAAAAAAAAAAAAAAAAAAAA! Something went wrong.")
            return
        if channel is None:
            print('Voice channel not found... somehow.')
            return

        voice_client = await self._create_ffmpeg_player(server, str(self.settings[server.id][after.id]), local=True)
        voice_client.audio_player.start()
        #except:
        #    print("Permissions Error. User that joined a voice channel: {0.name}".format(member))
        #    print("Bot doesn't have the proper permissions for {1.name} channel".format(channel))


    def speak_permissions(self, member):
        channel = self.member.voice.voice_channel
        if channel is None:
            return False
        return server.get_member(self.bot.user.id).permissions_in(channel).speak


def check_folders():
    if not os.path.exists("data/greet"):
        print("Creating data/greet folder...")
        os.makedirs("data/greet")

    if not os.path.exists("data/greet/sounds"):
        print("Creating data/greet/sounds folder...")
        os.makedirs("data/greet/sounds")

def check_files():
    f = "data/greet/settings.json"
    if not fileIO(f, "check"):
        print("Creating welcome settings.json...")
        fileIO(f, "save", {})

def setup(bot):
    check_folders()
    check_files()
    n = Greet(bot)
    bot.add_listener(n.user_join, "on_voice_state_update")
    bot.add_cog(n)
