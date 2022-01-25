import discord
from discord.ext import commands
import youtube_dl

import traceback
# import yt_dlp as youtube_dl

import urllib.parse, urllib.request
import re, sys, os

import datetime

import asyncio

FFMPEG_OPTIONS = {"before_options":"-reconnect 1 -reconnect_streamed 1  -reconnect_delay_max 5", "options":"-vn"}
YDL_OPTIONS = {"format":"bestaudio"}

queue_list = {}
player_info = {}
loop_index = {}
looping = {}
url_queue = {}
playlist = {}
embed_url = {}
fix = 0

def youtube_search(search):
  query_string = urllib.parse.urlencode({
    'search_query': search
  })

  html_content = urllib.request.urlopen(
    "https://www.youtube.com/results?" + query_string
  )

  search_results = re.findall(r"watch\?v=(\S{11})", html_content.read().decode())

  vid_id = search_results[0]
  vid_url = 'https://www.youtube.com/watch?v=' + vid_id

  return vid_url


def embed_build(info, url):
  try:
   duration = str(datetime.timedelta(seconds=int(info["duration"])))
  except:
    pass
  vid_title = info["title"]
  vid_img = info["thumbnail"]
  channel = info["channel"]
  upload = str(info["upload_date"])

  year = upload[: 4]
  month = upload[4 : 6: 1]
  day = upload[6: 8: 1]
  upload = day + "-" + month + "-" + year

  embed = discord.Embed(title=vid_title, url=url, color=discord.Color.red())
  try:
    embed.add_field(name="duration", value=duration, inline=True)
  except:
    pass
  embed.add_field(name="creator", value=channel, inline=True)
  embed.add_field(name="uploaded", value=upload, inline=True)
  embed.set_image(url=vid_img)

  return embed

