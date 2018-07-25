from discord.ext import commands
from __main__ import send_cmd_help
import aiohttp
import io
import os
try:
    from PIL import Image
except:
    raise RuntimeError("You don't have pillow installed. run 'pip3 install pillow' and try again")


class Moji:
    def __init__(self, bot):
        self.bot = bot
        self.size = 128, 128
        self.bot.loop.create_task(self.init_task())

    def update_folders(self):
        for x in self.bot.servers:
            if os.path.exists("data/moji/" + x.name):
                os.rename("data/moji/" + x.name,
                          "data/moji/" + x.id)

    async def init_task(self):
        await self.bot.wait_until_ready()
        self.update_folders()

    @commands.command(pass_context=True, no_pm=True)
    async def emoji(self, ctx, name: str):
        """Send a large custom emoji.

        Bot must be in the server with the emoji"""
        for x in list(self.bot.get_all_emojis()):
            if x.name.lower() == name.lower():
                fdir = "data/moji/" + x.server.id
                fp = fdir + "/{0.name}.png".format(x)
                if not os.path.exists(fdir):
                    os.mkdir(fdir)
                if not os.path.isfile(fp):
                    async with aiohttp.get(x.url) as r:
                        img_bytes = await r.read()
                        img = io.BytesIO(img_bytes)
                        with open(fp, 'wb') as o:
                            o.write(img.read())
                        o.close()

                im = Image.open(fp)
                im.thumbnail(self.size, Image.ANTIALIAS)
                im.save(fp, "PNG")

                # You can uncomment this line if you want c:
                # await self.bot.delete_message(ctx.message)
                return await self.bot.send_file(ctx.message.channel, fp)

    @commands.group(pass_context=True, no_pm=True)
    async def moji(self, ctx):
        """Various emoji operations"""
        if ctx.invoked_subcommand is None:
            return await send_cmd_help(ctx)

    @moji.command(pass_context=True, no_pm=True)
    async def list(self, ctx, server: int = None):
        """List all available custom emoji"""
        server = server
        servers = list(self.bot.servers)
        if server is None:
            msg = "``` Available servers:"
            for x in servers:
                msg += "\n\t" + str(servers.index(x)) + ("- {0.name}".format(x))
            await self.bot.say(msg + "```")
        else:
            msg = "```Emojis for {0.name}".format(servers[server])
            for x in list(servers[server].emojis):
                msg += "\n\t" + str(x.name)
            await self.bot.say(msg + "```")


def check_folders():
    if not os.path.exists("data/moji"):
        print("Creating data/moji folder...")
        os.makedirs("data/moji")


def setup(bot):
    check_folders()
    bot.add_cog(Moji(bot))
