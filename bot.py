with open('ID.txt', 'r') as IDfile:
    if IDfile.readline(0) == 'Jens':
        import nest_asyncio
        nest_asyncio.apply()
import discord
from discord.ext import commands

client = commands.Bot(command_prefix='!')

@client.event
async def on_ready():
    print('euh ja het werkt fz')

#Command checks

@client.check
async def check_blacklist(ctx):
    with open('Blacklist.txt', 'r') as blacklist_file:
        for blacklisted_user in blacklist_file.readlines():
            if str(ctx.message.author.id) == blacklisted_user:
                return False
        return True

def admin_check(ctx):
    with open('Admin.txt', 'r') as admin_file:
        for admin in admin_file.readlines():
            if str(ctx.message.author.id) == admin:
                return True
        return False

#Admin commands

@client.command()
@commands.check(admin_check)
async def blacklist(ctx,*,user_id):
    with open('Blacklist.txt', 'a') as blacklist_file:
        blacklist_file.write(user_id + '\n')

@client.command()
@commands.check(admin_check)
async def admin(ctx):
    await ctx.channel.send('Yup')

#User commands

@client.command(aliases = ['m'])
async def mute(context):
    vc = context.message.author.voice.channel
    for member in vc.members:
        if member.voice.self_mute == 0 and member.id != 235088799074484224:
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

lobbycode = None
@client.command(aliases = ['cd'])
async def code(context,*,new_lobbycode=''):
    global lobbycode 
    await context.message.delete()
    if len(new_lobbycode) == 0:
        if (lobbycode != None):
            await context.channel.send('```' + lobbycode + '```')
        else:
            await context.channel.send('No code yet')
    elif len(new_lobbycode) == 9 or len(new_lobbycode) == 6:
        lobbycode = new_lobbycode.upper()
        await context.channel.send('```' + lobbycode.upper() + '```')
    else:
        await context.channel.send(new_lobbycode.upper() + ' is not a valid code!')    
        
@client.command()
async def mock(ctx,*,to_mock):
    mocked_text = ''
    for i in range(len(to_mock)):
        if (i%2):
            mocked_text += to_mock[i].upper()
        else:
            mocked_text += to_mock[i].lower()
    await ctx.send(mocked_text)
            
@client.command()
async def hotel(ctx):
    await ctx.send('Trivago!')
        
@client.command()
async def vliegt_de_blauwvoet(ctx):
    await ctx.send('``Storm op zee!``') 
    
@client.command()
async def python(ctx):
    await ctx.send('Nu blij Benjamin?')
    
@client.command()
async def stemopsimon(ctx):
    await ctx.send('Sinds wanneer heeft een SSL stemmen nodig?')

@client.command()
async def crew(context, member : discord.Member):
    for e in context.guild.roles:
        if e.name == 'Crewmates':
            await member.add_roles(e)
            return 

@client.command()
async def commands(context):
    await context.send('```md\n' + '#!mute (!m)= Mutes the voice chat.\n'
                       '#!unmute (!um)= Unmutes the voice chat.\n'
                       '#!clear <#> = Clears the last number of messages (standard = 1)\n'
                       '#!code <******-**>= Formats 6-digit code.\n'
                       '#!code = Resends current code.\n'
                       '#!hotel = Just try it!' + '```')

#Bot events

@client.event
async def on_guild_channel_create(channel):
    await channel.send('Welcome, I was expecting you...')

@client.event
async def on_member_join(member):
    for i in member.guild.channels:
        if i.name == 'general':
            ch = i
            await ch.send(f'Heyhey {member.display_name}!')
            for e in member.guild.roles:
                if e.name == 'Crewmates':
                    await member.add_roles(e,reason=None)
                    return 
        
@client.event
async def on_member_remove(member):
    for i in member.guild.channels:
        if i.name == 'general':
            ch = i
            await ch.send(f'Byebye {member.display_name}!')
            return 

client.run('NzU0MDIwODIxMzc4MjY5MzI0.X1uqnA.o9Ea3VuoJpC797mfx0jFhLEozu4')