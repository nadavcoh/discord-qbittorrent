# bot.py
import os
import platform
import logging

logging.basicConfig(level=logging.INFO)
# todo: get level from env

from qbittorrentapi import Client

from discord.ext import commands, tasks

from dotenv import load_dotenv

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
channel = int(os.getenv('DISCORD_CHAN'))
qbittorrent_host = os.getenv('QBITTORRENT_HOST')
qbittorrent_user = os.getenv('QBITTORRENT_USER')
qbittorrent_pass = os.getenv('QBITTORRENT_PASS')

possible_state = [ # Possible values of state:
    "error",	# Some error occurred, applies to paused torrents
    "missingFiles",	# Torrent data files is missing
"uploading",	# Torrent is being seeded and data is being transferred
"pausedUP",	# Torrent is paused and has finished downloading
"queuedUP",	# Queuing is enabled and torrent is queued for upload
"stalledUP",	# Torrent is being seeded, but no connection were made
"checkingUP",	# Torrent has finished downloading and is being checked
"forcedUP",	# Torrent is forced to uploading and ignore queue limit
"allocating",	# Torrent is allocating disk space for download
"downloading",	# Torrent is being downloaded and data is being transferred
"metaDL",	# Torrent has just started downloading and is fetching metadata
"pausedDL",	# Torrent is paused and has NOT finished downloading
"queuedDL",	# Queuing is enabled and torrent is queued for download
"stalledDL",	# Torrent is being downloaded, but no connection were made
"checkingDL",	# Same as checkingUP, but torrent has NOT finished downloading
"forceDL",	    # Torrent is forced to downloading to ignore queue limit
"checkingResumeData",	# Checking resume data on qBt startup
"moving",	# Torrent is moving to another location
"unknown"]	# Unknown status

excluded_state = ["queuedUP", "stalledUP", "uploading"] # exclude spamming updates about upload queue

uname = platform.uname()
running_on = f"{uname[0]} {uname[1]}"
print(f"Running on {running_on}")

client = Client(host=qbittorrent_host, username=qbittorrent_user, password=qbittorrent_pass)

print(f"Connected to qBittorrent Version: {client.app_version()} on {client.host}")
rid=0
bot = commands.Bot(command_prefix='!')

# to do: say goodbye on graceful shutdown
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
            if (not torrent in torrent_name_cache):
                # New torrent!
                message = (f"Hey, {response.torrents[torrent].name} was just added")
                # to do: check if a category is assigned, if not, ask to assign one
                print(message)
                await bot.get_channel(channel).send(message)
            if (hasattr (response.torrents[torrent],"name")):
                torrent_name_cache[torrent]=response.torrents[torrent].name
            if (hasattr (response.torrents[torrent],"state")):
                message = (f"{response.torrents[torrent].state} {torrent_name_cache[torrent]} {torrent}")
                print(message)
                if (response.torrents[torrent].state not in excluded_state): # send the message on discord only if not excluded
                    await bot.get_channel(channel).send(message)
            if ("progress" in response.torrents[torrent]):
                if (response.torrents[torrent].progress == 1):
                    # Torrent Complete!
                    message = (f"Hey, {torrent_name_cache[torrent]} has just completed downloading!")
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

