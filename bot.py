import os, discord
from discord.ext import commands
from pretty_help import PrettyHelp
from commands.parsers import Parsers
from dotenv import load_dotenv
from commands.yt import Music
from commands.roles import Roles
from commands.messages import ManageMessages
from commands.banwords import BanWords
from commands.bans import Bans
from commands.functions import __confirmation, __overflowCheck, __wipe, restart_bot, Colors

intents = discord.Intents.all()
intents.members = True

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
bot = commands.Bot(command_prefix="bot ", intents=intents)

async def addCogs():
    await bot.add_cog(Music(bot, __confirmation, __overflowCheck, Parsers.crossroad))
    await bot.add_cog(Roles(bot, __confirmation))
    await bot.add_cog(ManageMessages(bot, __confirmation))
    await bot.add_cog(BanWords(bot, __confirmation))
    await bot.add_cog(Bans(bot, __confirmation))

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    await addCogs()
    #bot.loop.create_task(background_task())

def banwordsdb(ctx):
    banwords_file_dir = str(ctx.guild.id) + '/banwords.txt'
    with open(banwords_file_dir, "r") as f:
        bws = []
        for line in f:
            bws.append(line.strip('\n'))
    return bws

@bot.event
async def on_reaction_add(reaction, user):
    message = reaction.message
    emoji = reaction.emoji
    ctx = await bot.get_context(message)

@bot.event
async def on_guild_join(guild):
    text_channels = guild.text_channels
    if text_channels:
        channel = text_channels[0]
    await channel.send('Привет, {}!'.format(guild.name))

    guild_dir = str(guild.id)
    if not os.path.exists(guild_dir):
        os.makedirs(guild_dir)
    
    guild_dir += "/music"
    if not os.path.exists(guild_dir):
        os.makedirs(guild_dir)

    file_dir = guild_dir + '/banwords.txt'
    guild_file = open(file_dir, 'w')
    guild_file.close()

    file_dir = guild_dir + '/graylist.txt'
    guild_file = open(file_dir, 'w')
    guild_file.close()

    file_dir = guild_dir + '/roles.txt'
    guild_file = open(file_dir, 'w')
    guild_file.close()

@bot.event
async def on_message(message):
    ctx = await bot.get_context(message)
    content = message.content.lower()
    if message.author == bot.user:
        return
    for banword in banwordsdb(ctx):
        if banword in content:
            await ctx.channel.send(ctx.author.mention + ", вы использовали запрещенное на сервере слово!")
            await Bans.__graylist(ctx, message.author, reason = "Запрещенное слово: " + message.content)
    if message.content.startswith("wipe"):
        await message.delete()
        if not __wipe():
            await ctx.send("Ошибка при очистке кэша!")
    await bot.process_commands(message)

@bot.command()
async def hello(ctx, *arg):
	await ctx.channel.send(ctx.author.mention + " Hello!")

@bot.command()
async def test(ctx, *args):
    arguments = ', '.join(args)
    await ctx.send(f'{len(args)} arguments: {arguments}')

@bot.command(name='reboot', aliases=['restart', 'rb'], description="Перемешивает очередь в случайном порядке")
@commands.has_guild_permissions(administrator = True)
async def reboot(ctx):
    restart_bot()

class MyHelp(commands.HelpCommand):

    help_embed=discord.Embed(title="Команды бота", description=(
        "Я много чего умею - играть музыку, модерировать каналы, даже банить пользователей!\n"
        "Узнать более подробную информацию о команде - `bot help команда`\n"
        "Некоторые команды требуют наличия прав модератора или администратора на сервере.\n"
        "\n"
        "Бот находится в состоянии **альфа-тестирования**, а если бы была буква перед **альфой**, то была бы она.\n"
        "По любым ошибкам в работе бота можно и нужно писать мне: **vaskebjorn#8805**\n"
        "\n\n"
        "**Музыка** - Команды для управления музыкальным плеером. Все команды требуют наличия роли `DJ`, которая выдается тому, кто вызвал плеер.\n"
        "`join`, `play`, `pause`, `resume`, `skip`, `skipto`, `nowplaying`, `queue`, `clear`, `shuffle`, `move`, `remove`\n"
        "\n"
        "**Команды** - набор разноцветных ролей, на которые смогут делиться участники сервера. Команды можно переименовать.\n"
        "`[MOD]create_teams`, `jointeam`\n"
        "\n"
        "**Предупреждения и баны** - давайте надеяться, что до такого не дойдет!\n"
        "`[MOD]graylist`, `[MOD]ungraylist`, `[MOD]ban`, `[ADM]mercy`, `[ADM]amnesty`\n"
        "\n"
        "**Модерация** - для ограничения свободы слова (или ее возвращения).\n"
        "`[MOD]banword`, `[MOD]unbanword`, `[ADM]liberty`, `banwords`\n"
        "\n"
        "**Очистка сообщений из канала** - только моих, или вообще всех.\n"
        "`[MOD]purge`, `[MOD]purge_all`"
    ), color=Colors.yoba_custom)

   # !help
    async def send_bot_help(self, mapping):
        await self.context.send(embed=self.help_embed)
       
   # !help <command>
    async def send_command_help(self, command):
        aliases = "`bot {}`, ".format(command.name)
        for a in command.aliases:
            aliases += "`bot {}`, ".format(a)
        aliases = aliases[:-2]
        description = f"{aliases}\n\n{command.help}"
        help_command_embed = discord.Embed(title=f"Команда {command.name}", description=description, color=Colors.yoba_custom)
        await self.context.send(embed=help_command_embed)

bot.help_command = MyHelp()

#YTКОМАНДЫ-----------------------------------------------------------------------------------------------------------------

bot.run(TOKEN)