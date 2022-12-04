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

    @tasks.loop(time = datetime.time(hour=0, minute=0, tzinfo=utc))
    async def loop(self): 
        with open('bank1.txt', 'r') as file:
            number = file.readlines()[0]
        with open('bank1.txt', 'w') as newfile:
            newnumber = int(number) + 2
            newfile.write(str(newnumber))
        channel = self.client.get_channel(1007689563440951326) #the-bank
        embed = discord.Embed(title="The bank", description="Your current balance is "+newnumber", use it wisely!", color=0x7289da) 
        await channel.send(embed=embed)

#Allows to connect cog to bot   
async def setup(client):
    await client.add_cog(Personal(client))