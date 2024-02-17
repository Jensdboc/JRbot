import datetime
import discord
import os
import typing
from discord.ext import commands

utc = datetime.timezone.utc


class Daycounter(commands.Cog):
    """
    This class contains the commands for Daycounter.
    """
    def __init__(self, client: discord.Client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """"
        Creates the Day_counter.txt file
        """
        file_path = "Day_counters.txt"
        if not os.path.exists(file_path):
            with open(file_path, 'w'):
                pass
            print(f"{file_path} created")

    def printcounter(counter_name: str, ctx_guild_id: int) -> typing.Union[discord.Embed, None]:
        """
        Creates an embed message for a counter.

        :param counter_name: Name of the counter.
        :param ctx_guild_id: ID of the guild.
        """
        with open('Day_counters.txt', 'r') as file:
            content = file.readlines()
        for line in content:
            name, last_reset, _, description, guild_id = line[:-1].split("\t")
            if name.lower() == counter_name.lower() and guild_id == ctx_guild_id:
                days_since_last_reset = (datetime.datetime.now() - datetime.datetime.strptime(last_reset, "%Y/%m/%d")).days
                message = f"It's been **{str(days_since_last_reset)}** days since {description.lower()}."
                embed = discord.Embed(title=name, description=message)
                return embed
        return None

    @commands.command(usage="!createcounter <name> <description>",
                      description="Creates a new counter and sets the last reset to the current date",
                      help="!createcounter Goose the last goose incident\nThe name cannot contain any spaces. The description will be be added to the sentence *It has been been x days since ...*.",
                      aliases=["makecounter", "startcounter", "cc"])
    async def createcounter(self, ctx: commands.Context, name: str = None, *, description: str = None) -> None:
        """
        Creates a counter and adds it to the file.

        :param ctx: The context.
        :param name: The name of the counter.
        :param description: The description of the counter.
        """
        if name is None or description is None:
            await ctx.send("Please add a name and description for your counter.")
            return
        with open('Day_counters.txt', 'r') as readfile:
            for line in readfile.readlines():
                counter_name, _, _, _, guild_id = line[:-1].split("\t")
                if name.lower() == counter_name.lower() and guild_id == str(ctx.guild.id):
                    await ctx.send(f"There already exists a counter with the name **{name.capitalize()}**. Please pick a new name or delete the previous one.")
                    return
        with open('Day_counters.txt', 'a') as file:
            last_reset = datetime.datetime.now().strftime("%Y/%m/%d")
            creator_id = str(ctx.message.author.id)
            guild_id = str(ctx.guild.id)
            counter_entry = f"{name.capitalize()}\t{last_reset}\t{creator_id}\t{description}\t{guild_id}\n"
            file.write(counter_entry)
        embed = Daycounter.printcounter(name, guild_id)
        if embed is not None:
            await ctx.send(embed=embed)

    @commands.command(usage="!deletecounter <name>",
                      description="Deletes a counter by name",
                      help="!deletecounter goose",
                      aliases=["removecounter", "dc"])
    async def deletecounter(self, ctx: commands.Context, to_delete: str = None) -> None:
        """
        Deletes a counter from the file.

        :param ctx: The context.
        :param to_delete: The counter to delete.
        """
        if to_delete is None:
            await ctx.send("Please specify which counter you want to delete.")
            return
        with open('Day_counters.txt', 'r') as file:
            content = file.readlines()
        with open('Day_counters.txt', 'w') as newfile:
            deleted = False
            ctx_guild_id = str(ctx.guild.id)
            for line in content:
                name, _, creator_id, _, guild_id = line[:-1].split("\t")
                if to_delete.lower() == name.lower() and guild_id == ctx_guild_id:
                    if creator_id != str(ctx.message.author.id):
                        await ctx.send("You can only delete counters you created!")
                        newfile.write(line)
                    else:
                        await ctx.send(f"Counter **{to_delete.capitalize()}** has been succesfully deleted.")
                    deleted = True
                else:
                    newfile.write(line)
            if not deleted:
                await ctx.send(f"No counter with name **{to_delete.capitalize()}** was found.")

    # Resets the counter to the current date
    @commands.command(usage="!resetcounter <name>",
                      description="Resets a counter and displays how many days have passed since the last reset.",
                      help="!resetcounter goose",
                      aliases=["rc"])
    async def resetcounter(self, ctx: commands.Context, to_reset: str = None) -> None:
        """
        Resets the counter to the current date.

        :param ctx: The context.
        :param to_reset: The counter to reset.
        """
        if to_reset is None:
            await ctx.send("Please specify which counter you want to reset.")
            return
        with open('Day_counters.txt', 'r') as file:
            content = file.readlines()
        with open('Day_counters.txt', 'w') as newfile:
            reset = False
            ctx_guild_id = str(ctx.guild.id)
            for line in content:
                name, last_reset, creator_id, description, guild_id = line[:-1].split("\t")
                if to_reset.lower() == name.lower() and guild_id == ctx_guild_id:
                    if creator_id != str(ctx.message.author.id):
                        await ctx.send("You can only reset counters you created!")
                        newfile.write(line)
                    else:
                        days_since_last_reset = (datetime.datetime.now() - datetime.datetime.strptime(last_reset, "%Y/%m/%d")).days
                        message = f"It's been *~~{days_since_last_reset}~~* **0** days since {description.lower()}."
                        embed = discord.Embed(title=name, description=message)
                        await ctx.send(embed=embed)
                        new_reset = datetime.datetime.now().strftime("%Y/%m/%d")
                        newfile.write(f"{name.capitalize()}\t{new_reset}\t{creator_id}\t{description}\t{guild_id}\n")
                    reset = True
                else:
                    newfile.write(line)
            if not reset:
                await ctx.send(f"No counter with name **{to_reset.capitalize()}** was found.")

    # Edit the description of a counter
    @commands.command(usage="!editcounter <name> <description>",
                      description="Edits the description of a counter.",
                      help="!editcounter goose the last horrible goose incident",
                      aliases=["ec"])
    async def editcounter(self, ctx: commands.Context, to_edit: str = None, *, new_description: str = None) -> None:
        """
        Edit the description of a counter.

        :param ctx: The context.
        :param to_edit: The counter to edit.
        :param new_description: The new description of the counter.
        """
        if to_edit is None or new_description is None:
            await ctx.send("Please specify which counter you want to edit and the description you want to replace it with.")
            return
        with open('Day_counters.txt', 'r') as file:
            content = file.readlines()
        with open('Day_counters.txt', 'w') as newfile:
            edited = False
            ctx_guild_id = str(ctx.guild.id)
            for line in content:
                name, last_reset, creator_id, description, guild_id = line[:-1].split("\t")
                if to_edit.lower() == name.lower() and guild_id == ctx_guild_id:
                    if creator_id != str(ctx.message.author.id):
                        await ctx.send("You can only edit counters you created!")
                        newfile.write(line)
                    else:
                        days_since_last_reset = (datetime.datetime.now() - datetime.datetime.strptime(last_reset, "%Y/%m/%d")).days
                        message = f"It's been **{str(days_since_last_reset)}** days since {description.lower()}.\n\n"
                        message += "*was changed to*\n\n"
                        message += f"It's been **{str(days_since_last_reset)}** days since {new_description.lower()}."
                        embed = discord.Embed(title=f"Counter **{to_edit}** successfully updated", description=message)
                        await ctx.send(embed=embed)
                        newfile.write(f"{name.capitalize()}\t{last_reset}\t{creator_id}\t{new_description}\t{guild_id}\n")
                    edited = True
                else:
                    newfile.write(line)
            if not edited:
                await ctx.send(f"No counter with name **{to_edit.capitalize()}** was found.")

    @commands.command(usage="!showcounter <name>",
                      description="Displays the days that have passed sinc the last reset of a counter.",
                      help="!showcounter goose",
                      aliases=["printcounter", "displaycounter", "sc"])
    async def showcounter(self, ctx: commands.Context, name: str = None) -> None:
        """
        Display the counter.

        :param ctx: The context.
        :param name: The name of the counter.
        """
        if name is None:
            await ctx.send("Please specify which counter you want to display.")
            return
        embed = Daycounter.printcounter(name, str(ctx.guild.id))
        if embed is not None:
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"No counter with name **{name.capitalize()}** was found.")

    @commands.command(usage="!listcounters",
                      description="Gives an overview of all counters in this server",
                      help="!listcounters\nAll counters and the amount of days since their last reset are displayed.",
                      aliases=["listcounter", "showcounters", "lc"])
    async def listcounters(self, ctx: commands.Context) -> None:
        """
        Display an overview of all counters in this guild.

        :param ctx: The context.
        """
        message = ""
        with open('Day_counters.txt', 'r') as readfile:
            for line in readfile.readlines():
                counter_name, last_reset, _, description, guild_id = line[:-1].split("\t")
                if guild_id == str(ctx.guild.id):
                    days_since_last_reset = (datetime.datetime.now() - datetime.datetime.strptime(last_reset, "%Y/%m/%d")).days
                    message += f"**{counter_name}**: {days_since_last_reset} days since {description}.\n"
        if message == "":
            embed = discord.Embed(title="No counters to display.")
        else:
            embed = discord.Embed(title="Day counters", description=message)
        await ctx.send(embed=embed)


# Allows to connect cog to bot
async def setup(client):
    await client.add_cog(Daycounter(client))
