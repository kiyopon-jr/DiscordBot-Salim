import asyncio
import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv
import youtube_dl  # open source code Download Manager for video and audio content from YouTube

# Download the video what we are sending to a port. It will download it and then it will play.
load_dotenv()
DISCORD_TOKEN = os.getenv('TOKEN')

intents = discord.Intents().all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!', intents=intents)

# Загрузка аудио из видео файла

youtube_dl.utils.bug_reports_message = lambda: ''  # lambda функция

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


# Класс - внутри класса переменная URL будет принимать URL-адреса. По URL-адресу будет загружено видео,
# затем транслируется по порту как звук

class YTDLSource(discord.PCMVolumeTransformer):  # Преобразователь громкости
    def __init__(self, source, *, data, volume=0.5):  # ф-ия инициализации
        super().__init__(source, volume)  # Источник звука и громкость звука
        self.data = data
        self.title = data.get('title')
        self.url = ''

    # Создадим метод, который будет являться методом класса
    # cls цикл чтобы не производилось снова и снова.
    # И сначала загружает потом командами функции воспроизводит
    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url,
                                                                          download=not stream))  # Использование ф-ии для извлечения
        # информации с URL-адреса
        if 'entries' in data:  # Возьмем первый элемент из списка воспроизведения
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename()  # передали данные
        return filename  # вернем имя файла

    # Создан метод from_url, метод исходного класса, который принимает исходный в качестве параметра URL-адрес и
    # возвращает имя файла, загружаемого аудио файла

    # Команда !join, которая будет начинаться с ! - префикс команд
    # Метод боту, чтобы присоединиться к голосовому каналу

    @bot.command(name='join')
    async def join(ctx):
        if not ctx.message.author.voice:  # если нет автора в голосовом канале, то сообщение и возвращение
            await ctx.send(f"{ctx.message.author.name} is not connected to a voice channel")
            return
        else:  # иначе присоединиться к автору сообщения в голосовой чат
            channel = ctx.message.author.voice.channel
            await channel.connect()

    # Команда для воспроизведения песни
    @bot.command(name='play')
    async def play(ctx, url):
        server =
