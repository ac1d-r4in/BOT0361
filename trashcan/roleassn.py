import discord

async def roleassn(message):
    author = message.author
    channel = message.channel
    print("file")
    team_list = ["водолаз", "шерсть", "петух", "мужик", "козел", "авторитет"]
    roles = [
        "200087445079851008",
        "200087567318646793",
        "200087733262090240",
    ]
    for r in author.roles:
        if r.id in roles:
            await channel.send("Ты уже прошел прописку, другалек. Если хочешь перепрописаться в хате, обратись к смотрящему.")
            return 1
    return 0
    
    
    
    #try:
        #await client.add_roles(message.author, role)
        #await client.send_message(message.channel, "Successfully added role {0}".format(role.name))
    #except discord.Forbidden:
        #await client.send_message(message.channel, "I don't have perms to add roles.")