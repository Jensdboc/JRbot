import discord
from discord.ext import commands
import random
import re
import typing
import asyncio
import nltk

MAX_TITLE_LENGTH = 256
LARS_CHANNEL_ID = 1178007345243103302


class Fun(commands.Cog):

    def __init__(self, client):
        self.client = client

    autist_id = 383952659310444544

    @commands.command(usage="!mock <sentence>",
                      description="Randomly capitalize the sentence",
                      help="The sentence can contain **spaces**")
    async def mock(self, ctx, *, to_mock):
        mocked_text = ''
        if (ctx.message.author.id == 383952659310444544):
            c = 0
            for i in range(len(to_mock)):
                if (c % 2):
                    mocked_text += to_mock[i].lower()
                else:
                    mocked_text += to_mock[i].upper()
                if (to_mock[i] != ' '):
                    c += 1
        else:
            for i in range(len(to_mock)):
                if (i % 2):
                    mocked_text += to_mock[i].upper()
                else:
                    mocked_text += to_mock[i].lower()
        embed = discord.Embed(title=mocked_text, color=0xe67e22)
        await ctx.send(embed=embed)

    @commands.command(usage="!hotel",
                      description="Trivago!",
                      help="")
    async def hotel(self, ctx):
        embedVar = discord.Embed(title="Trivago!", color=0x992d22)
        await ctx.send(embed=embedVar)

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
    async def hug(self, ctx, target: typing.Union[discord.Member, discord.Role] = None):
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

    @commands.command(usage="!answer <sentence>",
                      description="Send a message to Britt for quizzes",
                      help="Sentence can contain **spaces**",
                      aliases=['a'])
    async def answer(self, ctx):
        for user in self.client.users:
            # Id van Britt
            if user == self.client.get_user(688070365448241247):
                name = str(ctx.author.name)
                answer = ''
                start = 0
                for letter in ctx.message.content:
                    if start > 0:
                        answer += str(letter)
                    if str(letter) == ' ':
                        start += 1
                embed = discord.Embed(title=f'{name}: {answer}', color=0x7289da)
                await user.send(embed=embed)

    @commands.command(usage="!secret <sentence>",
                      description="Send a secret message",
                      help="This message will be posted in the secretchannel with a randomised color :). Sentence can contain **spaces**")
    async def secret(self, ctx):
        channel = self.client.get_channel(935507669580652544)
        message = ctx.message.content[8:]
        embed_color = random.randint(0, 16777215)
        # Split message if longer than 256 (= embed title character limit) characters
        if len(message) >= MAX_TITLE_LENGTH:

            # You only have to do this once (you can comment it out afterwards)
            nltk.download('punkt')

            # Seperate words into messages of max 256 characters
            words = nltk.word_tokenize(message)
            messages = []
            current_line = ""
            for word in words:
                if len(current_line) + len(word) + 1 <= MAX_TITLE_LENGTH:
                    current_line += word + " "
                else:
                    messages.append(current_line.strip())
                    current_line = word + " "
            if current_line:
                messages.append(current_line.strip())

            # Print each message with message number
            embeds = []
            for i in range(len(messages)):
                embeds.append(discord.Embed(title=messages[i], description=f"{i+1}/{len(messages)}", color=discord.Color(embed_color)))
            await channel.send(embeds=embeds)

        else:
            embed = discord.Embed(title=message, color=discord.Color(embed_color))
            await channel.send(embed=embed)

    @commands.command(usage="!pewpew <user>",
                      description="Pewpew somebody ",
                      help="This person won't be able to see the normal channels anymore because he/she is dead")
    async def pewpew(self, ctx, member: discord.Member):
        pewpew_role = ctx.guild.get_role(943050771228917812)  # Boomhut
        # Check if person doesn't have pewpewrole
        if pewpew_role in ctx.author.roles:
            embed = discord.Embed(title="Whoops...", description="Dead people are not supposed to kill people.", color=0xDC143C)
            await ctx.send(embed=embed)
            return
        # Decide if person is going to get shot
        chance = random.randint(0, 10)
        if chance < 8:
            await member.add_roles(pewpew_role)
            await ctx.send(f"Oh no, {member.name} has been shot!")
            await asyncio.sleep(180)  # Wait time
            await member.remove_roles(pewpew_role)
            await ctx.send(f"{member.name} has been revived!")
        elif chance < 10:
            await ctx.send(f"The shot missed {member.name}!")
        elif chance == 10:
            await ctx.author.add_roles(pewpew_role)
            await ctx.send(f"Oh no, {ctx.author.name} shot themself! Now laugh!")
            await asyncio.sleep(100)  # Wait time
            await ctx.author.remove_roles(pewpew_role)
            await ctx.send(f"{ctx.author.name} has been revived!")

    @commands.command(usage="!lars <correction>",
                      description="The wrong message will be posted into the channel with the correction underneath",
                      help="This message will be posted in the channel of Lars. Reply to the message that contains a mistake.")
    async def lars(self, ctx: commands.Context, *, description: str = None):
        lars_channel = self.client.get_channel(LARS_CHANNEL_ID)
        if ctx.message.reference is not None:
            lars_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            if lars_message:
                if lars_message.author.id != 350243309270335489:
                    embed = discord.Embed(title="Woops...", description="This message was not from Lars!")
                    await ctx.reply(embed=embed)
                else:
                    embed = discord.Embed(title=lars_message.content, description=description)
                    await lars_channel.send(embed=embed)
        else:
            embed = discord.Embed(title="Woops...", description="You did not reply to a message of Lars!")
            await ctx.reply(embed=embed)

    @commands.Cog.listener("on_message")
    async def taylor(self, message):
        verboden_woorden = ['taylor swift', 'taylor', 'swift', 'taylorswift', 'folklore', 'love story', 'evermore', 'lovestory', 'taytay', 't swizzle', 'tswizzle', 'swizzle', 'queen t']
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
        if message.author.id == 589027434611867668:  # Pingo id
            pattern_match = re.compile(r"You need to wait (\d+ day(s)?, )?\d+ hour(s)? and \d+ minute(s)? before you can collect your next credits")
            present = pattern_match.match(message.content)
            emoji = "\U0001F1F1"  # regional_indicator_l
            if present:
                await message.add_reaction(emoji)


# Allows to connect cog to bot
async def setup(client):
    await client.add_cog(Fun(client))
