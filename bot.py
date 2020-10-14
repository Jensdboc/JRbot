'''import nest_asyncio
nest_asyncio.apply()'''
import discord
from discord.ext import commands

client = commands.Bot(command_prefix='!')

@client.event
async def on_ready():
    print('euh ja het werkt fz')

'''@client.event
async def on_message_delete(message): 
    if message.author == client.user:
        await message.channel.send(message.content)
        return
    
    await message.channel.send('Someone just deleted this message from ' + message.author.name +  ' : ' + '```' + message.content + '```')'''

@client.event
async def on_guild_channel_create(channel):
    await channel.send('Welcome, I was expecting you...')

@client.command(aliases = ['m'])
async def mute(context):
    vc = context.message.author.voice.channel
    for member in vc.members:
        if member.voice.self_mute == 0:
            await member.edit(mute = 1)
    await context.message.delete()

@client.command(aliases = ['um'])
async def unmute(context):
    vc = context.message.author.voice.channel
    for member in vc.members:
        await member.edit(mute = 0)
    await context.message.delete()

@client.command()
async def clear(context,*,number=1):
    messages = await context.channel.history(limit = number+1).flatten()
    await context.channel.delete_messages(messages)

@client.command()
async def code(context,*,lobbycode):
    await context.message.delete()
    if len(lobbycode) == 6:
        await context.channel.send('```' + lobbycode.upper() + '```')

@client.command()
async def hotel(ctx):
    await ctx.send('Trivago!')
    
client.run('NzU0MDIwODIxMzc4MjY5MzI0.X1uqnA.o9Ea3VuoJpC797mfx0jFhLEozu4')