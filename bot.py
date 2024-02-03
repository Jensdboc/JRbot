import os
import asyncio
import discord

from discord.ext import commands, tasks

from Help import CustomHelpCommand
from admincheck import admin_check
from constants import STATUS_CYCLE, PREFIX

intents = discord.Intents.all()
client = commands.Bot(command_prefix=PREFIX, help_command=CustomHelpCommand(),
                      case_insensitive=True, intents=intents)
status = STATUS_CYCLE


@tasks.loop(seconds=180)
async def change_status():
    await client.change_presence(activity=discord.Game(next(status)))


@client.event
async def on_ready():
    change_status.start()
    print('Bot = ready')


@client.command()
@commands.check(admin_check)
async def load(ctx, extension) -> None:
    """
    Load a given extension

    :param extension: Extension to be loaded.
    """
    await client.load_extension(f'cogs.{extension}')
    await ctx.send("Succesfully loaded `" + extension + '`')


@client.command()
@commands.check(admin_check)
async def unload(ctx, extension) -> None:
    """
    Unload a given extension

    :param extension: Extension to be unloaded.
    """
    await client.unload_extension(f'cogs.{extension}')
    await ctx.send("Succesfully unloaded `" + extension + '`')


@client.command()
@commands.check(admin_check)
async def reload(ctx, extension) -> None:
    """
    Reload a given extension

    :param extension: Extension to be reloaded.
    """
    await client.unload_extension(f'cogs.{extension}')
    await client.load_extension(f'cogs.{extension}')
    await ctx.send("Succesfully reloaded `" + extension + '`')


async def load_extensions() -> None:
    """
    Load every extensions in cogs folder.
    """
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await client.load_extension(f'cogs.{filename[:-3]}')


async def main():
    with open('token.txt', 'r') as file:
        token = file.readline()
        print("Reading token...")
    await load_extensions()
    await client.start(token)


if __name__ == "__main__":
    asyncio.run(main())
