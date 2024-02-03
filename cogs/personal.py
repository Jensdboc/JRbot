import datetime
import discord
from discord.ext import commands, tasks

utc = datetime.timezone.utc


class Personal(commands.Cog):

    def __init__(self, client: discord.Client):
        self.client = client
        self.loop.start()

    def open_file_and_adapt(amount):
        with open('bank1.txt', 'r') as file:
            number = file.readlines()[0]
        with open('bank1.txt', 'w') as newfile:
            newnumber = int(number) + amount
            newfile.write(str(newnumber))
        return newnumber

    @tasks.loop(time=datetime.time(hour=23, minute=00, tzinfo=utc))
    async def loop(self):
        newnumber = Personal.open_file_and_adapt(2)
        channel = self.client.get_channel(1007689563440951326)  # the-bank
        embed = discord.Embed(title="The bank", description=f"Your current balance is {str(newnumber)}, use it wisely!", color=0x7289da)
        await channel.send(embed=embed)

    @loop.before_loop
    async def before_printer(self):
        await self.client.wait_until_ready()

    @commands.command(usage="!add <amount>",
                      description="Add points to the bank",
                      help="!add 5\nStandard amount is 1.")
    async def add(self, ctx, amount=1):
        if (ctx.author.id == 656916865364525067 or ctx.author.id == 960445370062766121):
            newnumber = Personal.open_file_and_adapt(amount)
            channel = self.client.get_channel(1007689563440951326)  # the-bank
            embed = discord.Embed(title="The bank", description=f"Your current balance is {str(newnumber)}, use it wisely!", color=0x7289da)
            await channel.send(embed=embed)

    @commands.command(usage="!minus <amount>",
                      description="Minus points to the bank",
                      help="!minus 5\nStandard amount is 1.")
    async def minus(self, ctx, amount=1):
        if (ctx.author.id == 656916865364525067 or ctx.author.id == 960445370062766121):
            newnumber = Personal.open_file_and_adapt(-amount)
            channel = self.client.get_channel(1007689563440951326)  # the-bank
            embed = discord.Embed(title="The bank", description=f"Your current balance is {str(newnumber)}, use it wisely!", color=0x7289da)
            await channel.send(embed=embed)


# Allows to connect cog to bot
async def setup(client):
    await client.add_cog(Personal(client))
