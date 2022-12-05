import discord
import datetime
import re

from io import DEFAULT_BUFFER_SIZE
from typing import Text
from discord.ext import commands, tasks

utc = datetime.timezone.utc

class Date(commands.Cog):
    
    def __init__(self, client):
        self.client = client
        self.check_loop.start()

    #@tasks.loop(time = datetime.time(hour=23, minute=0, tzinfo=utc))
    @tasks.loop(seconds=5)
    async def check_loop(self): 
        print("In the loop")
        with open('Examen_data.txt', 'r') as file:
            content = file.readlines()
        with open('Examen_data.txt', 'w') as newfile:
            for i in range(len(content)):
                split_line = content[i].split('\t')
                split_line[3] = split_line[3][:-1]
                date = split_line[0]
                date_time = datetime.datetime.strftime(date, "%d/%m/%Y")
                if date_time >= datetime.datetime.now().strftime("%d/%m/%Y"):
                    newfile.write(content[i])   

    @check_loop.before_loop
    async def before_printer(self):
        print('waiting...')
        await self.client.wait_until_ready()

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

    @commands.command(usage="!adddate <date> <name>", 
                      description="Add date to list of exams", 
                      help="!adddate 15/02/2022 a very hard exam\nDate should follow the format **DD/MM/YYYY**\nExam is allowed to contain **spaces**", 
                      aliases = ['ad'])
    async def adddate(self, ctx, date, *, name):
        if not re.match("[0-3][0-9]/[0-1][0-9]/[0-9]{4}", date):
            await ctx.send("Date has to be DD/MM/YYYY, try again.")
            return
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

    @commands.command(usage="!showdate <member>", 
                      description="Show current examdates", 
                      help="!showdate: Show all dates\n!showdate @member: Show all dates from certain member", 
                      aliases = ['sd'])
    async def showdate(self, ctx, member : discord.Member=None):
        with open('Examen_data.txt', 'r') as file:
            content = file.readlines()
        page = 1
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
                if len(message) > 2000:
                    embed = discord.Embed(title = "Examen Data " + str(page), description = message)
                    await ctx.send(embed = embed)
                    message = ''
                    page += 1
                message += "**__" + current_date + ":__**\n"
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
            embed = discord.Embed(title = "Examen Data " + str(page), description = message)
            await ctx.send(embed = embed)

    @commands.command(usage="!deletedate <date> <name>", 
                      description="Delete date from list of exams", 
                      help="!deletedate 15/02/2022 a very hard exam\nThe arguments have to be **the same arguments** as the ones in !adddate", 
                      aliases = ['dd'])
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
async def setup(client):
    await client.add_cog(Date(client))