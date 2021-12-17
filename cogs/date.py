from io import DEFAULT_BUFFER_SIZE
from typing import Text
import discord
from discord.ext import commands

class Date(commands.Cog):
    
    def __init__(self, client):
        self.client = client
    
    def sort():
        with open('Examen_data.txt', 'r') as file:
            content = file.readlines()
        text = []
        dates = []
        index = 0
        for line in content:
            split_line = line.split('\t')
            date = split_line[0].split('/')
            date.append(index)
            text.append(line)
            dates.append(date)
            index += 1
        dates.sort(key=lambda x:x[0])
        dates.sort(key=lambda x:x[1])
        dates.sort(key=lambda x:x[2])
        with open('Examen_data.txt', 'w') as newfile:
            for index in dates:
                newfile.write(text[index[3]])
        
    @commands.command(aliases = ['ad'])
    async def adddate(self, ctx, date, *, name):
        with open('Examen_data.txt', 'a') as file:
            file.write(date + '\t')
            split_name = name.split(' ')
            for i in range(len(split_name)):
                file.write(split_name[i])
                if i != len(split_name) - 1:
                    file.write(' ')
                else:
                    file.write('\t')
            file.write(ctx.message.author.name + '\t' + str(ctx.message.author.id) + '\n')
        Date.sort()
        await ctx.send("Date added!")

    @commands.command(aliases = ['sd'])
    async def showdate(self, ctx, member : discord.Member=None):
        with open('Examen_data.txt', 'r') as file:
            content = file.readlines()
        count = 0
        message = ''
        Date.sort()
        if len(content) == 0:
            await ctx.send("No dates added yet!")
            return
        for line in content: 
            split_line = line.split('\t')
            split_line[3] = split_line[3][:-1]
            if member == None:
                count += 1
                line = split_line[2] + " heeft examen " + split_line[1] + " op " + split_line[0] + '.'
                message += line
                message += '\n'
            elif str(split_line[3]) == str(member.id):
                count += 1
                line = split_line[2] + " heeft examen " + split_line[1] + " op " + split_line[0] + '.'
                message += line
                message += '\n'
        if count == 0:
            await ctx.send("No such user found!")
        else:
            embed = discord.Embed(title = "Examen Data", description = message)
            await ctx.send(embed = embed)

    @commands.command(aliases = ['sdd'])
    async def showdatedate(self, ctx, member : discord.Member=None):
        with open('Examen_data.txt', 'r') as file:
            content = file.readlines()
        count = 0
        message = ''
        current_date = ''
        Date.sort()
        if len(content) == 0:
            await ctx.send("No dates added yet!")
            return
        for line in content: 
            split_line = line.split('\t')
            split_line[3] = split_line[3][:-1]
            if current_date != split_line[0]:
                current_date = split_line[0]
                message += current_date + ":\n"
            if member == None:
                count += 1
                line = split_line[2] + " heeft examen " + split_line[1] + '.'
                message += line
                message += '\n'
            elif str(split_line[3]) == str(member.id):
                count += 1
                line = split_line[2] + " heeft examen " + split_line[1] + '.'
                message += line
                message += '\n'
        if count == 0:
            await ctx.send("No such user found!")
        else:
            embed = discord.Embed(title = "Examen Data", description = message)
            await ctx.send(embed = embed)

    @commands.command(aliases = ['dd'])
    async def deletedate(self, ctx, date, *, name):
        with open('Examen_data.txt', 'r') as file:
            content = file.readlines()
        with open('Examen_data.txt', 'w') as newfile:
            deleted = False
            for i in range(len(content)):
                split_line = content[i].split('\t')
                split_line[3] = split_line[3][:-1]
                if split_line[0] == date and split_line[1] == name and split_line[2] == ctx.message.author.name:
                    deleted = True
                    await ctx.send("Date has been deleted!")
                elif split_line[0] == date and split_line[1] == name:
                    deleted = True
                    await ctx.send("You are not allowed to deleted dates from others!")
                    newfile.write(content[i]) 
                else:
                    newfile.write(content[i])   
            if not deleted:
                await ctx.send("No such date has been found!")

#Allows to connect cog to bot    
def setup(client):
    client.add_cog(Date(client))