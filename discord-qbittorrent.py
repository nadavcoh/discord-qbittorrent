# bot.py
# https://realpython.com/how-to-make-a-discord-bot-python/
import os
import platform

from qbittorrentapi import Client

uname = platform.uname()
running_on = f"{uname[0]} {uname[1]}"
print(f"Running on {running_on}")

client = Client(host='', username='', password='')

print(f"Connected to qBittorrent Version: {client.app_version()} on {client.host}")

from discord.ext import commands, tasks

from dotenv import load_dotenv

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
channel = int(os.getenv('DISCORD_CHAN'))

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(
        f'{bot.user} is connected to the following guilds:\n'
    )
    for guild in bot.guilds:
        print(
            f'{guild.name} (id: {guild.id})\n'
        )
        members = '\n - '.join([member.name for member in guild.members])
        print(f'Guild Members:\n - {members}')
#        for channel in guild.text_channels:
#            await channel.send(f'{bot.user} is connected')
        await bot.get_channel(channel).send(f"Hi! I'm running on {running_on} and connected to qBittorrent on {client.host}")

@bot.command(name='machine', help='a')
async def machine(ctx):
    print(f'{ctx.message.author.name} called {ctx.message.content}')
    response = running_on
    await ctx.send(response)

@bot.command(name='torrents', help='a')
async def torrents(ctx):
    print(f'{ctx.message.author.name} called {ctx.message.content}')
    response = platform.uname()
    await ctx.send(response)

@tasks.loop(seconds=5.0)
async def looper():
    global rid
#    print(looper.current_loop)
#    print(rid)
    response = client.sync.maindata(rid)
    rid = response.rid
    if(hasattr(response,"torrents")):
        for torrent in response.torrents:
            if (hasattr (response.torrents[torrent],"name")):
                torrent_name_cache[torrent]=response.torrents[torrent].name
            if (hasattr (response.torrents[torrent],"state")):
                message = (f"{response.torrents[torrent].state} {torrent_name_cache[torrent]} {torrent}")
                print(message)
                await bot.get_channel(channel).send(message)
    if(hasattr(response,"torrents_removed")):
        for torrent in response.torrents_removed:
            message = (f"Removed {torrent_name_cache[torrent]} {torrent}")
            print(message)
            await bot.get_channel(channel).send(message)

#    print(response)


response = client.sync.maindata(0)
torrent_name_cache={}
if(hasattr(response,"torrents")):
    for torrent in response.torrents:
        torrent_name_cache[torrent]=response.torrents[torrent].name

rid = response.rid
looper.start()

bot.run(token)

