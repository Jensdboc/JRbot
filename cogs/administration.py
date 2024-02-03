import discord
import typing
from discord.activity import Spotify
from discord.ext import commands

from admincheck import admin_check

GENERAL_CHANNEL_ID = 764196816517464086


class Administration(commands.Cog):
    """
    This class contains the commands for administrations.
    """
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.check(admin_check)
    async def admin(self, ctx: commands.Context) -> None:
        """
        Confirm if user is an admin.

        :param ctx: The context.
        """
        await ctx.reply("Yup")

    @commands.command(usage="!nick <member> <name>",
                      description="Change nickname of member",
                      help="!nick @member a very cool nickname\nName is allowed to contain **spaces**")
    async def nick(self, ctx: commands.Context, member: discord.Member, *, nickname: str) -> None:
        """
        Give user a new nickname.

        :param ctx: The context.
        :param member: The member.
        :param nickname: The new nickname.
        """
        oldnick = member.nick
        await member.edit(nick=nickname)
        if oldnick is None:
            await ctx.send(f"{member.name} just got a new name: {member.nick}")
        else:
            await ctx.send(f"{oldnick} changed to {member.nick}")

    @commands.command(usage="!welcome <member>",
                      description="Give member all required roles",
                      help="Member will get 🌳-role, General Roles and Reward Roles")
    async def welcome(self, ctx: commands.Context, member: discord.Member) -> None:
        """
        Give a member the required roles.

        :param ctx: The context.
        :param member: The member.
        """
        amount_of_roles = 0
        for e in ctx.guild.roles:
            if e.name == '🌳' or e.name == '------------[ General Roles ]------------' or e.name == '------------[ Reward Roles ]------------':
                await member.add_roles(e)
                amount_of_roles += 1
        if amount_of_roles == 3:
            await ctx.reply(f"Added all roles to {member.name}")
        else:
            await ctx.reply(f"Something went wrong, added {amount_of_roles} roles to {member.name}")

    @commands.command(usage="!clear <number>",
                      description="Clear the last number of messages",
                      help="The default value is 1 message")
    @commands.check(admin_check)
    async def clear(self, ctx: commands.Context, *, number: int = 1) -> None:
        """
        Clear the last amount of messages in the current channel.

        :param ctx: The context.
        :param number: The amount of messages.
        """
        messages = [message async for message in ctx.channel.history(limit=number + 1)]
        await ctx.channel.delete_messages(messages)

    @commands.command(usage="!thumbmail <url>",
                      description="Return the thumbmail from youtube",
                      help="!thumbmail https://www.youtube.com/watch?v=dQw4w9WgXcQ 😏",
                      aliases=['tm'])
    async def thumbmail(self, ctx: commands.Context, url) -> None:
        """"
        Return the thumbmail of a given youtube url.

        :param ctx: The context.
        :param url: The youtube url.
        """
        await ctx.reply('https://i.ytimg.com/vi/' + str(url)[32:] + '/maxresdefault.jpg')
        await ctx.message.delete()

    @commands.command(usage="!show_activity <user>",
                      description="Return the songs people in the server are listening to",
                      help="Specifying a certain user doesn't work yet. Use !sa for now",
                      aliases=['sa'])
    async def show_activity(self, ctx: commands.Context, member: typing.Union[discord.Member, str] = None) -> None:
        """
        Show the spotify activity of users.

        :param ctx: The context.
        :param u_id: The ID of a user. If None show everyone, else only the user.
        """
        message = ""
        if member is None:
            for m in ctx.guild.members:
                for activity in m.activities:
                    if isinstance(activity, Spotify):
                        message += f"**{m.name}** is listening to **{activity.title}** from **{activity.album}** by **{activity.artist}**\n"
            if message == "":
                message = "No one is currently listening to Spotify :pensive:"
        else:
            if member == "me":
                member = ctx.author
            for activity in member.activities:
                if isinstance(activity, Spotify):
                    message = f"**{m.name}** is listening to **{activity.title}** from **{activity.album}** by **{activity.artist}**\n"
            if message == "":
                message = f"**{member.name}** is not currently listening to Spotify :pensive:"
        embed = discord.Embed(title="Spotify activity", description=message)
        await ctx.reply(embed=embed)

    @commands.command(usage="!join",
                      description="Make the bot join a voice channel",
                      help="The bot will and can only join the channel where you are currently in",
                      pass_context=True)
    async def join(self, ctx: commands.Context) -> None:
        """
        Make the bot join your current voice channel.

        :param ctx: The context.
        """
        try:
            channel = ctx.author.voice.channel
            await channel.connect()
            await ctx.message.add_reaction("✅")
        except Exception:
            await ctx.reply("You are currently not in a voice channel!")
            await ctx.message.add_reaction("❌")

    @commands.command(usage="!leave",
                      description="Make the bot leave a voice channel",
                      help="The bot will leave the channel even if you are not in the channel",
                      pass_context=True)
    async def leave(self, ctx: commands.Context) -> None:
        """
        Make the bot leave your current voice channel.

        :param ctx: The context.
        """
        try:
            client = ctx.message.guild.voice_client
            await client.disconnect()
            await ctx.message.add_reaction("✅")
        except Exception:
            await ctx.reply("The bot is currently not in a channel!")
            await ctx.message.add_reaction("❌")

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: commands.Context.channel) -> None:
        """
        Send a greeting in a newly created channel.

        :param channel: The newly created channel.
        """
        embed = discord.Embed(title='Welcome, I was expecting you...', colour=0xff0000)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        """
        Give a welcome message and assign the relevant roles to a newly joined member.

        :param member: The member.
        """
        general_ch = self.client.get_channel(GENERAL_CHANNEL_ID)
        embed = discord.Embed(title=f'Heyhey {member.display_name}!', colour=0xff0000)
        await general_ch.send(embed=embed)
        for e in member.guild.roles:
            if e.name == '🌳' or e.name == '------------[ General Roles ]------------' or e.name == '------------[ Reward Roles ]------------':
                await member.add_roles(e, reason=None)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """
        Give a goodbye message.

        :param member: The member.
        """
        general_ch = self.client.get_channel(GENERAL_CHANNEL_ID)
        embed = discord.Embed(title=f'Byebye {member.display_name}!', colour=0xff0000)
        await general_ch.send(embed=embed)


# Allows to connect cog to bot
async def setup(client):
    await client.add_cog(Administration(client))
