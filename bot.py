import discord
from discord.utils import get
from discord.ext import commands
from discord.ext.commands import Bot
import random
import youtube_dl
import os
import pyowm
from discord.ext.commands.errors import *


list_landscape = ['a.jpg', 'b.jpg', 's.jpg', '2.jpg', '3.jpg', '4.jpg', '5.jpg', '6.jpg']
list_cat = ['c.jpg', 'm.jpg', 'z.jpg', 'n.jpg', 'v.jpg', 'q.jpg', 'w.jpg', 'e.jpg', 'r.jpg', 't.jpg', 'y.jpg',]
list_dog = ['dog1.jpg', 'dog2.jpg', 'dog3.jpg', 'dog4.jpg','dog5.jpg', 'dog6.jpg']

Bot = commands.Bot(command_prefix = '-')

Bot.remove_command('help')

@Bot.event
async def on_ready():
    print('+')


@Bot.command()
async def join(ctx):
    global voice
    channel = ctx.message.author.voice.channel
    voice = get(Bot.voice_clients, guild = ctx.guild)

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
        await ctx.send(f'bot connected to voice channel {channel}')


@Bot.command()
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(Bot.voice_clients, guild = ctx.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
    else:
        voice = await channel.connect()
        await ctx.send(f'bot disconnected to voice channel {channel}')


@Bot.command()
async def play(ctx, url : str):
    song_there = os.path.exists('song.mp3')

    try:
        if song_there:
            os.remove('song.mp3')
            print('[log] Старый файл удален')
    except PermissionError:
        print('[log] не удалось удалить файл')

    await ctx.send('Ожидание...')

    voice = get(Bot.voice_clients, guild = ctx.guild)

    ydl_opts = {
        'format' : 'bestaudio/best',
        'postprocessors' : [{
            'key' : 'FFmpegExtractAudio',
            'preferredcodec' : 'mp3',
            'preferredquality' : '192'
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print('[log] Загружаю МУЗОН...')
        ydl.download([url])

        for file in os.listdir('./'):
            if file.endswith('.mp3'):
                name = file
                print(f'[log] Переименовываю файл: {file}')
                os.rename(file, 'song.mp3')

        voice.play(discord.FFmpegPCMAudio('song.mp3'), after = lambda e: print(f'[log] {name}, Музыка закончила своё прогирование'))
        voice.source = discord.PCMVolumeTransformer(voice.source)
        voice.source.volume = 0.6

        song_name = name.rsplit('-', 2)
        await ctx.send(f'проигрывание {song_name[1]}')


@Bot.command()
async def stop(ctx):
    voice = get(Bot.voice_clients, guild = ctx.guild)
    voice.stop()


@Bot.command()
async def pause(ctx):
    voice = get(Bot.voice_clients, guild = ctx.guild)
    voice.pause()


@Bot.command()
async def resume(ctx):
    voice = get(Bot.voice_clients, guild = ctx.guild)
    voice.resume()


@Bot.command()
async def help(ctx):
    await ctx.send('''Что я умею делать
#Комманды для картинок
```1)landscape - выдает рандомный пейзаж
2)cat - высылает рандомного котика ^-^
3)dog - высылает рандомную собачку ^-^
4)stonks - Ну тупо стонкс
5)nostonks - Ну тупо не стонкс```
#Комманды для музыки
```1)join - добавляет бота в войс чат в котором вы сидите
2)leave - удаляет бота из войс чата в котором вы сидите
3)play (Ссылка url на видео в youtube) - проигрывает песню (бот должен быть в войсе и после команды надо вставить ссылку на видео на ютубе)
4)stop - останавливает музыку 
5)pause - ставит на паузу музыку
6)resume - возобновляет воспроизведение музыки```
#Бесполезные, но интересные комманды
```1)dyrka - вызывает дурку
2)whydimaisgay - говорит почему же дима гей
3)sanyasotky - САНЯ ЭТО УЖЕ НЕ СМЕШНО
4)weather (Город/Страна) - выясняет погоду в каком то городе
5)donate - Поддержка разрабов```''')


@Bot.command()
async def landscape(ctx):
    await ctx.send(file = discord.File(fp = list_landscape[random.randint(0, 2)]))

@Bot.command()
async def cat(ctx):
    await ctx.send(file = discord.File(fp = 'cats/' + list_cat[random.randint(0, 10)]))


@Bot.command()
async def dyrka(ctx):
    await ctx.send(file = discord.File(fp = 'Dyrka.png'))


@Bot.command()
async def whydimaisgay(ctx):
    await ctx.send('''Потому что так надо''')


@Bot.command()
async def stonks(ctx):
    await ctx.send(file = discord.File(fp = 'stonks.jpg'))


@Bot.command()
async def nostonks(ctx):
    await ctx.send(file = discord.File(fp = 'notstonks.jpg'))


@Bot.command()
async def dog(ctx):
    await ctx.send(file = discord.File(fp = 'dogs/' + list_dog[random.randint(0, 5)]))


@Bot.command()
async def sanyasotky(ctx):
    await ctx.send('''САНЯ СОТКУ ВЕРНИ!!!''')


@Bot.command()
async def weather(ctx, place : str):
    owm = pyowm.OWMowm = pyowm.OWM('63f515875baf3226d7689dc6ae18d157', language = 'ru')
    observation = owm.weather_at_place(place)
    w = observation.get_weather()
    temp = w.get_temperature('celsius')['temp']
    await ctx.send('В городе ' + place + ' сейчас ' + str(temp) + ' по цельсию ' + str(w.get_detailed_status()))


@Bot.command()
async def donate(ctx):
    await ctx.send('Хочешь поддержать разрабов? https://www.donationalerts.com/r/kirill0712')


#errors
@weather.error
async def weather_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'{ctx.author.mention}, Пример: -weather Москва')


@play.error
async def play_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'{ctx.author.mention}, Шаблон: play url_adress')


token = os.environ.get('BOT_TOKEN')

Bot.run(token)