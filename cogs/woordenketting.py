import discord
from discord.ext import commands

#****************************#
#User commands woordenketting#
#****************************#  

class Woordenketting(commands.Cog):
    
    def __init__(self, client):
        self.client = client

    @commands.command(aliases = ['aw'])
    async def add_word(self, ctx, *, entry=None):
        list = []
        # Eerste lijn is nu het thema
        with open('Woordenketting.txt','r') as txt: 
            for word in txt.readlines():
                list.append(str(word[:-1]))
                woord = list[-1] 
                print(woord)
                letter = list[-1][-1]
        thema = list[0].upper()
        # Vragen om laatste woord
        if entry == None:
            embed =  discord.Embed(title='Woordenketting: ' + thema, description='You need to find a word starting with ' + '`' + letter + '`' + ', final letter of ' + '`' + woord + '`', colour=0x11806a)
            await ctx.send(embed=embed)
            return
        # Woord toevoegen
        with open('Last_user.txt', 'r') as user_file:
            for user in user_file.readlines():
                with open('Woordenketting.txt','a') as txt:
                    # Nieuwe user + juiste letter
                    if str(ctx.message.author.id) != user and str(entry[0]).lower() == letter.lower():
                        # Check of entry niet in de lijst
                        if entry.lower() in list:
                            embed =  discord.Embed(title='Woordenketting: ' + thema, description='`' + entry + '`' + ' already in list!', colour=0xff0000)
                            await ctx.send(embed=embed)
                            return 
                        elif entry.lower() == 'linx' or entry.lower() == 'lynx':
                            embed =  discord.Embed(title='Woordenketting: ' + thema, description='`' + entry + '`' + ' has NOT been added!', colour=0xff0000)
                            embed.add_field(name='Note', value='Do you really have to be that guy?')
                            await ctx.send(embed=embed)
                            return 
                        with open('Last_user.txt', 'a') as user_file:
                            user_file.truncate(0)
                            user_file.write(str(ctx.message.author.id)) 
                            txt.write(entry.lower() + '\n')
                            embed =  discord.Embed(title='Woordenketting: ' + thema, description='`' + entry + '`' + ' has been added!', colour=0x11806a)
                            await ctx.send(embed=embed)
                    # Geen nieuwe user
                    elif str(ctx.message.author.id) == user:
                        embed =  discord.Embed(title='Woordenketting: ' + thema, description='You need to wait for someone else to submit a word!\n The last word was ' + '`' + woord + '`', colour=0xff0000)
                        await ctx.send(embed=embed)   
                    # Nieuwe user + verkeerde letter
                    elif str(entry[0]).lower() != letter.lower() and str(ctx.message.author.id) != user:
                        embed =  discord.Embed(title='Woordenketting: ' + thema, description='Word should start with ' + '`' + letter + '`' + ', final letter of ' + '`' + woord + '`', colour=0xff0000)
                        await ctx.send(embed=embed)    

    @commands.command()
    async def count(self, ctx):
        number = 0
        with open('Woordenketting.txt','r') as txt: 
            for word in txt.readlines():
                number += 1
        embed = discord.Embed(title='Woordenketting: ', description='The list contains ' + '`' + f'{number}' + '`' + ' words so far.', colour=0x11806a)
        await ctx.send(embed=embed)

    @commands.command()
    async def edit(self, ctx, nieuwe_entry):
        ketting = []
        with open('Woordenketting.txt','r') as txt: 
            for word in txt.readlines():
                ketting.append(str(word[:-1]))
        thema = ketting[0].upper()
        vorig_dier = ketting[-1]
        # Edit blijft hetzelfde
        if nieuwe_entry == vorig_dier:
            embed = discord.Embed(title='Woordenketting: ' + thema, description='What\'s the point of editing if you are going to put ' + '`' + nieuwe_entry + '`' + ' again?', colour=0xff0000)
            await ctx.send(embed=embed)
            return   
        # Edit bevindt zich al in de lijst
        elif nieuwe_entry in ketting:
            embed = discord.Embed(title='Woordenketting: ' + thema, description='`' + nieuwe_entry + '`' + ' already in list!\n The last word was ' + '`' + vorig_dier + '`', colour=0xff0000)
            await ctx.send(embed=embed)
            return
        # Nieuwe edit
        else:
            ketting[-1] = nieuwe_entry
            # Edit start met juiste letter
            if vorig_dier[0] == nieuwe_entry[0]:
                with open('Woordenketting.txt','w') as txt: 
                    for woord in ketting:
                        txt.write(woord.lower() + '\n') 
                embed = discord.Embed(title='Woordenketting: ' + thema, description= '`' + str(vorig_dier) + '`' + ' has been replaced with ' + '`' + nieuwe_entry + '`', colour=0x11806a)
                await ctx.send(embed=embed)
            else:
                embed =  discord.Embed(title='Woordenketting: ' + thema, description='Word should start with ' + '`' + vorig_dier[0] + '`' + ', first letter of ' + '`' + vorig_dier + '`', colour=0xff0000)
                await ctx.send(embed=embed)

    @commands.command()
    async def show(self, ctx, first_letter=None):
        ketting = []
        message = ''
        page = 1
        if first_letter != None:
            with open('Woordenketting.txt','r') as txt:
                thema = str(txt.readline()[:-1]).upper() 
                for word in txt.readlines():
                    if word[0] == first_letter:
                        ketting.append(str(word[:-1]))
            ketting.sort()
            for word in ketting:
                message += str(word) + '\n'
                if len(message) > 2000:
                    embed =  discord.Embed(title='Woordenketting: ' + thema + ' ' + str(page), description=message, colour=0x11806a)
                    await ctx.send(embed=embed)
                    message = ''
                    page += 1
            embed = discord.Embed(title='Woordenketting: ' + thema + ' ' + str(page), description=message, colour=0x11806a)
            await ctx.send(embed=embed)
        else:
            with open('Woordenketting.txt','r') as txt: 
                thema = str(txt.readline()[:-1]).upper()
                for word in txt.readlines():
                    message += str(word) 
                    if len(message) > 2000:
                        embed =  discord.Embed(title='Woordenketting: ' + thema + ' ' + str(page), description=message, colour=0x11806a)
                        await ctx.send(embed=embed)
                        message = ''
                        page += 1
            embed = discord.Embed(title='Woordenketting: ' + thema + ' ' + str(page), description=message, colour=0x11806a)
            await ctx.send(embed=embed)

#Allows to connect cog to bot    
def setup(client):
    client.add_cog(Woordenketting(client))