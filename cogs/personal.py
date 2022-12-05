import discord
from discord.ext import commands, tasks
import typing
import asyncio
import datetime

#*****************#     
#User commands fun#
#*****************# 

utc = datetime.timezone.utc

class Personal(commands.Cog):

    def __init__(self, client):
        self.client = client  
        self.loop.start()

<<<<<<< HEAD
    @tasks.loop(time = datetime.time(hour=23, minute=0, tzinfo=utc))
    async def loop(self): 
=======
    def open_file_and_adapt(amount):
>>>>>>> a44d1ba63872c1e605d3d8c84e6dbde1a1af63bd
        with open('bank1.txt', 'r') as file:
            number = file.readlines()[0]
        with open('bank1.txt', 'w') as newfile:
            newnumber = int(number) + amount
            newfile.write(str(newnumber))
        return newnumber

    @tasks.loop(time = datetime.time(hour=23, minute=0, tzinfo=utc))
    async def loop(self): 
        # with open('bank1.txt', 'r') as file:
        #     number = file.readlines()[0]
        # with open('bank1.txt', 'w') as newfile:
        #     newnumber = int(number) + 2
        #     newfile.write(str(newnumber))
        newnumber = self.open_file_and_adapt(2)
        channel = self.client.get_channel(1007689563440951326) #the-bank
        embed = discord.Embed(title="The bank", description="Your current balance is "+str(newnumber)+", use it wisely!", color=0x7289da) 
        await channel.send(embed=embed)

    @loop.before_loop
    async def before_printer(self):
        print('waiting...')
        await self.client.wait_until_ready()

    @commands.command(usage="!add <amount>", 
                      description="Add points to the bank", 
                      help="!add 5\nStandard amount is 1.")
    async def add(self, ctx, amount=1):
        newnumber = self.open_file_and_adapt(amount)
        channel = self.client.get_channel(1007689563440951326) #the-bank
        embed = discord.Embed(title="The bank", description="Your current balance is "+str(newnumber)+", use it wisely!", color=0x7289da) 
        await channel.send(embed=embed)
        
    @commands.command(usage="!minus <amount>", 
                      description="Minus points to the bank", 
                      help="!minus 5\nStandard amount is 1.")
    async def minus(self, ctx, amount=1):
        newnumber = self.open_file_and_adapt(-amount)
        channel = self.client.get_channel(1007689563440951326) #the-bank
        embed = discord.Embed(title="The bank", description="Your current balance is "+str(newnumber)+", use it wisely!", color=0x7289da) 
        await channel.send(embed=embed)

#Allows to connect cog to bot   
async def setup(client):
    await client.add_cog(Personal(client))
