import discord
from discord.ext import commands

class Test(commands.Cog):
    
    def __init__(self, client):
        self.client = client

    #Command within a cog
    @commands.command()
    async def test(self, ctx):
        await ctx.send("Test!")

#Allows to connect cog to bot    
def setup(client):
    client.add_cog(Test(client))