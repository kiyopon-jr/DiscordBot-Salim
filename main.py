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