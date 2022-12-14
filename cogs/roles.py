import discord
from discord.ext import commands
from discord.utils import get

class Roles(commands.Cog):
    def __init__(self, bot, confirm):
        self.bot = bot
        self.confirm = confirm
    
    def __getdir(ctx):
        return 'servers/' + str(ctx.guild.id) + '/roles.txt'

    @classmethod
    def __roleFileCheck(cls, ctx):
        dir = cls.__getdir(ctx)
        with open(dir, "r") as f:
            ids = f.readlines()
        with open(dir, "w") as f:
            for id in ids:
                if ctx.guild.get_role(int(id.strip("\n"))) is not None:
                    f.write(id)
    
    @commands.command(name='create_teams', help=(
        "Создает набор разноцветных команд, или дополняет неполный набор. "
        "По команде `jointeam` участник сервера сможет присоединиться к одной из созданных таким образом команд. "
        "Команды при этом могут быть переименованы. Команда требует прав управления ролями на сервере."))
    @commands.has_guild_permissions(manage_roles = True)
    async def __createRoles(self, ctx):
        Roles.__roleFileCheck(ctx)
        server = ctx.guild
        role_file_dir = self.__getdir(ctx)

        team_list = ["Red", "Blue", "Green", "Yellow", "Black", "White"]
        new_teams = []
        try:
            rname = team_list[0]
            if get(server.roles, name = rname):
                pass
            else:
                newteam = await server.create_role(name=rname, color = discord.Colour(0xFF0000))
                new_teams.append(str(newteam.id))
            
            rname = team_list[1]
            if get(server.roles, name = rname):
                pass
            else:
                newteam = await server.create_role(name=rname, color = discord.Colour(0x0000FF))
                new_teams.append(str(newteam.id))
            
            rname = team_list[2]
            if get(server.roles, name = rname):
                pass
            else:
                newteam = await server.create_role(name=rname, color = discord.Colour(0x00FF00))
                new_teams.append(str(newteam.id))
            
            rname = team_list[3]
            if get(server.roles, name = rname):
                pass
            else:
                newteam = await server.create_role(name=rname, color = discord.Colour(0xFFFF00))
                new_teams.append(str(newteam.id))
            
            rname = team_list[4]
            if get(server.roles, name = rname):
                pass
            else:
                newteam = await server.create_role(name=rname, color = discord.Colour(0x080808))
                new_teams.append(str(newteam.id))
            
            rname = team_list[5]
            if get(server.roles, name = rname):
                pass
            else:
                newteam = await server.create_role(name=rname, color = discord.Colour(0xFFFFFF))
                new_teams.append(str(newteam.id))
            
            await ctx.channel.send("Создание новых команд...")
            with open(role_file_dir, 'a') as f:
                teams = ''
                for t_id in new_teams:
                    f.write(t_id + '\n')
                    teams += ctx.guild.get_role(int(t_id)).mention + ', '
            await ctx.channel.send(f"Созданы команды:  {teams[:-2]}")
            
        except discord.Forbidden:
            await ctx.channel.send("Я не имею права создавать роли.")

    @commands.command(name='jointeam', help=(
        "Присоединиться к одной из предложенных на сервере команд, "
        "если они были созданы модератором сервера при помощи команды `create_teams`. "
        "Если вы уже состоите в команде, чтобы сменить ее, попросите модератора удалить вашу имеющуюся. "
        "Чтобы увидеть список доступных на сервере команд, введите эту команду без аргумента - `bot jointeam`"
    ))
    async def __assignRole(self, ctx, entered_team):
        Roles.__roleFileCheck(ctx)
        role_file_dir = self.__getdir(ctx)
        role = discord.utils.get(ctx.guild.roles, name=entered_team)
        roleids = []
        with open(role_file_dir, "r") as file:
            for line in file:
                roleids.append(line[:-1])
        # roleids = roleids[1:]
        print(roleids)
        for r in ctx.message.author.roles:
            if str(r.id) in roleids:
                await ctx.channel.send("Вы уже состоите в команде. Если вы хотите сменить её, обратитесь к модератору!")
                return
        if role is None or str(role.id) not in roleids:
            av_roles = ''
            for r in roleids:
                av_roles += ctx.guild.get_role(int(r)).name + ', '
            await ctx.channel.send(f"Такой команды нет! Доступные команды: {av_roles[:-2]}")
            return
        elif entered_team in ctx.message.author.roles:
            await ctx.channel.send("Вы уже состоите в этой команде!")
        else:
            try:
                await ctx.message.author.add_roles(role)
                await ctx.channel.send(f"Добро пожаловать в команду {role.name}, {ctx.author.mention}")
            except discord.Forbidden:
                await ctx.channel.send("Я не имею права выдавать роли.")