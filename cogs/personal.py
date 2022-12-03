import discord
from discord.ext import commands, tasks
import typing
import asyncio
import datetime

#*****************#     
#User commands fun#
#*****************# 

utc = datetime.timezone.utc
time = datetime.time(hour=0, minute=0, tzinfo=utc),

class Personal(commands.Cog):

    def __init__(self, client):
        self.client = client  
        self.loop.start()

    @tasks.loop(time = time)
    async def loop(self): 
        channel = self.client.get_channel(765211470744518658)
        embed = discord.Embed(title="Ignore this please", description="This is an automated message! Please do not try to respond!", color=0x7289da) 
        await channel.send(embed=embed)

#Allows to connect cog to bot   
async def setup(client):
    await client.add_cog(Personal(client))