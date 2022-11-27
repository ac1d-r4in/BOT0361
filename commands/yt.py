import discord
from discord.ext import commands
import asyncio
import itertools
import sys
import os
import traceback
from async_timeout import timeout
from random import shuffle
from functools import partial
import youtube_dl
from yt_dlp import YoutubeDL

youtube_dl.utils.bug_reports_message = lambda: ''

ytdlopts = {
    'username': 'gleksquadgvs@gmail.com',
    'password': 'ebalmamyalex2002sosite',
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': True,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # ipv6 addresses cause issues sometimes
}

ffmpegopts = {
    'before_options': '-nostdin',
    'options': '-vn'
}

ytdl = YoutubeDL(ytdlopts)

class Colors:
    yoba_custom = discord.Color.from_str("0x7badff")

class Embeds:
    im_not_in_vc = discord.Embed(title="", description="Я не подсоединен к голосовому каналу!", color=Colors.yoba_custom)

class VoiceConnectionError(commands.CommandError):
    """Custom Exception class for connection errors."""

class InvalidVoiceChannel(VoiceConnectionError):
    """Exception for cases of invalid Voice Channels."""

class DownloadError(commands.CommandInvokeError):
    """Exception for download errors."""


class YTDLSource(discord.PCMVolumeTransformer):

    def __init__(self, source, *, filename, data, requester):
        super().__init__(source)
        self.filename = filename
        self.requester = requester
        self.title = data.get('title')
        self.web_url = data.get('webpage_url')
        self.duration = data.get('duration')

        # YTDL info dicts (data) have other useful information you might want
        # https://github.com/rg3/youtube-dl/blob/master/README.md

    # def __getitem__(self, item: str):
    #     """Allows us to access attributes similar to a dict.
    #     This is only useful when you are NOT downloading.
    #     """
    #     return self.__getattribute__(item)

    embedtext = ""

    @classmethod
    async def create_source_part_I(cls, ctx, search: str, playlist=False, *, loop, download=True):
        loop = loop or asyncio.get_event_loop()
        try:
            to_run = partial(ytdl.extract_info, url=search, download=download)
            data = await loop.run_in_executor(None, to_run)
        except:
            ctx.send("Произошла ошибка при получении данных с сервера!")
        
        if 'entries' in data:
            if playlist:
                data = data['entries']
                sources = []
                for entry in data:
                    try:
                        sources.append(await cls.create_source_part_II(ctx, entry))
                    except:
                        continue
                while len(cls.embedtext) != 0:
                    text = cls.embedtext[0:4096]
                    cls.embedtext = cls.embedtext[4096:]
                    embed = discord.Embed(title="", description=text, color=Colors.yoba_custom)
                    await ctx.send(embed=embed)
                return sources
            else:
                data = data['entries'][0]
                source = await cls.create_source_part_II(ctx, data)
                embed = discord.Embed(title="", description=cls.embedtext[:-2], color=Colors.yoba_custom)
                await ctx.send(embed=embed)
                return source
        elif 'title' in data:
            source = await cls.create_source_part_II(ctx, data)
            embed = discord.Embed(title="", description=cls.embedtext[:-2], color=Colors.yoba_custom)
            await ctx.send(embed=embed)
            return source
        else:
            await ctx.send("Результатов по такому запросу не найдено!")

    @classmethod
    async def create_source_part_II(cls, ctx, data, download=True):
        cls.embedtext += f"Добавлен [{data['title']}]({data['webpage_url']}) [{ctx.author.mention}]\n\n"

        if download:
            source = ytdl.prepare_filename(data)
        else:
            return {'webpage_url': data['webpage_url'], 'requester': ctx.author, 'title': data['title']}

        return cls(discord.FFmpegPCMAudio(source), filename=source, data=data, requester=ctx.author)

    @classmethod
    async def regather_stream(cls, data, *, loop):
        """Used for preparing a stream, instead of downloading.
        Since Youtube Streaming links expire."""
        loop = loop or asyncio.get_event_loop()

        to_run = partial(ytdl.extract_info, url=data['webpage_url'], download=True)
        data = await loop.run_in_executor(None, to_run)

        return cls(discord.FFmpegPCMAudio(data['url']), data=data, requester=data['requester'])


