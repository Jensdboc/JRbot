import discord

client = discord.Client()

@client.event
async def on_ready():
    print('euh ja het werkt fz')
    
@client.event
async def on_message(message):
    if message.author == client.user:
        if message.content == 'Welcome, I was expecting you...':
            await message.pin()
        return

    if message.content.startswith('Oei'):
        await message.channel.send('Oei')


@client.event
async def on_message_delete(message): 
    if message.author == client.user:
        await message.channel.send(message.content)
        return
    
    await message.channel.send('Someone just deleted this message from ' + message.author.name +  ' : ' + '```' + message.content + '```')

@client.event
async def on_reaction_add(reaction,user):
    if user == client.user:
        return
    
    await reaction.message.add_reaction(reaction)

@client.event
async def on_guild_channel_create(channel):
    await channel.send('Welcome, I was expecting you...')

client.run('NzU0MDIwODIxMzc4MjY5MzI0.X1uqnA.o9Ea3VuoJpC797mfx0jFhLEozu4')