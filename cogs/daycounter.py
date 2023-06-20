import datetime
import discord
from discord.ext import commands

utc = datetime.timezone.utc

class Daycounter(commands.Cog):

    def __init__(self, client):
        self.client = client

    # Creates an embed message for a counter
    def printcounter(counter_name):
        with open('Day_counters.txt', 'r') as file:
            content = file.readlines()
        for line in content:
            name, last_reset, _, description = line.split("\t")
            if name == counter_name:
                days_since_last_reset = (datetime.datetime.now() - datetime.datetime.strptime(last_reset, "%d/%m/%y")).days
                message = "It's been **" + str(days_since_last_reset) + "** days since " + description[:-1] + "."
                embed = discord.Embed(title=name.capitalize(), description=message)
                return embed
        
        return None

    # Creates a counter and adds it to the file
    @commands.command()
    async def createcounter(self, ctx, name, *, description):
        with open('Day_counters.txt', 'r') as readfile:
            for line in readfile.readlines():
                counter_name, _, _, _ = line.split("\t")
                if name == counter_name:
                    await ctx.send(f"There already exists a counter with the name **{name}**. Please pick a new name or delete the previous one.")
                    return
        with open('Day_counters.txt', 'a') as file:
            if not description:
                await ctx.send("Please enter a name and description for your counter.")
                return
            else:
                last_reset = datetime.datetime.now().strftime("%d/%m/%y")
                creator_id = str(ctx.message.author.id)
                counter_entry = name + "\t" + str(last_reset) + "\t" + creator_id + "\t" + description + "\n"
                file.write(counter_entry)

        embed = Daycounter.printcounter(name)
        if embed is not None:
            await ctx.send(embed=embed)
                
    # Deletes a counter from the file
    @commands.command()
    async def deletecounter(self, ctx, to_delete):
        with open('Day_counters.txt', 'r') as file:
            content = file.readlines()
        with open('Day_counters.txt', 'w') as newfile:
            deleted = False
            for line in content:
                name, _, creator_id, _ = line.split("\t")
                if to_delete == name:
                    if creator_id != str(ctx.message.author.id):
                        await ctx.send("You can only delete counters you created!")
                        newfile.write(line) 
                    else:
                        await ctx.send(f"Counter **{to_delete}** has been succesfully deleted.")
                    deleted = True
                else:
                    newfile.write(line)
            
            if not deleted:
                await ctx.send(f"No counter with name **{to_delete}** was found.")

    
    @commands.command()
    async def resetcounter(self, ctx, name):
        pass

    @commands.command()
    async def showcounter(self, ctx, name):
        embed = Daycounter.printcounter(name)
        if embed is not None:
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"No counter with name **{name}** was found.")

    @commands.command()
    async def listcounters(self, ctx):
        pass

# Allows to connect cog to bot
async def setup(client):
    await client.add_cog(Daycounter(client))