class MusicPlayer:
    """A class which is assigned to each guild using the bot for Music.
    This class implements a queue and loop, which allows for different guilds to listen to different playlists
    simultaneously.
    When the bot disconnects from the Voice it's instance will be destroyed.
    """

    __slots__ = ('bot', '_guild', '_channel', '_cog', 'queue', 'next', 'current', 'np', 'volume', 'filename')

    def __init__(self, ctx):
        self.bot = ctx.bot
        self._guild = ctx.guild
        self._channel = ctx.channel
        self._cog = ctx.cog

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()

        self.np = None  # Now playing message
        self.volume = .5
        self.current = None
        self.filename = None

        ctx.bot.loop.create_task(self.player_loop())

    async def player_loop(self):
        """Our main player loop."""
        await self.bot.wait_until_ready()
        
        while not self.bot.is_closed():
            self.next.clear()
            try:
                # Wait for the next song. If we timeout cancel the player and disconnect...
                async with timeout(300):  # 5 minutes...
                    if self.filename:
                        try:
                            os.remove(self.filename)
                        except FileNotFoundError:
                            pass
                    source = await self.queue.get()
                    self.filename = source.filename
            except asyncio.TimeoutError:
                return self.destroy(self._guild)

            # if not isinstance(source, YTDLSource):
            #     # Source was probably a stream (not downloaded)
            #     # So we should regather to prevent stream expiration
            #     try:
            #         source = await YTDLSource.regather_stream(source, loop=self.bot.loop)
            #     except Exception as e:
            #         await self._channel.send(f'Не удалось добавить указанный трек :(.\n'
            #                                  f'```css\n[{e}]\n```')
            #         continue

            source.volume = self.volume
            self.current = source
            
            self._guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
            embed = discord.Embed(title="Сейчас играет", description=f"[{source.title}]({source.web_url}) [{source.requester.mention}]", color=Colors.yoba_custom)
            self.np = await self._channel.send(embed=embed)
            await self.next.wait()

            # Make sure the FFmpeg process is cleaned up.
            # source.cleanup()
            self.current = None

    def destroy(self, guild):
        """Disconnect and cleanup the player."""
        return self.bot.loop.create_task(self._cog.cleanup(guild))


