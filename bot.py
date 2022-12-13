import os, discord, asyncio
from discord.ext import commands
from dotenv import load_dotenv
from cogs.yt import Music
from cogs.roles import Roles
from cogs.messages import ManageMessages
from cogs.banwords import BanWords
from cogs.bans import Bans
from cogs.owner import OwnerCommands
from stuff.assets import Colors, Embeds

intents = discord.Intents.all()
intents.members = True

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
bot = commands.Bot(command_prefix="bot ", intents=intents)

async def confirmation(ctx, arg):
    emojis = ['✅']
    botMessage = await ctx.channel.send(f"Вы уверены, что хотите {arg}?")
    for emoji in emojis:
        await botMessage.add_reaction(emoji)

    def checktrue(reaction, user):
        return user == ctx.author and str(reaction.emoji) == '✅'
    try:
        await ctx.bot.wait_for('reaction_add', timeout=10.0, check=checktrue)
    except asyncio.TimeoutError:
        await botMessage.delete()
        return False
    else:
        await botMessage.delete()
        return True

async def addCogs():
    await bot.add_cog(Music(bot, confirmation))
    await bot.add_cog(Roles(bot, confirmation))
    await bot.add_cog(ManageMessages(bot, confirmation))
    await bot.add_cog(BanWords(bot, confirmation))
    await bot.add_cog(Bans(bot, confirmation))
    await bot.add_cog(OwnerCommands(confirmation))

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    await addCogs()
    #bot.loop.create_task(background_task())

def banwordsdb(ctx):
    banwords_file_dir = 'servers/' + (str(ctx.guild.id)) + '/banwords.txt'
    with open(banwords_file_dir, "r") as f:
        bws = []
        for line in f:
            bws.append(line.strip('\n'))
    return bws

@bot.event
async def on_guild_join(guild):
    text_channels = guild.text_channels
    if text_channels:
        channel = text_channels[0]
    await channel.send('Привет, {}!'.format(guild.name))

    guild_dir = 'servers/'.join(str(guild.id))
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
    
    await bot.process_commands(message)

@bot.command()
async def hello(ctx, *arg):
	await ctx.channel.send(ctx.author.mention + " Hello!")

class MyHelp(commands.HelpCommand):

   # bot help
    async def send_bot_help(self, mapping):
        await self.context.send(embed=Embeds.help_embed)
       
   # bot help <command>
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