import discord
from discord.ext import commands
from sqlalchemy import true
from tables import Description

class CustomHelpCommand(commands.HelpCommand):

    def __init__(self):
        super().__init__()

    async def send_bot_help(self, mapping):
        print(mapping)
        for cog in mapping:
            if cog:
                print(cog.qualified_name)
                print(cog.description)
                # get_destination: Calls destination a.k.a. where you want to send the command
                await self.get_destination().send(f'{cog.qualified_name}: {[command.name for command in mapping[cog]]}') 

    async def send_cog_help(self, cog):
        print("Yooow")
        await self.get_destination().send(f'{cog.qualified_name}: {[command.name for command in cog.get_commands()]}')

    async def send_group_help(self, group):
        await self.get_destination().send(f'{group.name}: {[command.name for index, command in enumerate(group.commands)]}')
    
    async def send_command_help(self, command):
        title = command.name.capitalize()
        for alias in command.aliases:
            title += ', [!' + alias + ']'
        embed = discord.Embed(title=title, description=command.description)
        embed.add_field(name="Syntax:", value=command.usage, inline=False)
        embed.add_field(name="Example:", value=command.help, inline=False)
        await self.get_destination().send(embed=embed)