import discord
from discord.ext import commands
# from easy_pil import Editor, Canvas

# from keep_alive import keep_alive

import os
# TOKEN = os.environ['TOKEN']
TOKEN = "OTA3OTEzMDE2MjE2MDEwNzcy.YYuF4w.DwnyASEQ1tC7yl3k3P_8LhoXUc8"

# import music
import music

# cogs = [music]
cogs = [music]

activity = discord.Game(name="Girls und Panzer: Dream Tank Match!")
client = commands.Bot(command_prefix=".",activity=activity, intents = discord.Intents.all(), status=discord.Status.online)
client.remove_command('help')

# @client.event
# async def on_member_join(member):
#   # guild = client.get_guild(912796646092447774) [tabs]
#   # channel = guild.get_channel(913415785794387969) [tabs]
#   guild = client.get_guild(907913296135467008)
#   channel = guild.get_channel(915505531509153822)
#   await channel.send()

@client.event
async def on_ready():
  print ("We have logged in as {0.user}".format(client))

for i in range(len(cogs)):
  cogs[i].setup(client)

# keep_alive()
client.run(TOKEN)
