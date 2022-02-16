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

    @commands.command(usage="!nick <member> <name>", 
                      description="Change nickname of member", 
                      help="!nick @member a very cool nickname\nName is allowed to contain **spaces**")
    async def nick(self, ctx, member : discord.Member,*, nickname):
        await member.edit(nick=nickname)  

    @commands.command(usage="!welcome <member>", 
                      description="Give member all required roles", 
                      help="Member will get 🌳-role, General Roles and Reward Roles")
    async def welcome(self, context, member : discord.Member):
        for e in context.guild.roles:
            if e.name == '🌳' or e.name == '------------[ General Roles  ]------------' or e.name == '------------[ Reward Roles ]------------':
                await member.add_roles(e)
        return

    @commands.command(usage="!clear <number>", 
                      description="Clear the last number of messages", 
                      help="The default value is 1 message")
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

    @commands.command(usage="!thumbmail <url>", 
                      description="Return the thumbmail from youtube", 
                      help="!thumbmail https://www.youtube.com/watch?v=dQw4w9WgXcQ 😏",
                      aliases = ['tm'])
    async def thumbmail(self, ctx, url):
        await ctx.send('https://i.ytimg.com/vi/' + str(url)[32:] + '/maxresdefault.jpg')
        await ctx.message.delete()

    @commands.command(usage="!show_activity <user>", 
                      description="Return the songs people in the server are listening to", 
                      help="Specifying a certain user doesn't work yet. Use !sa for now",
                      aliases = ['sa'])
    async def show_activity(self, ctx, user=0):
        if user == 0:
            for member in ctx.guild.members:
                for activity in member.activities:
                    if isinstance(activity, Spotify) :
                        await ctx.send(member.name + ' is listening to ' + activity.title + ' from ' + activity.album + ' by ' + activity.artist)

    @commands.command(usage="!join", 
                      description="Make the bot join a voice channel", 
                      help="The bot will and can only join the channel where you are currently in",
                      pass_context=True)
    async def join(self, ctx):
        channel = ctx.message.author.voice.channel
        await channel.connect()
    
    @commands.command(usage="!leave", 
                      description="Make the bot leave a voice channel", 
                      help="The bot will leave the channel even if you are not in the channel",
                      pass_context=True)
    async def leave(self, ctx):
        client = ctx.message.guild.voice_client
        await client.disconnect()                               

#Allows to connect cog to bot    
def setup(client):
    client.add_cog(Administration(client))