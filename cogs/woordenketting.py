import discord
from discord.ext import commands

# Used for accents
import unicodedata


def lower_strip_accents(word):
    return (''.join(c for c in unicodedata.normalize('NFD', word) if unicodedata.category(c) != 'Mn')).lower()


class Woordenketting(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(usage="!addword <word>",
                      description="Add a word",
                      help="The word has to start with the last letter from the last word",
                      aliases=['aw'])
    async def add_word(self, ctx, *, entry=None):
        list = []
        # Eerste lijn is nu het thema
        with open('Woordenketting.txt', 'r') as txt:
            thema = str(txt.readline()[:-1]).upper()
            for word_user in txt.readlines():
                split_word = word_user.split('\t')
                list.append(str(split_word[0]))
            woord = list[-1]
            letter = list[-1][-1]
            last_user = split_word[1][:-1]
        # Vragen om laatste woord
        if entry is None:
            embed = discord.Embed(title=f'Woordenketting: {thema}', description=f'You need to find a word starting with `{letter}`, final letter of `{woord}`', colour=0x11806a)
            await ctx.send(embed=embed)
            return
        # Woord toevoegen
        with open('Woordenketting_users.txt', 'r') as user_file:
            with open('Woordenketting.txt', 'a') as txt:
                # Nieuwe user + juiste letter
                if str(ctx.message.author.id) != last_user and lower_strip_accents(str(entry[0])) == lower_strip_accents(letter):
                    # Check of entry niet in de lijst
                    if entry.lower() in list:
                        embed = discord.Embed(title=f'Woordenketting: {thema}', description=f'`{entry}` already in list!', colour=0xff0000)
                        await ctx.send(embed=embed)
                        return
                    elif lower_strip_accents(entry) == 'linx' or lower_strip_accents(entry) == 'lynx':
                        embed = discord.Embed(title=f'Woordenketting: {thema}', description=f'`{entry}` has NOT been added!', colour=0xff0000)
                        embed.add_field(name='Note', value='Do you really have to be that guy?')
                        await ctx.send(embed=embed)
                        return
                    with open('Woordenketting_users.txt', 'r') as user_file:
                        users = []
                        for user in user_file.readlines():
                            users.append(str(user[:-1]))
                        # Add id als het het eerste woord van die persoon is
                        if str(ctx.message.author.id) not in users:
                            with open('Woordenketting_users.txt', 'a') as user_file:
                                user_file.write(str(ctx.message.author.id) + '\n')
                    txt.write(entry.lower() + '\t' + str(ctx.message.author.id) + '\n')
                    embed = discord.Embed(title=f'Woordenketting: {thema}', description=f'`{entry}` has been added!', colour=0x11806a)
                    await ctx.send(embed=embed)
                # Geen nieuwe user
                elif str(ctx.message.author.id) == last_user:
                    embed = discord.Embed(title=f'Woordenketting: {thema}', description=f'You need to wait for someone else to submit a word!\n The last word was `{woord}`', colour=0xff0000)
                    await ctx.send(embed=embed)
                # Nieuwe user + verkeerde letter
                elif lower_strip_accents(str(entry[0])) != lower_strip_accents(letter) and str(ctx.message.author.id) != last_user:
                    embed = discord.Embed(title=f'Woordenketting: {thema}', description=f'Word should start with `{lower_strip_accents(letter)}`, final letter of `{woord}`', colour=0xff0000)
                    await ctx.send(embed=embed)

    @commands.command(usage="!delete_word",
                      description="Delete the last word",
                      help="This command will only execute when you are the last user",
                      aliases=['dw'])
    async def delete_word(self, ctx):
        ketting = []
        with open('Woordenketting.txt', 'r') as txt:
            thema = str(txt.readline()[:-1]).upper()
            for word_user in txt.readlines():
                ketting.append(str(word_user))
        last_word = ketting[-1].split('\t')[0]
        last_user = ketting[-1].split('\t')[1][:-1]
        # User is de laatste user of admin
        if str(ctx.message.author.id) == last_user or 656916865364525067 == ctx.message.author.id or 415176371736674304 == ctx.message.author.id:
            with open('Woordenketting.txt', 'w') as txt:
                txt.write(thema + '\n')
                for word_user in ketting[:-1]:
                    txt.write(word_user)
            embed = discord.Embed(title=f'Woordenketting: {thema}', description=f'`{last_word}` has been deleted!', colour=0xff0000)
            await ctx.send(embed=embed)
            return
        # User is andere user
        else:
            embed = discord.Embed(title=f'Woordenketting: {thema}', description='You do not have permission to delete this word!', colour=0xff0000)
            await ctx.send(embed=embed)

    @commands.command(usage="!edit <word>",
                      description="Replace the last word",
                      help="""!edit België: This will replace the last entry to België if the first letter is still the same.\n
                            The word will still count towards the wordcount of the user who submitted the original word""",)
    async def edit(self, ctx, nieuwe_entry=None):
        list = []
        ketting = []
        with open('Woordenketting.txt', 'r') as txt:
            thema = str(txt.readline()[:-1]).upper()
            for word_user in txt.readlines():
                split_word = word_user.split('\t')
                list.append(str(split_word[0]))
                ketting.append(str(word_user))
        last_word = ketting[-1].split('\t')[0]
        last_user = ketting[-1].split('\t')[1][:-1]
        # Vragen om laatste woord
        if nieuwe_entry is None:
            embed = discord.Embed(title=f'Woordenketting: {thema}', description=f'The last word that can be edited was `{last_word}`', colour=0x11806a)
            await ctx.send(embed=embed)
            return
        # Edit blijft hetzelfde
        if nieuwe_entry == last_word:
            embed = discord.Embed(title=f'Woordenketting: {thema}', description=f'What\'s the point of editing if you are going to put `{nieuwe_entry}` again?', colour=0xff0000)
            await ctx.send(embed=embed)
            return
        # Edit bevindt zich al in de lijst
        elif nieuwe_entry in list:
            embed = discord.Embed(title=f'Woordenketting: {thema}', description=f'`{nieuwe_entry}` already in list!\n The last word was `{last_word}`', colour=0xff0000)
            await ctx.send(embed=embed)
            return
        # Nieuwe edit
        else:
            ketting[-1] = nieuwe_entry
            # Edit start met juiste letter
            if lower_strip_accents(str(last_word[0])) == lower_strip_accents(str(nieuwe_entry[0])):
                with open('Woordenketting.txt', 'w') as txt:
                    txt.write(thema + '\n')
                    for woord in ketting[:-1]:
                        txt.write(woord.lower())
                    txt.write(nieuwe_entry + '\t' + last_user + '\n')
                embed = discord.Embed(title=f'Woordenketting: {thema}', description=f'`{str(last_word)}` has been replaced with `{nieuwe_entry}`', colour=0x11806a)
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title=f'Woordenketting: {thema}', description=f'Word should start with `{last_word[0]}`, first letter of `{last_word}`', colour=0xff0000)
                await ctx.send(embed=embed)

    @commands.command(usage="!show <letter>",
                      description="Show words in current list",
                      help="!show: Shows all words alphabetical\n!show a: Show all words starting with an a")
    async def show(self, ctx, first_letter=None):
        ketting = []
        message = ''
        page = 1
        if first_letter is not None:
            with open('Woordenketting.txt', 'r') as txt:
                thema = str(txt.readline()[:-1]).upper()
                for word in txt.readlines():
                    if word[0] == first_letter:
                        ketting.append(str(word[:-1]))
            ketting.sort()
            for word in ketting:
                split_word = word.split('\t')
                message += str(split_word[0]) + '\n'
                if len(message) > 2000:
                    embed = discord.Embed(title=f'Woordenketting: {thema} {str(page)}', description=message, colour=0x11806a)
                    await ctx.send(embed=embed)
                    message = ''
                    page += 1
            embed = discord.Embed(title=f'Woordenketting: {thema} {str(page)}', description=message, colour=0x11806a)
            await ctx.send(embed=embed)
        else:
            with open('Woordenketting.txt', 'r') as txt:
                thema = str(txt.readline()[:-1]).upper()
                for word in txt.readlines():
                    split_word = word.split('\t')
                    message += str(split_word[0]) + '\n'
                    if len(message) > 2000:
                        embed = discord.Embed(title=f'Woordenketting: {thema} {str(page)}', description=message, colour=0x11806a)
                        await ctx.send(embed=embed)
                        message = ''
                        page += 1
            embed = discord.Embed(title=f'Woordenketting: {thema} {str(page)}', description=message, colour=0x11806a)
            await ctx.send(embed=embed)

    @commands.command(usage="!stats <member>",
                      description="Show stats of current list",
                      help="!stats: Shows general stats\n!stats @member: Show stats for certain member")
    async def stats(self, ctx, member: discord.Member = None):
        number = 0
        number_user = 0
        if member is None:
            with open('Woordenketting.txt', 'r') as txt:
                thema = str(txt.readline()[:-1]).upper()
                for word_user in txt.readlines():
                    number += 1
            embed = discord.Embed(title=f'Woordenketting: {thema}', description=f'The list contains `{number}` words.', colour=0x11806a)
            await ctx.send(embed=embed)
        # Stats voor opgegeven member
        else:
            with open('Woordenketting.txt', 'r') as txt:
                thema = str(txt.readline()[:-1]).upper()
                for word_user in txt.readlines():
                    number += 1
                    user = word_user.split('\t')[1][:-1]
                    if user == str(member.id):
                        number_user += 1
            embed = discord.Embed(title=f'Woordenketting: {thema}', description=f'The list contains `{number}` words and `{str(member)[:-5]}` added `{number_user}` words.', colour=0x11806a)
            await ctx.send(embed=embed)


# Allows to connect cog to bot
async def setup(client):
    await client.add_cog(Woordenketting(client))
