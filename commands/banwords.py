from discord.ext import commands

class BanWords(commands.Cog):
    def __init__(self, bot, confirm):
        self.bot = bot
        self.confirm = confirm

    @classmethod
    async def __addBanWord(cls, ctx, banword):
        server = ctx.guild
        banwords_file_dir = str(server.id) + '/banwords.txt'
        banword = banword.lower()

        with open(banwords_file_dir, "a") as f:
            f.write(banword + '\n')
        await ctx.channel.send("Слово " +  banword + " теперь запрещено на сервере!")

    @classmethod
    async def __removeBanWord(cls, ctx, banword):
        server = ctx.guild
        file_dir = str(server.id) + '/banwords.txt'

        with open(file_dir, "r") as f:
            lines = f.readlines()
        
        if (banword + '\n') not in lines:
            await ctx.channel.send("Слово \"" + banword + "\" не запрещено на сервере!")
        else:
            with open(file_dir, "w") as f:
                for line in lines:
                    if line.strip('\n') == banword:
                        pass
                    else:
                        f.write(line)
            await ctx.channel.send("Слово \"" + banword + "\" больше не запрещено на сервере!")

    @classmethod
    async def __showBanWords(cls, ctx):
        server = ctx.guild
        banwords_file_dir = str(server.id) + '/banwords.txt'

        with open(banwords_file_dir, "r") as f:
            bws = ""
            for line in f:
                bws += "\"" + line.strip('\n') + '\", '
            await ctx.channel.send("Запрещенные на сервере слова: " + bws[:-2] + ".")
    
    @classmethod
    def __freedomOfSpeech(cls, ctx):
        server = ctx.guild
        file_dir = str(server.id) + '/banwords.txt'
        f = open(file_dir, 'w')
        f.close()
    
    @commands.command(name='banword', help='Tells the bot to join the voice channel')
    @commands.has_guild_permissions(ban_members = True)
    async def banword(self, ctx, arg):
        await BanWords.__addBanWord(ctx, arg)

    @commands.command(name='unbanword', help='Tells the bot to join the voice channel')
    @commands.has_guild_permissions(ban_members = True)
    async def unbanword(self, ctx, arg):
        await BanWords.__removeBanWord(ctx, arg)

    @commands.command(name='unbanwords', help='Tells the bot to join the voice channel')
    @commands.has_guild_permissions(administrator = True)
    async def unbanwords(self, ctx):
        if await self.confirm(ctx, "очистить список запрещенных на сервере слов?") == True:
            BanWords.__freedomOfSpeech(ctx)
            await ctx.channel.send("Список запрещенных слов полностью очищен! Да здравствует свобода слова!")
    
    @commands.command(name='banwords', help='Tells the bot to join the voice channel')
    async def banwords(self, ctx):
        await BanWords.__showBanWords(ctx)