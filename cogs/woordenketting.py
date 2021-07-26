import discord
from discord.ext import commands

#****************************#
#User commands woordenketting#
#****************************#  

class Woordenketting(commands.Cog):
    
    def __init__(self, client):
        self.client = client

    @commands.command(aliases = ['d'])
    async def dier(self, ctx,*, dier=None):
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
        if dier.lower() in list:
            embed =  discord.Embed(title='Woordenketting', description='`' + dier + '`' + ' already in list!', colour=0xff0000)
            await ctx.send(embed=embed)
            return 
        elif dier.lower() == 'linx' or dier.lower() == 'lynx':
            embed =  discord.Embed(title='Woordenketting', description='`' + dier + '`' + ' has NOT been added!', colour=0xff0000)
            embed.add_field(name='Note', value='Do you really have to be that guy?')
            await ctx.send(embed=embed)
            return 
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
                        embed =  discord.Embed(title='Woordenketting', description='Animal should start with ' + '`' + letter + '`' + ', final letter of ' + '`' + woord + '`', colour=0xff0000)
                        await ctx.send(embed=embed)
                    else:
                        embed =  discord.Embed(title='Woordenketting', description='You need to wait for someone else to submit an animal!', colour=0xff0000)
                        await ctx.send(embed=embed)        
        
    @commands.command()
    async def count(self, ctx):
        number = 0
        with open('Dieren.txt','r') as txt: 
            for word in txt.readlines():
                number += 1
        embed = discord.Embed(title='Woordenketting', description='The list contains ' + '`' + f'{number}' + '`' + ' animals so far.', colour=0x11806a)
        await ctx.send(embed=embed)

    @commands.command()
    async def edit(self, ctx, nieuw_dier):
        dieren = []
        with open('Dieren.txt','r') as txt: 
            for word in txt.readlines():
                dieren.append(str(word[:-1]))
        if nieuw_dier in dieren:
            embed = discord.Embed(title='Woordenketting', description='`' + nieuw_dier + '`' + ' already in list!', colour=0xff0000)
            await ctx.send(embed=embed)
            return
        else:
            vorig_dier = dieren[-1] 
            dieren[-1] = nieuw_dier
            if vorig_dier[0] == nieuw_dier[0]:
                with open('Dieren.txt','w') as txt: 
                    for woord in dieren:
                        txt.write(woord.lower() + '\n') 
                embed = discord.Embed(title='Woordenketting', description= '`' + str(vorig_dier) + '`' + ' has been replaced with ' + '`' + nieuw_dier + '`', colour=0x11806a)
                await ctx.send(embed=embed)
            else:
                embed =  discord.Embed(title='Woordenketting', description='Animal should start with ' + '`' + vorig_dier[0] + '`' + ', first letter of ' + '`' + vorig_dier + '`', colour=0xff0000)
                await ctx.send(embed=embed)

#Allows to connect cog to bot    
def setup(client):
    client.add_cog(Woordenketting(client))