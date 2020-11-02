with open('ID.txt', 'r') as IDfile:
    for ID in IDfile.readlines():
        if ID == 'Jens':
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
            if str(ctx.message.author.id) == str(blacklisted_user)[:-1]:
                return False
        return True

def admin_check(ctx):
    with open('Admin.txt', 'r') as admin_file:
        for admin in admin_file.readlines():
            if str(ctx.message.author.id) == str(admin)[:-1]:
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

@client.command()
@commands.check(admin_check)
async def start(ctx, dier):
    with open('Dieren.txt','a') as txt: 
        txt.truncate(0)
        txt.write(dier + '\n')
    with open('Last_user.txt', 'a') as user_file:
        user_file.truncate(0)
        user_file.write('placeholder')
    embed =  discord.Embed(title='Woordenketting', description='A new game has been started with ' + '`' + dier + '`' + ' as first word.', colour=0x11806a)
    await ctx.send(embed=embed)
    
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
            embed1 = discord.Embed(title=lobbycode, color=0x2ecc71)
            await context.channel.send(embed=embed1) 
        else:
            embed2 = discord.Embed(title='No code yet', color=0xff0000)
            await context.channel.send(embed=embed2) 
    elif len(new_lobbycode) == 9 or len(new_lobbycode) == 6:
        lobbycode = new_lobbycode.upper()
        embed3 = discord.Embed(title=lobbycode.upper(), color=0x2ecc71)
        await context.channel.send(embed=embed3) 
    else:
        embed4 = discord.Embed(title=new_lobbycode.upper()+ ' is not a valid code!', color=0xff0000)
        await context.channel.send(embed=embed4)    
        
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
    embedVar = discord.Embed(title="Trivago!", color=0x992d22)
    await ctx.send(embed=embedVar)
        
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

#User commands dierenketting

@client.command(aliases = ['d'])
async def dier(ctx,*, dier=None):
    list = []
    with open('Dieren.txt','r') as txt: 
        for word in txt.readlines():
            list.append(str(word[:-1]))
            woord = list[-1] 
            letter = list[-1][-1]
    if dier == None:
        embed =  discord.Embed(title='Woordenketting', description='You need to find an animal starting with ' + '`' + letter + '`' + ', final letter of ' + '`' + woord + '`', colour=0x11806a)
        await ctx.send(embed=embed)
        return
    '''
    if dier.lower() in list:
        embed =  discord.Embed(title='Woordenketting', description='`' + dier + '`' + ' already in list!', colour=0xff0000)
        await ctx.send(embed=embed)
        return 
    elif dier.lower() == 'linx' or dier.lower() == 'lynx':
        embed =  discord.Embed(title='Woordenketting', description='`' + dier + '`' + ' has NOT been added!', colour=0xff0000)
        embed.add_field(name='Note', value='Do you really have to be that guy?')
        await ctx.send(embed=embed)
        return 
    '''
    with open('Last_user.txt', 'r') as user_file:
        for user in user_file.readlines():
            with open('Dieren.txt','a') as txt:
                if str(ctx.message.author.id) != user and str(dier[0]).lower() == letter.lower():
                    with open('Last_user.txt', 'a') as user_file:
                        user_file.truncate(0)
                        user_file.write(str(ctx.message.author.id)) 
                        txt.write(dier.lower() + '\n')
                        embed =  discord.Embed(title='Woordenketting', description='`' + dier + '`' + ' has been added!', colour=0x11806a)
                        await ctx.send(embed=embed)
                elif str(dier[0]).lower() != letter.lower() and str(ctx.message.author.id) != user:
                    embed =  discord.Embed(title='Animal should start with ' + '`' + letter + '`' + ', final letter of ' + '`' + woord + '`', colour=0xff0000)
                    await ctx.send(embed=embed)
                else:
                    embed =  discord.Embed(title='Woordenketting', description='You need to wait for someone else to submit an animal!', colour=0xff0000)
                    await ctx.send(embed=embed)        
    if dier.lower() in list:
        embed =  discord.Embed(title='Woordenketting', description='`' + dier + '`' + ' already in list!', colour=0xff0000)
        await ctx.send(embed=embed)
        return 
    elif dier.lower() == 'linx' or dier.lower() == 'lynx':
        embed =  discord.Embed(title='Woordenketting', description='`' + dier + '`' + ' has NOT been added!', colour=0xff0000)
        embed.add_field(name='Note', value='Do you really have to be that guy?')
        await ctx.send(embed=embed)
        return 
@client.command()
async def count(ctx):
    number = 0
    with open('Dieren.txt','r') as txt: 
        for word in txt.readlines():
            number += 1
    embed = discord.Embed(title='Woordenketting', description='The list contains ' + '`' + f'{number}' + '`' + ' animals so far.', colour=0x11806a)
    await ctx.send(embed=embed)
    
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