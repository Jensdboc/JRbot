import asyncio
import discord
import os

from itertools import cycle
from discord.ext import commands, tasks 

from Help import CustomHelpCommand
from admincheck import admin_check

# Intents
intents = discord.Intents.all()

client = commands.Bot(command_prefix="!", help_command=CustomHelpCommand(), case_insensitive=True, intents=intents)
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

#Loads extension
@client.command()
@commands.check(admin_check)
async def load(ctx, extension):
    await client.load_extension(f'cogs.{extension}')
    await ctx.send("Succesfully loaded `" + extension + '`')

#Unloads extension
@client.command()
@commands.check(admin_check)
async def unload(ctx, extension):
    await client.unload_extension(f'cogs.{extension}')
    await ctx.send("Succesfully unloaded `" + extension + '`')

#Reloads extension
@client.command()
@commands.check(admin_check)
async def reload(ctx, extension):
    await client.unload_extension(f'cogs.{extension}')
    await client.load_extension(f'cogs.{extension}')
    await ctx.send("Succesfully reloaded `" + extension + '`')

#Loads every extensions in cogs
async def load_extensions():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await client.load_extension(f'cogs.{filename[:-3]}')

async def main():
    with open('token.txt', 'r') as file:
        token = file.readline()
        print("Reading token...")
    await load_extensions()
    await client.start(token)

asyncio.run(main())