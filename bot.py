import asyncio
import discord
import os

from itertools import cycle
from discord.ext import commands, tasks
from pathlib import Path

from Help import CustomHelpCommand
from admincheck import admin_check

# Intents
intents = discord.Intents.all()

client = commands.Bot(command_prefix="!!", help_command=CustomHelpCommand(),
                      case_insensitive=True, intents=intents)
client.mute_message = None
status = cycle(["Goat Simulator and the grass is extra good today 🐐",
                "Monopoly and rent is due",
                "Monopoly",
                "still Monopoly",
                "Monopoly, this is taking too long",
                "Uno and I need new friends",
                "Patience but I'm running out of it 😤",
                "the Sims and the house burned down again",
                "Wii Sports and Matt showed up 😔",
                "Mario Cart and rainbow roads should be banned 🌈",
                "Tetris and the square is objectively the worst",
                "Just Dance and my knees hurt from Rasputin",
                "Roblox and got scammed on robux",
                "Fortnite and still can't build",
                "Rock Paper Scissors and in what world does paper win from rock",
                "Minecraft on peaceful 😌",
                "the long game",
                "the waiting game",
                "hard to get",
                "Russian Roulette and I'm the last one...",
                "waiting to claim my daily",
                "clicking the damned circles",
                "Valorant with a mousepad"])


@client.event
async def on_ready():
    change_status.start()
    print('Bot = ready')


@tasks.loop(seconds=180)
async def change_status():
    await client.change_presence(activity=discord.Game(next(status)))


# Create file if it doesn't exist
def file_exist(name):
    file = Path(name)
    file.touch(exist_ok=True)


# Loads extension
@client.command()
@commands.check(admin_check)
async def load(ctx, extension):
    await client.load_extension(f'cogs.{extension}')
    await ctx.send("Succesfully loaded `" + extension + '`')


# Unloads extension
@client.command()
@commands.check(admin_check)
async def unload(ctx, extension):
    await client.unload_extension(f'cogs.{extension}')
    await ctx.send("Succesfully unloaded `" + extension + '`')


# Reloads extension
@client.command()
@commands.check(admin_check)
async def reload(ctx, extension):
    await client.unload_extension(f'cogs.{extension}')
    await client.load_extension(f'cogs.{extension}')
    await ctx.send("Succesfully reloaded `" + extension + '`')


# Loads every extensions in cogs
async def load_extensions():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await client.load_extension(f'cogs.{filename[:-3]}')


@client.check
async def check_blacklist(ctx):
    file_exist('Blacklist.txt')
    with open('Blacklist.txt', 'r') as blacklist_file:
        for blacklisted_user in blacklist_file.readlines():
            if str(ctx.message.author.id) == str(blacklisted_user)[:-1]:
                return False
        return True


def admin_check(ctx):
    file_exist('Admin.txt')
    with open('Admin.txt', 'r') as admin_file:
        for admin in admin_file.readlines():
            if str(ctx.message.author.id) == str(admin)[:-1]:
                return True
        return False


@client.command()
@commands.check(admin_check)
async def blacklist(ctx, *, user_id):
    with open('Blacklist.txt', 'a') as blacklist_file:
        blacklist_file.write(user_id + '\n')


@client.command()
@commands.check(admin_check)
async def admin(ctx):
    await ctx.channel.send('Yup')


@client.command()
@commands.check(admin_check)
async def start(ctx, thema=None, woord=None):
    if thema is None or woord is None:
        embed = discord.Embed(title='Woordenketting', description='Something went wrong with starting a game. Use !start <theme> <word>', colour=0xFF0000)
        await ctx.send(embed=embed)
        return
    else:
        with open('Woordenketting.txt', 'a') as txt:
            txt.truncate(0)
            txt.write(thema + '\n' + woord + '\t' + str(ctx.message.author.id) + '\n')
        with open('Woordenketting_users.txt', 'a') as user_file:
            user_file.truncate(0)
            user_file.write(str(ctx.message.author.id) + '\n')
        embed = discord.Embed(title='Woordenketting', description='A new game has been started with ' + '`' + thema + '`' + ' as theme and ' + '`' + woord + '`' + ' as first word.', colour=0x11806a)
        await ctx.send(embed=embed)


@client.command(aliases=['cld'])
@commands.check(admin_check)
async def cleardates(ctx):
    with open('Examen_data.txt', 'w'):
        pass
    await ctx.send("All dates have been succesfully cleared!")


async def main():
    with open('token.txt', 'r') as file:
        token = file.readline()
        print("Reading token...")
    await load_extensions()
    await client.start(token)


if __name__ == "__main__":
    asyncio.run(main())
