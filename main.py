import asyncio
import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv
import yt_dlp as youtube_dl  # open source code Download Manager for video and audio content from YouTube

# Download the video what we are sending to a bot. It will download it and then it will play.
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
# затем транслируется ботом как звук

class YTDLSource(discord.PCMVolumeTransformer):  # Преобразователь громкости
    def __init__(self, source, *, data, volume=0.5):  # ф-ия инициализации
        super().__init__(source, volume)  # Источник звука и громкость звука
        self.data = data
        self.title = data.get('title')
        self.url = ""

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
        filename = data['title'] if stream else ytdl.prepare_filename(data)  # передали данные
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

    # Команда для воспроизведения песни !play


@bot.command(name='play')
async def play(ctx, url):
    server = ctx.message.guild  # чтобы получить объект сообщения
    voice_channel = server.voice_client  # присоединиться к голосовому каналу откуда был получен объект сообщения
    async with ctx.typing():
        filename = await YTDLSource.from_url(url, loop=bot.loop)  # передадим в ф-ию from_url URL-адрес
        voice_channel.play(discord.FFmpegPCMAudio(
            executable="C:\\Users\\user\\PycharmProjects\\DiscordBot-Salim\\ffmpeg.exe",
            source=filename))
    await ctx.send(f'**Now Playing:** {filename}')

    # Команда для паузы !pause


@bot.command(name='pause')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client  # уже в голосовом чате
    if voice_client.is_playing():
        await voice_client.pause()
    else:
        await ctx.send("The bot has pauses the music")


# Команда для возобновления !resume
@bot.command(name='resume')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client  # уже в голосовом чате
    if voice_client.is_paused():
        await voice_client.resume()
    else:
        await ctx.send("The bot isn't playing song")


# Команда покинуть !leave
@bot.command(name='leave')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client  # уже в голосовом чате
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("The bot not in channel")


# Команда остановить !stop
@bot.command(name="stop")
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.stop()
    else:
        await ctx.send("The bot isn't playing anything")


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
