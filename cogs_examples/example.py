from discord.ext import commands


class Example(commands.Cog):

    def __init__(self, client):
        self.client = client

    """
    #Event within a cog (// @client.event)
    @commands.Cog.listener()
    async def on_ready(self):
        print('Bot is ready!')
    """

    # Command within a cog
    @commands.command()
    async def ping(self, ctx):
        await ctx.send("Pong!")


# Allows to connect cog to bot
def setup(client):
    client.add_cog(Example(client))
