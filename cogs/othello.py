from re import A
import discord
from discord.ext import commands

import os
import sys

from discord.flags import MessageFlags
from othello_board import Board
fpath = os.path.join(os.path.dirname(__file__), 'othello_main')
sys.path.append(fpath)
from othello_main import simulate
fpath = os.path.join(os.path.dirname(__file__), 'othello_human_agent')
sys.path.append(fpath)
from othello_human_agent import *
fpath = os.path.join(os.path.dirname(__file__), 'othello_mcts_agent')
sys.path.append(fpath)
from othello_mcts_agent import *
fpath = os.path.join(os.path.dirname(__file__), 'othello_static_eval_agent')
sys.path.append(fpath)
from othello_static_eval_agent import *
fpath = os.path.join(os.path.dirname(__file__), 'othello_board')
sys.path.append(fpath)
from othello_board import *
#fpath = os.path.join(os.path.dirname(__file__), 'othello_random_agent')
#sys.path.append(fpath)
#from othello_random_agent import *


class Othello(commands.Cog):

    def __init__(self, client):
        self.client = client
    
    global games
    games = []

    @commands.command(aliases = ['os'])
    async def othello_start(self, ctx): #Show start screen, ask for input
        embed =  discord.Embed(title='Othello', description= "Calculating board...", color = ctx.author.color)
        message = await ctx.send(embed=embed)
        new_board = Board(ctx.author, message)
        for i in range(len(games)):
            if games[i].author == ctx.author:
                games[i] = new_board
        if new_board not in games:
            games.append(new_board)
        embed =  discord.Embed(title='Othello', description= new_board.display(), color = ctx.author.color)
        await message.edit(embed=embed) 

    @commands.command(aliases = ['oi']) 
    async def othello_input(self, ctx, x, y):
        for i in games:
            print(i.author)
            print(i.message)
        await ctx.message.delete() 
        for index, board in enumerate(games):
            if board.author == ctx.author:
                if not board.game_finished():
                    coords = [int(x), int(y)]
                    # Players turn
                    new_board = simulate(MCTSAgent('white', max_depth=2, rollouts=100, base_agent=StaticEvalAgent('white'), uct_const=1 / np.sqrt(2)), HumanAgent('black'), board, coords)
                    if isinstance(new_board, Board):
                        games[index] = new_board 
                    else:
                        await ctx.send(new_board)
                        return

                    embed =  discord.Embed(title='Othello', description= games[index].display(), color = ctx.author.color)       
                    await games[index].message.edit(embed = embed) 
                    print('Players turn ended')

                    # What if player turns is right but doesn't have moves anymore
                    if new_board.game_finished():
                        print('Game finished 1')
                        embed =  discord.Embed(title='Othello', description= games[index].display(), color = ctx.author.color)       
                        await games[index].message.edit(embed = embed) 

                        res = "Tie!"
                        count_white = sum(row.count('⬜') for row in board.board)
                        count_black = sum(row.count('⬛') for row in board.board)

                        if count_white > count_black:
                            res = f"You lose {count_black} vs {count_white}!"
                        elif count_black > count_white:
                            res = f"You win {count_black} vs {count_white}!"
                        await ctx.send(res)
                        return
                    
                    #Bots turn
                    newer_board = simulate(MCTSAgent('white', max_depth=2, rollouts=100, base_agent=StaticEvalAgent('white'), uct_const=1 / np.sqrt(2)), HumanAgent('black'), new_board, coords)
                    if isinstance(newer_board, Board):
                        games[index] = newer_board 
                    else:
                        embed =  discord.Embed(title='Othello', description= games[index].display(), color = ctx.author.color)       
                        await games[index].message.edit(embed = embed) 
                        await ctx.send(newer_board)  
                        return

                    print('Bots turn ended')
                    embed =  discord.Embed(title='Othello', description= games[index].display(), color = ctx.author.color)       
                    await games[index].message.edit(embed = embed) 

                    i = 0
                    print(games[index])
                    while len(games[index].legal_moves()) == 0:
                        games[index].turn = 'white'
                        newer_board = simulate(MCTSAgent('white', max_depth=2, rollouts=100, base_agent=StaticEvalAgent('white'), uct_const=1 / np.sqrt(2)), HumanAgent('black'), games[index], coords)
                        print(newer_board)
                        if isinstance(newer_board, Board):
                            print('Bots turn ended: ' + str(i))
                            games[index] = newer_board
                            newer_board.turn = 'black'
                            embed =  discord.Embed(title='Othello', description= games[index].display(), color = ctx.author.color)       
                            await games[index].message.edit(embed = embed) 
                        else:
                            # Bot kan niet zetten, spel is gedaan
                            if games[index].game_finished():
                                print('Game finished 2')
                                embed =  discord.Embed(title='Othello', description= games[index].display(), color = ctx.author.color)       
                                await games[index].message.edit(embed = embed) 

                                res = "Tie!"
                                count_white = sum(row.count('⬜') for row in board.board)
                                count_black = sum(row.count('⬛') for row in board.board)

                                if count_white > count_black:
                                    res = f"You lose {count_black} vs {count_white}!"
                                elif count_black > count_white:
                                    res = f"You win {count_black} vs {count_white}!"
                                await ctx.send(res)
                                return
                            else:
                                print('Player can move now')
                                await ctx.send(newer_board)
                                return
                    return
                else:
                    res = "Tie!"
                    count_white = sum(row.count('⬜') for row in board.board)
                    count_black = sum(row.count('⬛') for row in board.board)

                    if count_white > count_black:
                        res = f"You lose {count_black} vs {count_white}!"
                    elif count_black > count_white:
                        res = f"You win {count_black} vs {count_white}!"
                    await ctx.send(res)
                    return
        await ctx.send("No board found!")         
    
    @commands.command(aliases = ['oc']) 
    async def othello_clear(self, ctx):
        games = []
        await ctx.send("All games have been succesfully cleared!")
        
#Allows to connect cog to bot    
def setup(client):
    client.add_cog(Othello(client))