import discord


def crossroads(message, route):
    print()

async def l0(message):    
    #начало прописки
    emojis = ['✋', '😐', '😡']
    botMessage = await message.channel.send("Вы входите в камеру, и дверь позади вас закрывается...\nРазговоры в хате сразу затихают, и все внимание устремлено на вас.\n\n"
    +f"{emojis[0]} Поздороваться\n\n"
    +f"{emojis[1]} Молча смотреть в ответ\n\n"
    +f"{emojis[2]} Хуле вылупились, черти?\n")

    for emoji in emojis:
        await botMessage.add_reaction(emoji)