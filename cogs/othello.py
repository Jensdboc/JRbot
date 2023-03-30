from othello_files.othello_board import Board
from othello_files.othello_human_agent import HumanAgent
from othello_files.othello_mcts_agent import MCTSAgent
from othello_files.othello_static_eval_agent import StaticEvalAgent

import discord
import numpy as np
from discord.ext import commands


class Othello(commands.Cog):

    def __init__(self, client):
        self.client = client

    global games
    games = []

    @commands.command(usage="!othello_start",
                      description="Start othello game",
                      help="https://nl.wikipedia.org/wiki/Reversi for more information",
                      aliases=['os'])
    async def othello_start(self, ctx):  # Show start screen, ask for input
        embed = discord.Embed(title='Othello', description="Calculating board...", color=ctx.author.color)
        message = await ctx.send(embed=embed)
        new_board = Board(ctx.author, message)
        for i in range(len(games)):
            if games[i].author == ctx.author:
                games[i] = new_board
        if new_board not in games:
            games.append(new_board)
        embed = discord.Embed(title='Othello', description=new_board.display(), color=ctx.author.color)
        await message.edit(embed=embed)

    @commands.command(usage="!othello_input <x> <y>",
                      description="Give coordinates for next input",
                      help="https://nl.wikipedia.org/wiki/Reversi for more information",
                      aliases=['oi'])
    async def othello_input(self, ctx, x, y):
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

                    embed = discord.Embed(title='Othello', description=games[index].display(), color=ctx.author.color)
                    await games[index].message.edit(embed=embed)

                    # What if player turns is right but doesn't have moves anymore
                    if new_board.game_finished():
                        embed = discord.Embed(title='Othello', description=games[index].display(), color=ctx.author.color)
                        await games[index].message.edit(embed=embed)

                        res = "Tie!"
                        count_white = sum(row.count('⬜') for row in board.board)
                        count_black = sum(row.count('⬛') for row in board.board)

                        if count_white > count_black:
                            res = f"You lose {count_black} vs {count_white}!"
                        elif count_black > count_white:
                            res = f"You win {count_black} vs {count_white}!"
                        await ctx.send(res)
                        return

                    # Bots turn
                    newer_board = simulate(MCTSAgent('white', max_depth=2, rollouts=100, base_agent=StaticEvalAgent('white'), uct_const=1 / np.sqrt(2)), HumanAgent('black'), new_board, coords)
                    if isinstance(newer_board, Board):
                        games[index] = newer_board
                    else:
                        embed = discord.Embed(title='Othello', description=games[index].display(), color=ctx.author.color)
                        await games[index].message.edit(embed=embed)
                        await ctx.send(newer_board)
                        return

                    embed = discord.Embed(title='Othello', description=games[index].display(), color=ctx.author.color)
                    await games[index].message.edit(embed=embed)

                    while len(games[index].legal_moves()) == 0:
                        games[index].turn = 'white'
                        newer_board = simulate(MCTSAgent('white', max_depth=2, rollouts=100, base_agent=StaticEvalAgent('white'), uct_const=1 / np.sqrt(2)), HumanAgent('black'), games[index], coords)
                        if isinstance(newer_board, Board):
                            games[index] = newer_board
                            newer_board.turn = 'black'
                            embed = discord.Embed(title='Othello', description=games[index].display(), color=ctx.author.color)
                            await games[index].message.edit(embed=embed)
                        else:
                            # Bot kan niet zetten, spel is gedaan
                            if games[index].game_finished():
                                embed = discord.Embed(title='Othello', description=games[index].display(), color=ctx.author.color)
                                await games[index].message.edit(embed=embed)

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

    @commands.command(usage="!othello_clear",
                      description="Remove all current games",
                      help="https://nl.wikipedia.org/wiki/Reversi for more information",
                      aliases=['oc'])
    async def othello_clear(self, ctx):
        games = []
        await ctx.send("All games have been succesfully cleared!")


def simulate(white, black, board, coords):

    player = white if board.turn == 'white' else black
    move = player.move(board, coords)

    if isinstance(move, str):
        return move

    if len(move) == 0:
        board.turn = 'black' if board.turn == 'white' else 'white'
        if player == white:
            return "Bot didn't find a place to put his stuff! Your turn now :)"
        else:
            return "Player didn't find a place to put his stuff!"
    else:
        if board.turn == 'white':
            board.board[move[0]][move[1]] = '⬜'
            board.turn_token(move, '⬜', '⬛')
            board.white_played.append(move[0] * 8 + move[1])
            board.turn = 'black'
        else:
            board.board[move[0]][move[1]] = '⬛'
            board.turn_token(move, '⬛', '⬜')
            board.black_played.append(move[0] * 8 + move[1])
            board.turn = 'white'
    return board


# Allows to connect cog to bot
async def setup(client):
    await client.add_cog(Othello(client))
