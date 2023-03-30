import discord
from discord.ext import commands
import random

lobbycode = None
dead = []


class Amongus(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(usage="!code <code>",
                      description="Start among us game in mutechannel",
                      help="The code has to be a valid 6-digit number. The following message will be posted in mutechannel",
                      aliases=['cd'])
    async def code(self, ctx, *, new_lobbycode=''):
        global lobbycode
        await ctx.message.delete()
        if len(new_lobbycode) == 0:
            if (lobbycode is not None):
                embed1 = discord.Embed(title=lobbycode, color=0x2ecc71)
            else:
                embed1 = discord.Embed(title='No code yet', color=0xff0000)
            await ctx.channel.send(embed=embed1)
        elif len(new_lobbycode) == 9 or len(new_lobbycode) == 6:
            for channel in ctx.guild.channels:
                if channel.name == 'mutechannel':
                    lobbycode = new_lobbycode.upper()
                    embed2 = discord.Embed(title=lobbycode.upper(), color=0x2ecc71)
                    embed2.add_field(name='Mute', value='Press \N{Speaker with Cancellation Stroke}')
                    embed2.add_field(name='Unmute', value='Press \N{Speaker with Three Sound Waves}')
                    embed2.add_field(name='Dead', value='Press \N{Skull and Crossbones}')
                    embed2.add_field(name='Cancel', value='Press \N{Cross Mark}')
                    if (self.client.mute_message):
                        await self.client.mute_message.delete()
                    self.client.mute_message = await channel.send(embed=embed2)
                    await self.client.mute_message.add_reaction('\N{Speaker with Cancellation Stroke}')
                    await self.client.mute_message.add_reaction('\N{Speaker with Three Sound Waves}')
                    await self.client.mute_message.add_reaction('\N{Skull and Crossbones}')
                    await self.client.mute_message.add_reaction('\N{Black Universal Recycling Symbol}')
                    await self.client.mute_message.add_reaction('\N{Cross Mark}')
                    return
        else:
            embed3 = discord.Embed(title=new_lobbycode.upper() + ' is not a valid code!', color=0xff0000)
            await ctx.channel.send(embed=embed3)

    @commands.command(usage="!mute",
                      description="Mute all members",
                      help="This will mute the members from the channel where you are currently in.",
                      aliases=['m'])
    async def mute(self, ctx):
        vc = ctx.message.author.voice.channel
        for member in vc.members:
            if member.id != 235088799074484224:
                await member.edit(mute=1)
        await ctx.message.delete()

    @commands.command(usage="!unmute",
                      description="Unmute all members",
                      help="This will unmute the members from the channel where you are currently in.",
                      aliases=['um'])
    async def unmute(self, ctx):
        vc = ctx.message.author.voice.channel
        for member in vc.members:
            await member.edit(mute=0)
        await ctx.message.delete()

    @commands.command(usage="!switch",
                      description="Start a switch-game",
                      help="People in the voice channel will get assigned a name to pretend they are this person in the next game")
    async def switch(self, ctx):
        l1 = []
        vc = ctx.message.author.voice.channel
        for member in vc.members:
            if member.id != 235088799074484224:
                l1.append(member.nick)
        l2 = l1.copy()
        random.shuffle(l1)
        embed = discord.Embed(title='Switch-game', description='Click on the spoiler message next to your name to reveal who you need to be!', color=0x9b59b6)
        for i in range(len(l1)):
            embed.add_field(name=f'{l2[i]}', value='||' + f'{l1[i]}' + '||')
        await ctx.send(embed=embed)

    @commands.command(usage="!deads",
                      description="Show the list of dead people",
                      help="")
    async def deads(self, ctx):
        global dead
        await ctx.send(dead)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        global dead
        if user.id != self.client.user.id:
            try:
                if (reaction.message.id == self.client.mute_message.id):
                    mute_emoji = '\N{Speaker with Cancellation Stroke}'
                    unmute_emoji = '\N{Speaker with Three Sound Waves}'
                    cancel_emoji = '\N{Cross Mark}'
                    dead_emoji = '\N{Skull and Crossbones}'
                    recycle_emoji = '\N{Black Universal Recycling Symbol}'
                    if (str(reaction.emoji) == unmute_emoji):
                        await reaction.remove(user)
                        if (user.voice):
                            vc = user.voice.channel
                            for member in vc.members:
                                if member.name not in dead:
                                    await member.edit(mute=0, deafen=0)
                                else:
                                    await member.edit(mute=1, deafen=0)
                    if (str(reaction.emoji) == mute_emoji):
                        await reaction.remove(user)
                        if (user.voice):
                            vc = user.voice.channel
                            for member in vc.members:
                                if member.name not in dead:
                                    await member.edit(mute=1, deafen=1)
                                else:
                                    await member.edit(mute=0, deafen=0)
                    if (str(reaction.emoji) == cancel_emoji and user.voice):
                        await reaction.remove(user)
                        await self.client.mute_message.delete()
                        self.client.mute_message = None
                        if (user.voice):
                            vc = user.voice.channel
                            for member in vc.members:
                                await member.edit(mute=0, deafen=0)
                    if (str(reaction.emoji) == dead_emoji):
                        await reaction.remove(user)
                        dead.append(user.name)
                    if (str(reaction.emoji) == recycle_emoji):
                        await reaction.remove(user)
                        dead = []
                        if (user.voice):
                            vc = user.voice.channel
                            for member in vc.members:
                                await member.edit(mute=0, deafen=0)


# Allows to connect cog to bot
async def setup(client):
    await client.add_cog(Amongus(client))
