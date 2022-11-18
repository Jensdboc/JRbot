from dis import disco
from inspect import signature
from io import StringIO
from typing import overload
import discord
from discord.ext import commands
import random
import re
from discord.utils import get
from discord import FFmpegPCMAudio
from youtube_dl import YoutubeDL

import typing
import asyncio

#*****************#     
#User commands fun#
#*****************# 

class Fun(commands.Cog):

    def __init__(self, client):
        self.client = client  
    
    autist_id = 383952659310444544
    @commands.command(usage="!mock <sentence>", 
                      description="Randomly capitalize the sentence", 
                      help="The sentence can contain **spaces**")
    async def mock(self, ctx, *, to_mock):
        mocked_text = ''
        if(ctx.message.author.id == 383952659310444544):
            c = 0
            for i in range(len(to_mock)):
                if (c%2):
                    mocked_text += to_mock[i].lower()
                else:
                    mocked_text += to_mock[i].upper()
                if(to_mock[i] != ' '):
                    c += 1
        else:
            for i in range(len(to_mock)):
                if (i%2):
                    mocked_text += to_mock[i].upper()
                else:
                    mocked_text += to_mock[i].lower()
        embed = discord.Embed(title=mocked_text,color=0xe67e22)
        await ctx.send(embed=embed)

    @commands.command(usage="!hotel", 
                      description="Trivago!", 
                      help="")
    async def hotel(self, ctx):
        embedVar = discord.Embed(title="Trivago!", color=0x992d22)
        await ctx.send(embed=embedVar)

    """
    @commands.command(usage="!moses", 
                      description="Moses I guess?", 
                      help="")
    async def moses(self, ctx):
        file = discord.File("./data_pictures/mosesgif.gif")
        embed = discord.Embed(color=0x9b59b6)
        embed.set_image(url="attachment://mosesgif.gif")
        await ctx.send(file=file, embed=embed) 
    """
    """
    # Werkt momenteel niet
    @commands.command(usage="!stemopsimon", 
                      description="Show true communism", 
                      help="Currently broken")
    async def stemopsimon(self, ctx):
        embed = discord.Embed(title='Sinds wanneer heeft een SSL stemmen nodig?', color=0xff0000) 
        link = 'https://www.biography.com/.image/ar_1:1%2Cc_fill%2Ccs_srgb%2Cg_face%2Cq_auto:good%2Cw_300/MTY2NjgyOTkyNTMyNTMwMjMx/gettyimages-2637237.jpg'
        embed.set_image(url=link)
        await ctx.send(embed=embed)
        channel = ctx.message.author.voice.channel
        await channel.connect()
        YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        voice = get(self.client.voice_clients, guild=ctx.guild)
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info('https://www.youtube.com/watch?v=AlJ8z86e8A8', download=False)
            URL = info['formats'][0]['url']
            voice.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
            voice.is_playing()
    """
    
    @commands.command(usage="!broederliefde", 
                      description=":)", 
                      help="")
    async def broederliefde(self, ctx):
        file = discord.File("./data_pictures/broederliefde.png")
        embed = discord.Embed(color=0x9b59b6)
        embed.set_image(url="attachment://broederliefde.png")
        await ctx.send(file=file, embed=embed)
  
    @commands.command(usage="!perfection", 
                      description=":^)", 
                      help="")
    async def perfection(self, ctx):
        file = discord.File("./data_pictures/floef.png")
        embed = discord.Embed(color=0x9b59b6)
        embed.set_image(url="attachment://floef.png")
        await ctx.send(file=file, embed=embed)  

    @commands.command(usage="!hug <member/role>", 
                      description="Give someone a hug!", 
                      help="!hug @member: Send a random hug to the member\n!hug @role: Send a random hug to everyone with this role")
    async def hug(self, ctx, target : typing.Union[discord.Member, discord.Role] = None):
        embed = discord.Embed(title='You get a free hug!', color=0x1DDCF)
        hugs = ["hug1.gif", "hug2.gif", "hug3.gif", "hug4.gif", "hug5.gif"]
        picture = random.choice(hugs)
        file = discord.File("./data_pictures/" + picture)
        embed.set_image(url="attachment://" + picture)
        if (target):
            if (isinstance(target, discord.Role)):
                list = target.members  
                for member in list:
                    await member.send(file=file, embed=embed)
            else:
                await target.send(file=file, embed=embed)
        else:
            await ctx.message.author.send(file=file, embed=embed)

    @commands.command(usage="!hug <member/role>", 
                      description="Changes nicknames over time in a voice channel", 
                      help="")
    async def time_nick(self, ctx):
        l = ['appelflap', 'piemelgefriemel','kaiser Hans', 'Wedidntstartthefire', 'Kaboom', 'Potverdikke', 'DA imposter', '☺', '\N{Cross Mark}', 'VOTE KICK NORICK', 'Emma', 'Floefie', 'Meesje', 'Processing...', 'Norick03', 'ComradBenji']
        vc = ctx.message.author.voice.channel
        for member in vc.members:
            nickname = random.choice(l)
            await member.edit(nick=str(nickname))
    
    @commands.command(usage="!answer <sentence>", 
                      description="Send a message to Britt for quizzes", 
                      help="Sentence can contain **spaces**",
                      aliases = ['a'])
    async def answer(self, ctx):
        for user in self.client.users:
            #Id van Britt
            if user == self.client.get_user(688070365448241247):
                name = str(ctx.author.name)
                answer = ''
                start = 0
                for letter in ctx.message.content:
                    if start > 0:
                        answer += str(letter)
                    if str(letter) == ' ':
                        start += 1
                embed = discord.Embed(title=name + ': ' + answer, color=0x7289da)            
                await user.send(embed=embed)

    @commands.command(usage="!secret <sentence>", 
                      description="Send a secret message", 
                      help="This message will be posted in the secretchannel with a randomised color :). Sentence can contain **spaces**")
    async def secret(self, ctx):
        channel = self.client.get_channel(935507669580652544)
        embed = discord.Embed(title=ctx.message.content[8:], color=discord.Color(random.randint(0, 16777215))) 
        await channel.send(embed=embed)

    @commands.command(usage="!pewpew <user>", 
                      description="Pewpew somebody ", 
                      help="This person won't be able to see the normal channels anymore because he/she is dead")
    async def pewpew(self, ctx, member : discord.Member):
        pewpew_role = ctx.guild.get_role(943050771228917812) # Boomhut
        # Check if person doesn't have pewpewrole
        if pewpew_role in ctx.author.roles:
            embed = discord.Embed(title="Whoops...", description="Dead people are not supposed to kill people.", color=0xDC143C) 
            await ctx.send(embed=embed)
            return
        # Decide if person is going to get shot
        chance = random.randint(0, 10)
        if chance < 8:
            await member.add_roles(pewpew_role)
            await ctx.send("Oh no, "+ member.name + " has been shot!")
            await asyncio.sleep(180) # Wait time
            await member.remove_roles(pewpew_role)
            await ctx.send(member.name + " has been revived!")
        elif chance < 10:
            await ctx.send("The shot missed "+ member.name + "!")
        elif chance == 10:
            await ctx.author.add_roles(pewpew_role)
            await ctx.send("Oh no, "+ ctx.author.name + " shot themself! Now laugh!")
            await asyncio.sleep(100) # Wait time
            await ctx.author.remove_roles(pewpew_role)
            await ctx.send(ctx.author.name + " has been revived!")

    @commands.Cog.listener("on_message")
    async def taylor(self, message):
        verboden_woorden = ['taylor swift','taylor', 'swift', 'taylorswift', 'folklore', 'love story', 'evermore', 'lovestory', 'taytay', 't swizzle', 'tswizzle', 'swizzle', 'queen t']
        aantal = 0
        for woord in verboden_woorden:
            if message.author.id == 249527744466124801 or message.author.id == 688070365448241247:
                if woord in message.content.lower() and message.author.id != 754020821378269324 and aantal == 0:
                    embed = discord.Embed(title='Toch weer nie over Taylor Swift bezig???', colour=0x000000) 
                    aantal += 1 
                    await message.channel.send(embed=embed)
            else:
                if woord in message.content.lower() and message.author.id != 754020821378269324 and message.author.id != 235088799074484224 and aantal == 0:
                    link2 = 'https://media.discordapp.net/attachments/764196816517464086/786677044335083570/dh5qukew5vv01.jpg?width=582&height=599'
                    embed = discord.Embed(title='Toch weer nie over Taylorreeksen bezig???', colour=0x000000) 
                    embed.set_image(url=link2)
                    aantal += 1
                    await message.channel.send(embed=embed)
    
    @commands.Cog.listener("on_message")
    async def loser(self, message):
        if message.author.id == 589027434611867668: # Pingo id
            pattern_match = re.compile(r"You need to wait (\d+ day(s)?, )?\d+ hour(s)? and \d+ minute(s)? before you can collect your next credits")
            present = pattern_match.match(message.content)
            emoji = "\U0001F1F1" # regional_indicator_l
            if present:
                await message.add_reaction(emoji)

#Allows to connect cog to bot   
def setup(client):
    client.add_cog(Fun(client))