import asyncio, sys, os, shutil
from datetime import datetime, time, timedelta

channel_id = 1 # Put your channel id here
WHEN = time(17, 15, 0)  # 6:00 PM
TRIGGERED = False

async def __overflowCheck(ctx):
    global TRIGGERED
    if TRIGGERED:
        return
    dir_path = 'downloads'
    counter = 0
    try:
        for file in os.listdir(dir_path):
            if os.path.isfile(os.path.join(dir_path, file)): 
                counter += os.path.getsize(os.path.join(dir_path, file))
    except FileNotFoundError:
        pass
    print(counter)
    if (counter > 1000000000):
        ctx.bot.loop.create_task(background_task(ctx))
        await ctx.channel.send(f"Внимание! У меня скопилось много кэша и в {str(WHEN)} UTC я приберусь у себя на сервере! "
        +"Бот перезапустится, играющие в этот момент плейлисты сбросятся! Простите за возможные неудобства!")
        TRIGGERED = True

def restart_bot(): 
    os.execv(sys.executable, ['python'] + sys.argv)

def __wipe():
    try:
        shutil.rmtree('downloads')
        restart_bot()
    except Exception as e:
        if e == FileNotFoundError:
            pass
        else:
            print(e)
            return False
    return True

async def background_task(ctx):
    now = datetime.utcnow()
    if now.time() > WHEN:
        tomorrow = datetime.combine(now.date() + timedelta(days=1), time(0))
        seconds = (tomorrow - now).total_seconds() 
        await asyncio.sleep(seconds)
    while True:
        now = datetime.utcnow() 
        target_time = datetime.combine(now.date(), WHEN)  # (In UTC)
        seconds_until_target = (target_time - now).total_seconds()
        await asyncio.sleep(seconds_until_target - 60)
        await ctx.channel.send("Через минуту я перезагружусь, чтобы почистить свои сервера! Не теряйте!")
        await asyncio.sleep(60)
        if __wipe():
            print("Wiped!")
        else:
            print("Not wiped!")
        tomorrow = datetime.combine(now.date() + timedelta(days=1), time(0))
        seconds = (tomorrow - now).total_seconds()
        await asyncio.sleep(seconds)

async def __confirmation(ctx, arg):
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