class music(commands.Cog):
  def __init__(self, client):
    self.client = client

  async def index_play(ctx, guild, vc):
    while True:
      index = loop_index[guild]
      if index == len(url_queue[guild]) - 1:
        loop_index[guild] = 0
      else:
        loop_index[guild] = index + 1
      
      if url_queue[guild][index] == "dummy-url2":
        loop_index[guild] = index + 1

      index = loop_index[guild]
      url2 = url_queue[guild][index]
      source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
      ctx.voice_client.stop()
      vc.play(source)
      await asyncio.sleep(1)
      if ctx.voice_client.is_playing():
        pass
      else:
        loop_index[guild] = index - 1

      while ctx.voice_client.is_playing():
        await asyncio.sleep(1)
        while ctx.voice_client.is_paused():
          await asyncio.sleep(1)
      if looping[guild] == False:
        break

  async def que_check(vc, guild, ctx):
    try:
      while True:
        if url_queue[guild] != []:
          loop_index[guild] = 0

          url2 = url_queue[guild].pop(0)
          if url2 == "dummy-url2":
            url2 = url_queue[guild].pop(0)
          source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
          player_info[guild].pop(0)
          queue_list[guild].pop(0)
          embed_url[guild].pop(0)
        ctx.voice_client.pause()
        vc.play(source)
        while ctx.voice_client.is_playing():
          await asyncio.sleep(1)
          while ctx.voice_client.is_paused():
            await asyncio.sleep(1)
        if len(url_queue[guild]) == 0:
          break
    except Exception as e:
      print(str(e))
      await ctx.send(str(e))
      pass
    

  @commands.command(name="join", aliases=['j', 'summon'])
  async def join(self, ctx):
    if ctx.author.voice is None:
      await ctx.send("You are not in a voice channel")
    else:
      voice_channel = ctx.author.voice.channel
      connection = ctx.guild.voice_client 
      if ctx.voice_client is None:
        await voice_channel.connect()
      else:
        await connection.move_to(voice_channel)

  @commands.command(name="leave", aliases=['l', 'go'])
  async def leave(self, ctx):
    guild = ctx.voice_client
    try:
      if url_queue[guild] != []:
        url_queue[guild].clear()
        player_info[guild].clear()
        queue_list[guild].clear()
        loop_index[guild].clear()

      await ctx.voice_client.disconnect()
    except:
      await ctx.voice_client.disconnect()
  
  @commands.command(name="clear", aliases=['c'])
  async def clear(self, ctx):
    guild = ctx.voice_client
    ctx.voice_client.pause()
    try:
      if guild in url_queue:
        if url_queue[guild] != []:
          url_queue[guild].clear()
          player_info[guild].clear()
          queue_list[guild].clear()

        else:
          return
    except:
      pass

  @commands.command(name="play")
  async def play(self, ctx, *, url=None):
    guild = ctx.voice_client
    search = False
    yt_playlist = False
    vc = ctx.voice_client

    if vc == None:
      await ctx.send("Katyusha needs to join you before Katyusha can play")
      return
    else:
      pass
    
    if url == None:
      if guild in url_queue:
        try:
          if url_queue[guild] != []:
            await music.que_check(vc, guild, ctx)
        except:
          pass
      else:
        await ctx.send("Katyusha needs a url, playlist or some keywords")
        return
    else:
      if url == "for pravda!":
        url = "https://www.youtube.com/watch?v=C5Az984gVdU"
        embed = discord.Embed(title="", color=discord.Color.red())
        embed.set_image(url="https://i.pinimg.com/originals/30/fa/3d/30fa3dd4addd1556c4872f49506038ce.jpg")
        await ctx.send(embed = embed)
      if url.__contains__("https://www.youtube.com/watch?v=") or url.__contains__("https://youtu.be/"):
        pass
      elif url.__contains__("https://youtube.com/playlist") or url.__contains__("https://www.youtube.com/playlist"):
        await ctx.send("Katyusha needs some time to process that, please wait")
        yt_playlist = True
      else:
        url = youtube_search(url)
        search = True
      if ctx.voice_client is None:
        await ctx.send("If Katyusha wants to play, Katyusha will first have to join")
      else:
        
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
          try:
            info = ydl.extract_info(url, download=False)
          except:
            tr = traceback.format_exc()
            await ctx.send("Katyusha liep ergens tegen aan:/n" + str(tr))

          if yt_playlist == True:
            index = 0
            while len(info["entries"]) != index:
              url2 = info["entries"][index]["url"]
              url = "https://www.youtube.com/watch?v=" + info["entries"][index]["id"]
              embed = embed_build(info["entries"][index], url)
              if guild in url_queue:
                player_info[guild].append(embed)
                queue_list[guild].append(info["entries"][index]["title"])
                url_queue[guild].append(url2)
                embed_url[guild].append(url)
              else:
                queue_list[guild] = ["dummy-title"]
                queue_list[guild].append(info["entries"][index]["title"])
                player_info[guild] = ["dummy-url"]
                player_info[guild].append(embed)
                url_queue[guild] = ["dummy-url2"]
                url_queue[guild].append(url2)
                embed_url[guild] = [url]
              index = index + 1
            await ctx.send("Katyusha has finished processing it")
            await music.play(self, ctx)
          else:
            embed = embed_build(info, url)
            if search == True:
              await ctx.send(embed=embed)
            else:
                pass
            url2 = info["formats"][1]["url"]

            url_queue[guild] = ["dummy-url2"]
            url_queue[guild].append(url2)
            player_info[guild] = ["dummy-url"]
            player_info[guild].append(embed)
            queue_list[guild] = ["dummy-title"]
            queue_list[guild].append(info["title"])
            embed_url[guild] = [url]

            await music.play(self, ctx)

  @commands.command(name="delete", aliases=['del', 'remove'])
  async def remove(self, ctx, *, index=None):
    guild = ctx.voice_client
    try:
      if index == None:
        return
      else:
        try:
          index = int(index)
        except:
          index = 0
      if index == 0 or index == None:
        return
      else:
        index = index - 1
      if guild in looping:
        if looping[guild] == True:
          if queue_list[guild][index] == "dummy-title":
            removed = queue_list[guild].pop(index + 1)
            url_queue[guild].pop(index)
            player_info.pop(index + 1)
          else:
            removed = queue_list[guild].pop(index)
            url_queue[guild].pop(index)
            player_info.pop(index)
          await ctx.send("Katyusha removed {} from the queue".format(removed))
          return
        else:
          pass
      elif guild in queue_list:
        removed = queue_list[guild].pop(index)
        url_queue[guild].pop(index)
        player_info[guild].pop(index)
        await ctx.send("Katyusha removed {} from the queue".format(removed))
    except:
      pass

  @commands.command(name="pause", aliases=['p', 'break'])
  async def pause(self, ctx):
    try:
      ctx.voice_client.pause()
      await ctx.send("Paused")
    except:
      pass

  @commands.command(name="resume", aliases=['r', 'continue'])
  async def resume(self, ctx):
    try:
      ctx.voice_client.resume()
      await ctx.send("Resumed")
    except:
      pass

  @commands.command(name="skip", aliases=['s'])
  async def skip(self, ctx):
    guild = ctx.voice_client
    ctx.voice_client.pause()
    try:
      if guild in looping:
        if looping[guild] == True:
          await music.play(self, ctx)
        else:
          await music.play(self, ctx)
      else:
        await music.play(self, ctx)
    except:
      pass


  @commands.command(name="now", aliases=['current', 'currently', 'np'])
  async def current(self, ctx, index=None):
    guild = ctx.voice_client
    if guild in looping:
      if looping[guild] == True:
        if index == None:
          index = loop_index[guild] + 1
          if player_info[guild][index] == "dummy-url":
            embed = player_info[guild][index + 1]
          else:
            embed = player_info[guild][index]
          await ctx.send(embed=embed)
          return
        else:
          index = int(index)
          if player_info[guild][index] == "dummy-url":
            index + 1
            embed = player_info[guild][index]
          else:
            embed = player_info[guild][index]
          await ctx.send(embed=embed)
          return
      else:
        pass
    else:
      pass
    if index == None:
      if player_info[guild][0] == "dummy-url":
        embed = player_info[guild][1]
      else:
        embed = player_info[guild][0]
      await ctx.send(embed=embed)
    else:
      index = int(index) - 1
      if player_info[guild][index] == "dummy-url":
        index + 1
        embed = player_info[guild][index]
      else:
        embed = player_info[guild][index]
      await ctx.send(embed=embed)
  
  @commands.command(name="list", aliases=['queued'])
  async def list(self, ctx, index=None):
    guild = ctx.voice_client
    try:
      if guild in queue_list:
        add = ""
        now_playing = ""
        items = len(queue_list[guild])
        playing = True
        index = 1
        limit = 5
        for x in queue_list[guild]:
          # count = 0
          if x == "dummy-title":
            continue
          elif playing == True:
            now_playing = str(index) + ". " + x
            playing = False
            index = index + 1
          elif limit != 0:
            add = add + str(index) + ". " + x + "\n"
            index = index + 1
            limit = limit - 1
          elif index == items:
            add = add + "•••\n" + str(index) + ". " + x + "\n"
          else:
            index = index + 1

        embed = discord.Embed(title="now playing:", description = now_playing, color=discord.Color.red())
        if add != "":
          embed.add_field(name = "queued:", value = str(add), inline = False)
          await ctx.send(embed=embed)
        elif add == "":
          await ctx.send(embed=embed)
        return
      elif looping[guild] == True:
        add = ""
        playing = loop_index[guild]
        items = len(queue_list[guild])
        start = False
        index = 1
        now_playing = ""
        limit = 4
        for x in queue_list[guild]:
          if x == "dummy-title":
            continue
          elif playing == index - 1:
            now_playing = str(index) + ". " + x
          if index == 1:
            add = add + str(index) + ". " + x + "\n"
            index = index + 1
          elif limit != 0:
            if playing == index - 3:
              start = True
            else:
              index = index + 1
          if start == True:
            if limit == 4:
              add = add + "•••\n" + str(index) + ". " + x + "\n"
              limit = limit - 1
              index = index + 1
            else:
              add = add + str(index) + ". " + x + "\n"
              limit = limit - 1
              index = index + 1
            if limit == 0:
              start = False
          if index == items:
            add = add + "•••\n" + str(index) + ". " + x + "\n"

        embed = discord.Embed(title="now playing:", description = now_playing, color=discord.Color.red())
        try:
          embed.add_field(name = "queued:", value = add, inline = False)
          await ctx.send(embed=embed)
        except:
          await ctx.send(embed=embed)
        return
      else:
        await ctx.send("'.list' is unavailable")
    except Exception as e:
      print (str(e))
      pass

  @commands.command()
  async def loop(self, ctx, url=None):
    guild = ctx.voice_client
    vc = guild
    if guild in url_queue:
      pass
    else:
      return
    loop_index[guild] = len(url_queue[guild]) - 1
    if guild in url_queue:
      looping[guild] = True
      await music.index_play(ctx, guild, vc)
    else:
      return
    
  @commands.command(name="stop", aliases=['unloop'])
  async def stop(self, ctx):
    guild = ctx.voice_client
    if guild in looping:
      if looping[guild] == True:
        looping[guild] = False
        loop_index[guild] = 0
      else:
        return
    else:
      return

  @commands.command(name="add", aliases=['a', 'q', 'queue'])
  async def add(self, ctx, *, url=None):
    guild = ctx.voice_client
    search = False
    yt_playlist = False
    vc = ctx.voice_client
    global fix

    if vc == None:
      await ctx.send("Katyusha needs to join you before Katyusha can play")
      return
    else:
      pass

    if url == None:
      await ctx.send("Katyusha needs a url or some keywords")
      return
    else:
      if url == "for pravda!":
        url = "https://www.youtube.com/watch?v=C5Az984gVdU"
        embed = discord.Embed(title="", color=discord.Color.red())
        embed.set_image(url="https://i.pinimg.com/originals/30/fa/3d/30fa3dd4addd1556c4872f49506038ce.jpg")
        await ctx.send(embed = embed)
      if url.__contains__("https://www.youtube.com/watch?v=") or url.__contains__("https://youtu.be/"):
        pass
      elif url.__contains__("https://youtube.com/playlist"):
        await ctx.send("Katyusha needs some time to add this to the queue")
        yt_playlist = True
      else:
        url = youtube_search(url)
        search = True
      if ctx.voice_client is None:
        await ctx.send("If Katyusha wants to play, Katyusha will first have to join")
      else:
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
          try:
            info = ydl.extract_info(url, download=False)
          except:
            tr = traceback.format_exc()
            await ctx.send("Katyusha liep ergens tegen aan:/n" + str(tr))

          if yt_playlist == True:
            index = 0
            while len(info["entries"]) != index:
              url2 = info["entries"][index]["url"]
              url = "https://www.youtube.com/watch?v=" + info["entries"][index]["id"]
              embed = embed_build(info["entries"][index], url)
              if guild in url_queue:
                player_info[guild].append(embed)
                queue_list[guild].append(info["entries"][index]["title"])
                url_queue[guild].append(url2)
                embed_url[guild].append(url)
              else:
                queue_list[guild] = ["dummy-title"]
                queue_list[guild].append(info["entries"][index]["title"])
                player_info[guild] = ["dummy-url"]
                player_info[guild].append(embed)
                url_queue[guild] = ["dummy-url2"]
                url_queue[guild].append(url2)
                embed_url[guild] = [url]
              index = index + 1
            await ctx.send("Katyusha has finished adding the playlist to the queue")
          else:
            embed = embed_build(info, url)
            if search == True:
              await ctx.send(embed=embed)
            elif fix >= 1:
              fix = fix - 1
            else:
              await ctx.send("Katyusha added that one to the queue")
            url2 = info["formats"][1]["url"]

            if guild in url_queue:
              player_info[guild].append(embed)
              queue_list[guild].append(info["title"])
              url_queue[guild].append(url2)
              embed_url[guild].append(url)
            else:
              queue_list[guild] = ["dummy-title"]
              queue_list[guild].append(info["title"])
              player_info[guild] = ["dummy-url"]
              player_info[guild].append(embed)
              url_queue[guild] = ["dummy-url2"]
              url_queue[guild].append(url2)
              embed_url[guild] = [url]


  @commands.command()
  async def help(self, ctx):
    embed = discord.Embed(colour = discord.Color.orange())
    embed.set_author(name = "Bot commands:")
    embed.add_field(name = ".join", value = "de bot zal je joinen in je voice kanaal", inline = False)
    embed.add_field(name = ".leave", value = "de bot zal je voice kanaal verlaten", inline = False)
    embed.add_field(name = ".play", value = "nadat je .play hebt ingevoert heb je de optie om een youtube url mee te geven maar je kan ook keywords meegeven en dan zal de bot de eerste url op de youtube resultaten pagina afspelen\nDeze command maakt ook een queue aan, de queue kan je updaten met de volgende command", inline = False)
    embed.add_field(name = ".add", value = "met dit command voeg je nummers toe aan de queue, dit kan ook weer om achter de '.add' een youtube url te zetten, maar ook hier kun je gewoon keywords meegeven en het zal dan op de zelfde manier werken als '.play'\nals je een nummer aan de queue toevoegt ,zonder dat je eerst de '.play' command hebt gebruikt, dan zal je daarna '.play' moeten gebruiken om de queue te starten", inline = False)
    embed.add_field(name = ".pause", value = "met dit command word de de muziek, die momenteel wordt afgespeelt, stop gezet", inline = False)
    embed.add_field(name = ".resume", value = "met deze command wordt de muziek weer verder afgespeelt. deze command werkt niet als de muziek niet op pauze staat", inline = False)
    embed.add_field(name = ".skip", value = "dit zal de muziek die momenteel wordt afgespeelt overslaan en de volgende in de queue afspelen\n(als er geen queue is dan zal het opeens heel stil worden)", inline = False)
    embed.add_field(name = ".now", value = "dit zal informatie geven over de muziek die momenteel wordt afgespeelt, maar als je een nummer meegeeft van '.list' dan word de infromatie van die index gegeven", inline = False)
    embed.add_field(name = ".loop", value = "dit zal de aangemaakte queue of het nummer dat momenteel word gespeeld loopen, !als er al een nummer word afgespeeld en de loop command word gegeven dan zal het nummer dat momenteel wordt afgespeelt opnieuw worden afgespeelt", inline = False)
    embed.add_field(name = ".current", value = "dit zal informatie geven over de muziek die momenteel wordt afgespeelt, maar als je een nummer meegeeft van '.list' dan word de infromatie van die index gegeven", inline = False)

    await ctx.reply(embed=embed, mention_author=True)


def setup(client):
    try:
        client.add_cog(music(client))
    except:
        python = sys.executable
        os.execl(python, python, * sys.argv)
