import random
import discord
from discord.ext import commands

from admincheck import admin_check

lobbycode = None
dead = []


class Amongus(commands.Cog):
    """
    This class contains the commands for Among Us.
    """
    def __init__(self, client: discord.Client):
        self.client = client
        self.client.mute_message = None

    @commands.command(usage="!code <code>",
                      description="Start among us game in mutechannel",
                      help="The code has to be a valid 6-digit number. The following message will be posted in mutechannel",
                      aliases=['cd'])
    async def code(self, ctx: commands.Context, *, new_lobbycode: str = None) -> None:
        """
        Show lobbycode or update to a new code.

        :param ctx: The Context.
        :param new_lobbycode: The new lobbycode, if None show old lobbycode.
        """
        global lobbycode
        if new_lobbycode is None:
            if lobbycode is not None:
                embed1 = discord.Embed(title=lobbycode, color=0x2ecc71)
            else:
                embed1 = discord.Embed(title="No code yet!", color=0xff0000)
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
    @commands.check(admin_check)
    async def mute(self, ctx: commands.Context) -> None:
        """
        Mute all members in your current voice channel

        :param ctx: The Context.
        """
        vc = ctx.message.author.voice.channel
        for member in vc.members:
            await member.edit(mute=1)

    @commands.command(usage="!unmute",
                      description="Unmute all members",
                      help="This will unmute the members from the channel where you are currently in.",
                      aliases=['um'])
    @commands.check(admin_check)
    async def unmute(self, ctx: commands.Context) -> None:
        """
        Unmute all members in your current voice channel

        :param ctx: The Context.
        """
        vc = ctx.message.author.voice.channel
        for member in vc.members:
            await member.edit(mute=0)

    @commands.command(usage="!switch",
                      description="Start a switch-game",
                      help="People in the voice channel will get assigned a name to pretend they are this person in the next game")
    async def switch(self, ctx: commands.Context) -> None:
        """
        Assign people in the voice random names from other people.

        :param ctx: The Context.
        """
        l1 = []
        vc = ctx.message.author.voice.channel
        for member in vc.members:
            l1.append(member.nick)
        l2 = l1.copy()
        random.shuffle(l1)
        embed = discord.Embed(title='Switch-game', description='Click on the spoiler message next to your name to reveal who you need to be!', color=0x9b59b6)
        for i in range(len(l1)):
            embed.add_field(name=f'{l2[i]}', value='||' + f'{l1[i]}' + '||')
        await ctx.reply(embed=embed)

    @commands.command(usage="!deads",
                      description="Show the list of dead people",
                      help="")
    async def deads(self, ctx: commands.Context) -> None:
        """"
        Show the list of dead people in the Among Us game

        :param ctx: The Context.
        """
        global dead
        await ctx.send(dead)

    @commands.Cog.listener("on_reaction_add")
    async def on_reaction_add_among_us(self, reaction: discord.Reaction, user: discord.User) -> None:
        """
        Execute the code whenever a reaction is pressed.

        :param reaction: The pressed reaction.
        :param user: The user.
        """
        global dead
        if user.bot:
            return

        if self.client.mute_message != None:
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
            except Exception as e:
                print(f"Exception in on_reaction_add: {e}")


# Allows to connect cog to bot
async def setup(client):
    await client.add_cog(Amongus(client))
