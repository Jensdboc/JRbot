#Imports
from inspect import signature
from io import StringIO
from typing import overload
import discord
from discord.ext import commands 
import random
from discord.utils import get
from discord import FFmpegPCMAudio
from youtube_dl import YoutubeDL

import typing

#import for cogs
import os

#Intent for hug
intents = discord.Intents.default()  # Allow the use of custom intents
intents.members = True

client = commands.Bot(command_prefix="!", case_insensitive=True, intents=intents)
client.mute_message = None

#***********#
#Cogs commands#
#***********#

#Loads extension
@client.command()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')
    await ctx.send("Succesfully loaded `" + extension + '`')

#Unloads extension
@client.command()
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    await ctx.send("Succesfully unloaded `" + extension + '`')

#Reloads extension
@client.command()
async def reload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')
    await ctx.send("Succesfully reloaded `" + extension + '`')
    
#Loads every extensions in cogs
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

#***********#
#Ready check#
#***********#

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="youtube"))
    print('Bot = ready')

#**************#
#Command checks#
#**************#

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

#**************# 
#Admin commands#
#**************# 

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

@client.command(aliases = ['cld'])
@commands.check(admin_check)
async def cleardates(ctx):
    with open('Examen_data.txt', 'w') as file:
        pass
    await ctx.send("All dates have been succesfully cleared!")

#**********#
#Bot events#
#**********#

@client.event
async def on_message(message):
    
    verboden_woorden = ['taylor swift','taylor', 'swift', 'taylorswift', 'folklore', 'love story', 'evermore', 'lovestory', 'taytay', 't swizzle', 'tswizzle', 'swizzle', 'queen t']
    aantal = 0
    for woord in verboden_woorden:
        if message.author.id == 249527744466124801 or message.author.id == 688070365448241247:
            if woord in message.content.lower() and message.author.id != 754020821378269324 and aantal == 0:
                embed = discord.Embed(title='Toch weer nie over Taylor Swift bezig???', colour=0x000000) 
                aantal += 1 
                await message.channel.send(embed=embed)
        else:
            if woord in message.content.lower() and message.author.id != 754020821378269324 and message.author.id != 235088799074484224 and aantal == 0:
                link2 = 'https://media.discordapp.net/attachments/764196816517464086/786677044335083570/dh5qukew5vv01.jpg?width=582&height=599'
                embed = discord.Embed(title='Toch weer nie over Taylorreeksen bezig???', colour=0x000000) 
                embed.set_image(url=link2)
                aantal += 1
                await message.channel.send(embed=embed)
    await client.process_commands(message)
    
@client.event
async def on_guild_channel_create(channel):
    embed =  discord.Embed(title='Welcome, I was expecting you...', colour=0xff0000)
    await channel.send(embed=embed)

@client.event
async def on_member_join(member):
    for i in member.guild.channels:
        if i.name == 'general':
            ch = i
            embed = discord.Embed(title=f'Heyhey {member.display_name}!', colour=0xff0000)
            await ch.send(embed=embed)
            for e in member.guild.roles:
                if e.name == 'Crewmates':
                    await member.add_roles(e,reason=None)
                    return 
        
@client.event
async def on_member_remove(member):
    for i in member.guild.channels:
        if i.name == 'general':
            ch = i
            embed = discord.Embed(title=f'Byebye {member.display_name}!', colour=0xff0000)
            await ch.send(embed=embed)
            return 

client.run('NzU0MDIwODIxMzc4MjY5MzI0.X1uqnA.o9Ea3VuoJpC797mfx0jFhLEozu4')
