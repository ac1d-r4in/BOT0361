import discord
from discord.ext import commands

class ManageMessages(commands.Cog):
    def __init__(self, bot, confirm):
        self.bot = bot
        self.confirm = confirm

    @classmethod
    async def __purge(cls, ctx, mode):
        def is_me(m):
            if mode == 0: return True
            if mode == 1: return m.author == ctx.bot.user
        try:
            deleted = await ctx.channel.purge(limit=100, check=is_me)
        except discord.Forbidden:
            await ctx.channel.send("Я не имею права удалять сообщения из этого канала.")
        return len(deleted)

    @commands.command(name='purge', help='Tells the bot to join the voice channel')
    @commands.has_guild_permissions(manage_messages = True)
    async def purge(self, ctx, *arg):
        if await self.confirm(ctx, f"удалить 100 последних моих сообщений из канала?") == True:
            d = await ManageMessages.__purge(ctx, 1)
            await ctx.channel.send(f'Удалено {d} моих сообщений из текущего канала.')

    @commands.command(name='purge_all', help='Tells the bot to join the voice channel')
    @commands.has_guild_permissions(manage_messages = True)
    async def purge_all(self, ctx, *arg):
        if await self.confirm(ctx, f"удалить 100 последних сообщений из канала?") == True:
            d = await ManageMessages.__purge(ctx, 0)
            await ctx.channel.send(f'Удалено {d} сообщений из текущего канала.')