class Music(commands.Cog):

    __slots__ = ('bot', 'players')

    def __init__(self, bot, confirm, check):
        self.bot = bot
        self.players = {}
        self.confirm = confirm
        self.check = check

    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass
        try:
            del self.players[guild.id]
        except KeyError:
            pass

    async def __local_check(self, ctx):
        """A local check which applies to all commands in this cog."""
        if not ctx.guild:
            raise commands.NoPrivateMessage
        return True

    async def __error(self, ctx, error):
        """A local error handler for all errors arising from commands in this cog."""
        if isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send('Эта команда не используется в личных сообщениях. :|')
            except discord.HTTPException:
                pass
        elif isinstance(error, InvalidVoiceChannel):
            await ctx.send('Ошибка подключения к голосовому каналу. '
                           'Убедись, пожалуйста, что ты в том канале, в который я могу зайти! :/')

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    def __getPlayer(self, ctx):
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = MusicPlayer(ctx)
            self.players[ctx.guild.id] = player

        return player

    @commands.command(name='join', aliases=['connect', 'j'], description="Присоединиться в голосовой канал, в котором находится пользователь")
    async def __connect(self, ctx, *, channel: discord.VoiceChannel=None):

        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                embed = discord.Embed(title="", description="Не вижу, куда нужно присоединиться. Вызови `join` из голосового канала.", color=Colors.yoba_custom)
                await ctx.send(embed=embed)
                raise InvalidVoiceChannel('Не вижу, куда нужно присоединиться. Уточни канал в команде или присоединись в нужный канал.')

        vc = ctx.voice_client

        if vc:
            if vc.channel.id == channel.id:
                return
            try:
                await vc.move_to(channel)
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'Не удалось переместиться в канал: <{channel}>. :(')
        else:
            try:
                await channel.connect()
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'Не удалось подключиться к каналу: <{channel}>. :(')
        await ctx.send(f'Успешно **присоединился** в канал `{channel}`. Приветик!')

    @commands.command(name='play', aliases=['p'], description="Запускает музыку")
    async def __play(self, ctx, *, search: str):

        await self.check(ctx)
        
        async with ctx.typing():
            vc = ctx.voice_client
            if not vc:
                await self.__connect(self, ctx)

            player = self.__getPlayer(ctx)
            # If download is False, source will be a dict which will be used later to regather the stream.
            # If download is True, source will be a discord.FFmpegPCMAudio with a VolumeTransformer.
            
            playlist = False
            if "youtube.com/playlist" in search:
                playlist = True
            
            source = await YTDLSource.create_source_part_I(ctx, search, playlist = playlist, loop=self.bot.loop, download=True)
            if isinstance(source, list):
                for s in source:
                    await player.queue.put(s)
            elif isinstance(source, YTDLSource):
                await player.queue.put(source)
            else:
                await ctx.send(f"Source is invalid: {source}")

    @commands.command(name='pause', aliases = ['II'], description="Поставить плеер на паузу")
    async def __pause(self, ctx):
        
        vc = ctx.voice_client

        if not vc or not vc.is_playing():
            embed = discord.Embed(title="", description="А я сейчас ничего и не играю!", color=Colors.yoba_custom)
            return await ctx.send(embed=embed)
        elif vc.is_paused():
            return

        vc.pause()
        await ctx.send("Paused ⏸️")

    @commands.command(name='resume', description="Возобновить")
    async def __resume(self, ctx):

        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = Embeds.im_not_in_vc
            return await ctx.send(embed=embed)
        elif not vc.is_paused():
            return

        vc.resume()
        await ctx.send("Resuming ⏯️")

    @commands.command(name='skip', aliases=['s'], description="Переключить трек")
    async def __skip(self, ctx):

        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = Embeds.im_not_in_vc
            return await ctx.send(embed=embed)

        if vc.is_paused():
            pass
        elif not vc.is_playing():
            return

        vc.stop()
        await ctx.send(f'**`{ctx.author}`**: Пропустил трек!')
    
    @commands.command(name='remove', aliases=['rm', 'rem'], description="Удаляет трек из очереди по указанной позиции")
    async def __remove(self, ctx, pos : int=None):

        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = Embeds.im_not_in_vc
            return await ctx.send(embed=embed)

        s = None
        player = self.__getPlayer(ctx)
        if pos == None:
            s = player.queue._queue.pop()
            embed = discord.Embed(title="", description=f"**Удалил** [{s.title}]({s.web_url}) [{s.requester.mention}]", color=Colors.yoba_custom)
        else:
            try:
                s = player.queue._queue[pos-1]
                del player.queue._queue[pos-1]
                embed = discord.Embed(title="", description=f"**Удалил** [{s.title}]({s.web_url}) [{s.requester.mention}]", color=Colors.yoba_custom)
            except:
                embed = discord.Embed(title="", description=f'Нет трека на позиции "{pos}" :/', color=Colors.yoba_custom)
        
        try:
            os.remove(s.filename)
        except FileNotFoundError:
            pass
        
        await ctx.send(embed=embed)
    
    @commands.command(name='clear', aliases=['clr'], description="Очищает очередь")
    async def __clear(self, ctx):

        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = Embeds.im_not_in_vc
            return await ctx.send(embed=embed)

        player = self.__getPlayer(ctx)
        
        for entry in player.queue._queue:
            try:
                os.remove(entry.filename)
            except FileNotFoundError:
                pass

        player.queue._queue.clear()
        await ctx.send('Очередь **очищена**!')

    @commands.command(name='queue', aliases=['q', 'playlist'], description="Показывает очередь")
    async def __queueInfo(self, ctx):

        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = Embeds.im_not_in_vc
            return await ctx.send(embed=embed)

        player = self.__getPlayer(ctx)
        if player.queue.empty():
            embed = discord.Embed(title="", description="Плейлист пуст", color=Colors.yoba_custom)
            return await ctx.send(embed=embed)
        
        upcoming = list(itertools.islice(player.queue._queue, 0, int(len(player.queue._queue))))

        qtext = f"NOW: {self.__nowPlaying(vc.source)}\n\n"
        qtext += '\n'.join(f"{upcoming.index(_) + 1}. [{_.title}]({_.web_url}) | `{self.__getDuration(_.duration)}` [{_.requester.mention}]" for _ in upcoming)
        while len(qtext) != 0:
            text = qtext[0:4096]
            qtext = qtext[4096:]
            embed = discord.Embed(title="", description=text, color=Colors.yoba_custom)
            await ctx.send(embed=embed)

    @commands.command(name='np', aliases=['nowplaying', 'current'], description="Показывает играющий сейчас трек")
    async def now_playing(self, ctx):
        
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = Embeds.im_not_in_vc
            return await ctx.send(embed=embed)

        player = self.__getPlayer(ctx)
        if not player.current:
            embed = discord.Embed(title="", description="А я сейчас ничего и не играю!", color=Colors.yoba_custom)
            return await ctx.send(embed=embed)

        embed = discord.Embed(title="Сейчас играет", description=self.__nowPlaying(vc.source), color=Colors.yoba_custom)
        await ctx.send(embed=embed)

    def __nowPlaying(self, source):
        duration = self.__getDuration(source.duration % (24 * 3600))
        
        return f"[{source.title}]({source.web_url}) [{source.requester.mention}] | `{duration}`"

    def __getDuration(self, seconds):
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        if hour > 0:
            duration = "%dh %02dm %02ds" % (hour, minutes, seconds)
        else:
            duration = "%02dm %02ds" % (minutes, seconds)
        
        return duration


    @commands.command(name='leave', aliases=["stop", "dc", "disconnect", "bye"], description="Выключить плеер и выйти из канала")
    async def __leave(self, ctx):
        
        vc = ctx.voice_client
        player = self.__getPlayer(ctx)
        
        if not vc or not vc.is_connected():
            embed = Embeds.im_not_in_vc
            return await ctx.send(embed=embed)
        
        try:
            os.remove(player.filename)
            for entry in player.queue._queue:
                os.remove(entry.filename)
        except:
            pass
        
        await ctx.send('Успешно **отсоединился**. Пока-пока!')

        await self.cleanup(ctx.guild)

    @commands.command(name='shuffle', aliases=["sh"], description="Перемешивает очередь в случайном порядке")
    async def __shuffle(self, ctx):

        vc = ctx.voice_client
        player = self.__getPlayer(ctx)

        if not vc or not vc.is_connected():
            embed = Embeds.im_not_in_vc
            return await ctx.send(embed=embed)

        if player.queue.empty():
            return await ctx.send("Плейлист пуст!")
        
        try:
            shuffle(player.queue._queue)
        except:
            return await ctx.send("Не удалось перемешать плейлист!")
        
        await ctx.send('Плейлист **перемешан** в случайном порядке!')