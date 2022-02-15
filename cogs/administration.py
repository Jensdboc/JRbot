import discord
from discord.activity import Spotify
from discord.ext import commands

import urllib.request
from discord.ext.commands.core import command

from numpy.lib.type_check import imag

#****************************#
#User commands administration#
#****************************#

class Administration(commands.Cog):
    
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def nick(self, ctx, member : discord.Member,*, nickname):
        await member.edit(nick=nickname)  

    @commands.command()
    async def crew(self, context, member : discord.Member):
        for e in context.guild.roles:
            if e.name == '🌳':
                await member.add_roles(e)
                return 

    @commands.command()
    async def clear(self, ctx,*,number=1):
        messages = await ctx.channel.history(limit = number+1).flatten()
        for mes in messages:
            if (self.client.mute_message):
                if (self.client.mute_message.id == mes.id):
                    if (ctx.message.author.voice):
                        vc = ctx.message.author.voice.channel
                        for member in vc.members:
                            await member.edit(mute = 0)
                    self.client.mute_message = None
        await ctx.channel.delete_messages(messages)

    @commands.command(aliases = ['tm'])
    async def thumbmail(self, ctx, url):
        await ctx.send('https://i.ytimg.com/vi/' + str(url)[32:] + '/maxresdefault.jpg')
        await ctx.message.delete()

    @commands.command(aliases = ['sa'])
    async def show_activity(self, ctx, user=0):
        if user == 0:
            for member in ctx.guild.members:
                for activity in member.activities:
                    if isinstance(activity, Spotify) :
                        await ctx.send(member.name + ' is listening to ' + activity.title + ' from ' + activity.album + ' by ' + activity.artist)

    @commands.command(pass_context=True)
    async def join(self, ctx):
        channel = ctx.message.author.voice.channel
        await channel.connect()
    
    @commands.command(pass_context=True)
    async def leave(self, ctx):
        client = ctx.message.guild.voice_client
        await client.disconnect()                               

#Allows to connect cog to bot    
def setup(client):
    client.add_cog(Administration(client))