import discord
from discord.ext import commands
import datetime

class Bans(commands.Cog):
    def __init__(self, bot, confirm):
        self.bot = bot
        self.confirm = confirm

    @classmethod
    async def __graylist(cls, ctx, intruder, reason: str = None):
        server = ctx.guild
        graylist_file_dir = str(server.id) + '/graylist.txt'
        warnings = await Bans.__userWarnings(ctx, intruder.name)

        with open(graylist_file_dir, "a") as f:
            f.write(intruder.name + "\n")
        
        if warnings == 0:
            await ctx.channel.send(intruder.mention + ", это ваше первое предупреждение!")
            await Bans.__timeout(ctx, intruder, minutes=5, reason = reason)
        elif warnings == 1:
            await ctx.channel.send(intruder.mention + ", это ваше второе и последнее предупреждение! Дальше - Б А Н.")
            await Bans.__timeout(ctx, intruder, days=1, reason = reason)
        else:
            await ctx.channel.send(intruder.mention + ", вы исчерпали лимит предупреждений и будете забанены.")
            await Bans.__ban(ctx, intruder, reason)

    @classmethod
    async def __timeout(cls, ctx, intruder, seconds: int = 0, minutes: int = 0, hours: int = 0, days: int = 0, reason: str = None):
        try:
            duration = datetime.timedelta(seconds=seconds, minutes=minutes, hours= hours, days=days)
            if reason == None: reason = "Причина не указана"
            await intruder.timeout(duration, reason = reason)
            await ctx.channel.send(intruder.mention + " предупрежден и приглушен на период " + str(duration))
        except discord.Forbidden:
            await ctx.channel.send("Я не имею права заглушать пользователей.")

    @classmethod
    async def __ban(cls, ctx, user, reason = None):
        try:
            await ctx.guild.ban(user, reason = reason)
            await Bans.__ungraylist(ctx, user.name)
            await ctx.channel.send("Пользователь " + user.name + " отправлен в бан.")
        except discord.Forbidden:
            await ctx.channel.send("Пользователю " + user.name + " сегодня везет - у меня нет прав забанить его.")

    @classmethod
    async def __userWarnings(cls, ctx, username):
        server = ctx.guild

        graylist_file_dir = str(server.id) + '/graylist.txt'
        with open(graylist_file_dir, "r") as f:
            c = 0
            for line in f:
                if line.strip('\n') == username:
                    c += 1
        return c

    @classmethod
    async def __ungraylist(cls, ctx, username):
        server = ctx.guild
        file_dir = str(server.id) + '/graylist.txt'

        with open(file_dir, "r") as f:
            lines = f.readlines()
        
        if (username + '\n') not in lines:
            await ctx.channel.send("У пользователя " + username + " нет предупреждений!")
        else:
            with open(file_dir, "w") as f:
                for line in lines:
                    if line.strip('\n') == username:
                        pass
                    else:
                        f.write(line)
            await ctx.channel.send("С пользователя " + username + " сняты все предупреждения!")

    @classmethod
    async def __amnesty(cls, ctx, full):
        server = ctx.guild
        file_dir = str(server.id) + '/graylist.txt'
        f = open(file_dir, 'w')
        f.close()
        await ctx.channel.send("Список предупреждений полностью очищен!")
        if (full == 1):
            try:
                async for entry in server.bans():
                    await server.unban(entry.user)
                await ctx.channel.send("Все забаненные пользователи разблокированы! Да здравствует милосердный администратор!")
            except discord.Forbidden:
                await ctx.channel.send("Я не имею права разбанивать пользователей.")

    @commands.command(name='graylist', help='Выписывает пользователю предупреждение. 1е предупреждение - таймаут 5 мин, 2е предупреждение - таймаут 1 день, 3е - бан.')
    @commands.has_guild_permissions(ban_members = True)
    async def graylist(self, ctx, *args):
        user = ctx.message.mentions[0]
        try:
            reason = args[1]
        except IndexError:
            reason = None
        if await self.confirm(ctx, f"выписать предупреждение пользователю {user.mention}?") == True:
            await Bans.__graylist(ctx, user, reason = reason)

    @commands.command(name='ungraylist', help='Снимает с пользователя все предупреждения')
    @commands.has_guild_permissions(ban_members = True)
    async def ungraylist(self, ctx):
        user = ctx.message.mentions[0]
        await Bans.__ungraylist(ctx, user.name)

    @commands.command(name='ban', help='Забанить пользователя')
    @commands.has_guild_permissions(ban_members = True)
    async def ban(self, ctx, *arg):
        user = ctx.message.mentions[0]
        if await self.confirm(ctx, f"забанить пользователя {user.mention}?") == True:
            await Bans.__ban(ctx, user, arg)
    
    @commands.command(name='mercy', help='Снять предупреждение со всех пользователей')
    @commands.has_guild_permissions(administrator = True)
    async def amnesty(self, ctx):
        if await self.confirm(ctx, "снять предупреждение со всех пользователей") == True:
            await Bans.__amnesty(ctx, 0)

    @commands.command(name='amnesty', help='Снять все предупреждения и разбанить всех забаненных')
    @commands.has_guild_permissions(administrator = True)
    async def full_amnesty(self, ctx):
        if await self.confirm(ctx, "снять предупреждение со всех пользователей и разбанить всех забаненных") == True:
            await Bans.__amnesty(ctx, 1)

    @commands.command(name='warnings', help='Узнать количество выписанных пользователю предупреждений')
    async def warnings(self, ctx):
        warnings = await Bans.__userWarnings(ctx, ctx.author.name)
        await ctx.channel.send(ctx.author.mention + f", у вас {warnings} предупреждений.")