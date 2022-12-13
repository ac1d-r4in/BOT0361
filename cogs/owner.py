from discord.ext import commands
from stuff.parsers import Parsers
from stuff.wipetools import WipeTools

class OwnerCommands(commands.Cog):
    def __init__(self, conf):
        self.confirm = conf
        self.reb = WipeTools.restart_bot
        self.wip = WipeTools.wipe

    @commands.command(name='reboot', aliases=['rb'])
    @commands.is_owner()
    async def reboot(self, ctx):
        if await self.confirm(ctx, "перезагрузить меня, Глеб") == True:
            self.reb()

    @commands.command(name='wipe')
    @commands.is_owner()
    async def wipe(self, ctx):
        if not self.wip():
            await ctx.send("Ошибка при очистке кэша!")