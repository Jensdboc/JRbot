import discord
from discord.ext import commands

import urllib.request

#****************************#
#User commands administration#
#****************************#

class Administration(commands.Cog):
    
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def nick(ctx, member : discord.Member,*, nickname):
        await member.edit(nick=nickname)  

    @commands.command()
    async def crew(context, member : discord.Member):
        for e in context.guild.roles:
            if e.name == '🌳':
                await member.add_roles(e)
                return 

    @commands.command()
    async def clear(self, ctx,*,number=1):
        messages = await ctx.channel.history(limit = number+1).flatten()
        for mes in messages:
            if(self.client.mute_message):
                if (self.client.mute_message.id == mes.id):
                    if (ctx.message.author.voice):
                        vc = ctx.message.author.voice.channel
                        for member in vc.members:
                            await member.edit(mute = 0)
                    self.client.mute_message = None
        await ctx.channel.delete_messages(messages)

    @commands.command(aliases = ['tm'])
    async def thumbmail(ctx, url):
        urllib.request.urlretrieve(url, filename = 'secret.html')
        with open('secret.html', 'r', encoding = 'utf-8') as infile:
                start = '<meta property="og:image"'
                k = 0
                jpg = ''
                for line in infile:
                    if start in str(line):
                        for i in range(len(line)):
                            if line[i] == 'o' and line[i+1] == 'g' and line[i+2] == ':' and line[i+3] == 'i' and line[i+4] == 'm' and line[i+5] == 'a' and k == 0:
                                k = i
                                start = i + 18
                        for i in range(k, len(line)):      
                            if line[i] == 'j' and line[i+1] == 'p' and line[i+2] == 'g' and k != 0:
                                jpg += 'jpg'
                                await ctx.send(jpg)
                                await ctx.message.delete()
                                return 
                            if i > start:
                                jpg += line[i]   

    @commands.command(pass_context=True)
    async def join(ctx):
        channel = ctx.message.author.voice.channel
        await channel.connect()
    
    @commands.command(pass_context=True)
    async def leave(ctx):
        client = ctx.message.guild.voice_client
        await client.disconnect()
                                
    @commands.command()
    async def commands(ctx):
        embed = discord.Embed(title='List of commands', color=0x7289da)
        embed.add_field(name='!Unmute [!um]', value='Unmutes the voicechat' )
        embed.add_field(name='!Mute [!m]', value='Mutes the voicechat' )
        embed.add_field(name='!clear <#>', value='Clears the last number of messages (standard = 1)' )
        embed.add_field(name='!code <*\*\*\*\*\*-**>  [!cd]', value='Formats 6-digit code, NA/EU is optional' )
        embed.add_field(name='!code', value='Resends current code, click on the emoji to mute, unmute or to remove the message' )
        embed.add_field(name='!hotel', value='Just try it!' )
        embed.add_field(name='!crew <@person>', value='Gives someone the crew-role' )
        embed.add_field(name='!broederliefde', value=':)' )
        embed.add_field(name='!stemopsimon', value='**ussr intensifies**' )
        embed.add_field(name='!mock <...>', value='Mock inserted text' )
        embed.add_field(name='!commands', value='Shows this message' )
        embed.add_field(name='!python', value='Alstublieft Benjamin' )
        embed.add_field(name='!nick <@person> <nick>', value='Changes the nickname of a certain person' )
        embed.add_field(name='!thumbmail <url> [!tm]', value='Provide a youtube link and recieve the thumbmail' )
        embed.add_field(name='!hug', value='Feeling lonely?' )
        embed.add_field(name='!switch', value='Starts a among-us switch game, click on the spoiler under your name' )
        embed.add_field(name='!perfection', value='Perfection!' )
        await ctx.send(embed=embed) 

#Allows to connect cog to bot    
def setup(client):
    client.add_cog(Administration(client))