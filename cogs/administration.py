import discord
from discord.activity import Spotify
from discord.ext import commands
from discord import app_commands

from admincheck import admin_check


class Administration(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    @app_commands.check(admin_check)
    async def admin(self, ctx):
        await ctx.channel.send("Yup")

    @commands.command(usage="!nick <member> <name>",
                      description="Change nickname of member",
                      help="!nick @member a very cool nickname\nName is allowed to contain **spaces**")
    async def nick(self, ctx, member: discord.Member, *, nickname):
        oldnick = member.nick
        await member.edit(nick=nickname)
        if oldnick is None:
            await ctx.send(f"{member.name} just got a new name: {member.nick}")
        else:
            await ctx.send(f"{oldnick} changed to {member.nick}")

    @commands.command(usage="!welcome <member>",
                      description="Give member all required roles",
                      help="Member will get 🌳-role, General Roles and Reward Roles")
    async def welcome(self, context, member: discord.Member):
        for e in context.guild.roles:
            if e.name == '🌳' or e.name == '------------[ General Roles  ]------------' or e.name == '------------[ Reward Roles ]------------':
                await member.add_roles(e)

    @commands.command(usage="!clear <number>",
                      description="Clear the last number of messages",
                      help="The default value is 1 message")
    @app_commands.check(admin_check)
    async def clear(self, ctx, *, number=1):
        messages = [message async for message in ctx.channel.history(limit=number + 1)]
        await ctx.channel.delete_messages(messages)

    @commands.command(usage="!thumbmail <url>",
                      description="Return the thumbmail from youtube",
                      help="!thumbmail https://www.youtube.com/watch?v=dQw4w9WgXcQ 😏",
                      aliases=['tm'])
    async def thumbmail(self, ctx, url):
        await ctx.send('https://i.ytimg.com/vi/' + str(url)[32:] + '/maxresdefault.jpg')
        await ctx.message.delete()

    @commands.command(usage="!show_activity <user>",
                      description="Return the songs people in the server are listening to",
                      help="Specifying a certain user doesn't work yet. Use !sa for now",
                      aliases=['sa'])
    async def show_activity(self, ctx, user=0):
        if user == 0:
            for member in ctx.guild.members:
                for activity in member.activities:
                    if isinstance(activity, Spotify):
                        await ctx.send(f'{member.name} is listening to {activity.title} from {activity.album} by {activity.artist}')

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

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        embed = discord.Embed(title='Welcome, I was expecting you...', colour=0xff0000)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        for i in member.guild.channels:
            if i.name == 'general':
                ch = i
                embed = discord.Embed(title=f'Heyhey {member.display_name}!', colour=0xff0000)
                await ch.send(embed=embed)
                for e in member.guild.roles:
                    if e.name == '🌳' or e.name == '------------[ General Roles  ]------------' or e.name == '------------[ Reward Roles ]------------':
                        await member.add_roles(e, reason=None)
                        return

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        for i in member.guild.channels:
            if i.name == 'general':
                ch = i
                embed = discord.Embed(title=f'Byebye {member.display_name}!', colour=0xff0000)
                await ch.send(embed=embed)
                return


# Allows to connect cog to bot
async def setup(client):
    await client.add_cog(Administration(client))
