import asyncio, sys, os, shutil
from datetime import datetime, time, timedelta

class WipeTools:
    def __init__(self) -> None:
        pass

    WHEN = time(4, 0, 0)  # 6:00 PM
    TRIGGERED = False

    @classmethod
    async def overflowCheck(cls, ctx):
        if cls.TRIGGERED:
            return
        dir_path = 'downloads'
        counter = 0
        try:
            for file in os.listdir(dir_path):
                if os.path.isfile(os.path.join(dir_path, file)): 
                    counter += os.path.getsize(os.path.join(dir_path, file))
        except FileNotFoundError:
            pass
        if (counter > 1000000000):
            ctx.bot.loop.create_task(cls.background_task(ctx))
            await ctx.channel.send(f"Внимание! У меня скопилось много кэша и в {str(cls.WHEN)} UTC я приберусь у себя на сервере! "
            +"Бот перезапустится, играющие в этот момент плейлисты сбросятся! Простите за возможные неудобства!")
            TRIGGERED = True

    @classmethod
    def restart_bot(cls): 
        os.execv(sys.executable, ['python'] + sys.argv)

    @classmethod
    def wipe(cls):
        try:
            shutil.rmtree('downloads')
            cls.restart_bot()
        except Exception as e:
            if e == FileNotFoundError:
                pass
            else:
                print(e)
                return False
        return True

    @classmethod
    async def background_task(cls, ctx):
        now = datetime.utcnow()
        if now.time() > cls.WHEN:
            tomorrow = datetime.combine(now.date() + timedelta(days=1), time(0))
            seconds = (tomorrow - now).total_seconds() 
            await asyncio.sleep(seconds)
        while True:
            now = datetime.utcnow() 
            target_time = datetime.combine(now.date(), cls.WHEN)  # (In UTC)
            seconds_until_target = (target_time - now).total_seconds()
            await asyncio.sleep(seconds_until_target - 60)
            await ctx.channel.send("Через минуту я перезагружусь, чтобы почистить свои сервера! Не теряйте!")
            await asyncio.sleep(60)
            cls.__wipe()
            tomorrow = datetime.combine(now.date() + timedelta(days=1), time(0))
            seconds = (tomorrow - now).total_seconds()
            await asyncio.sleep(seconds)
