import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import yt_dlp as youtube_dl

# set up the Discord bot client
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# Discord bot token
load_dotenv()
token = os.getenv("TOKEN")

song_queue = []

@bot.event
async def on_ready():
    print(f"\033[1;36;40m{bot.user} has connected to Discord!\n")

@bot.command()
async def play(ctx, url):
    channel = ctx.author.voice.channel
    voice_client = ctx.voice_client

    if voice_client and voice_client.is_connected():
        if voice_client.channel != channel:
            await voice_client.move_to(channel)
    else:
        voice_client = await channel.connect()

    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        audio_url = info_dict['url']
        title = info_dict.get('title', 'Unknown Title')

    song_queue.append((audio_url, title))

    if len(song_queue) == 1:
        voice_client.play(discord.FFmpegPCMAudio(song_queue[0][0], before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", executable="C:\\ffmpeg\\bin\\ffmpeg.exe"), after=lambda e: play_next(ctx))

async def play_next(ctx):
    global song_queue

    if len(song_queue) > 0:
        song_queue.pop(0)
        if len(song_queue) > 0:
            voice_client = ctx.voice_client
            voice_client.play(discord.FFmpegPCMAudio(song_queue[0][0], before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", executable="C:\\ffmpeg\\bin\\ffmpeg.exe"))
    else:
        await ctx.send("There are no more songs in the queue.")
        
@bot.command()
async def skip(ctx):
    if len(song_queue) > 0:
        ctx.voice_client.stop()
        # Remove the first item from the queue and play the next one if available
        song_queue.pop(0)
        if len(song_queue) > 0:
            voice_client = ctx.voice_client
            voice_client.play(discord.FFmpegPCMAudio(song_queue[0][0], before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", executable="C:\\ffmpeg\\bin\\ffmpeg.exe"))
    else:
        await ctx.send("There are no more songs in the queue.")

@bot.command()
async def queue(ctx):
    if len(song_queue) == 0:
        await ctx.send("The queue is empty.")
    else:
        queue_message = "**Queue:**\n"
        for index, (_, title) in enumerate(song_queue):
            queue_message += f"{index + 1}. {title}\n"

        await ctx.send(queue_message)

@bot.command()
async def stop(ctx):
    voice_client = ctx.voice_client
    if voice_client.is_playing():
        voice_client.stop()

@bot.command()
async def disconnect(ctx):
    voice_client = ctx.voice_client
    await voice_client.disconnect()

def run_discord_bot():
    print("\033[1;36;40mConnecting to Discord...\n")
    bot.run(token, reconnect=True)