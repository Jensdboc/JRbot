import os
import pickle
from typing import List, Union
from PIL import Image

import discord
from discord.ext import commands

from poker.game import Game


class Games:
    def __init__(self):
        self.games = []

    def add_game(self, game: Game):
        self.games.append(game)

    def remove_game(self, game: Game):
        self.games.remove(game)


def write_poker_games_to_file(output_file: str, games: Games) -> None:
    """
    Write a Games object to a pickle file.

    :param output_file: The output file.
    :param games: The games object.
    """
    with open(output_file, 'wb') as file:
        pickle.dump(games, file)


def load_poker_games_from_file(input_file: str) -> Games:
    """
    Read a Games object from a pickle file.

    :param input_file: The input file.

    :return: The Games object.
    """
    with open(input_file, 'rb') as file:
        games = pickle.load(file)

    return games


class Poker(commands.Cog):
    """
    This class contains the filename in which the data is stored and the commands.
    """
    def __init__(self, client):
        self.client = client
        self.filename = 'poker.pkl'

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """
        Create the file in which the data will be stored.
        """
        write_poker_games_to_file(self.filename, Games())
        print(f"{self.filename} created")

    @commands.command(usage="!poker small_blind start_amount",
                      description="Start a poker game and wait for players to join.",
                      help="!poker 5 1000")
    async def poker(self, ctx: discord.ext.commands.context.Context, small_blind: int = 5, start_amount: int = 1000) -> None:
        games_obj = load_poker_games_from_file(self.filename)

        for game in games_obj.games:
            if (ctx.author.id, ctx.author.display_name) in list(map(lambda x: (x.player_id, x.name), game.players)):
                ctx.reply("You are already in a game!")
                return

        if small_blind <= 0:
            ctx.reply("The small blind has to be bigger than 0!")
            return
        if small_blind > start_amount / 20:
            ctx.reply(f"The max small blind for a start amount of {start_amount} is {start_amount / 20}!")
            return
        if start_amount < 100:
            ctx.reply("The start amount has to be higher than 100!")
            return

        poker_start_embed = discord.Embed(title="A poker game has started!", description=f"Current players: \n>{ctx.author.display_name}")
        poker_start_message = await ctx.send(embed=poker_start_embed)

        new_game = Game(ctx.author, small_blind, start_amount, poker_start_message.id)
        games_obj.add_game(new_game)
        write_poker_games_to_file(self.filename, games_obj)

        await poker_start_message.add_reaction('✋')
        await poker_start_message.add_reaction('▶')

    @commands.Cog.listener("on_reaction_add")
    async def on_reaction_add_poker(self, reaction: discord.Reaction, user: Union[discord.Member, discord.User]):
        if user.bot:
            return
        current_game = None
        games_obj: Games = load_poker_games_from_file(self.filename)
        filtered_list_of_games: List[Game] = list(filter(lambda game: reaction.message.id == game.poker_start_message_id, games_obj.games))
        if len(filtered_list_of_games) > 0:
            current_game = filtered_list_of_games[0]

        if reaction.emoji == '✋' and current_game is not None and len(current_game.players) < 10:
            embed = reaction.message.embeds[0]
            embed.description = current_game.add_player(user)
            await reaction.message.edit(embed=embed)
            write_poker_games_to_file(self.filename, games_obj)
        elif reaction.emoji == '▶' and current_game is not None and user.id == current_game.players[0].player_id and 1 <= len(current_game.players) <= 10:

            current_game.on_game_start()
            write_poker_games_to_file(self.filename, games_obj)
            await reaction.message.delete()

            try:
                for player in current_game.players:

                    # poker_background = Image.new("RGB", (800, 400), "white")
                    # poker_png.save("data_pictures/poker/poker_background800x600.png")
                    poker_background = Image.open("data_pictures/poker/poker_background800x600.png")

                    player_cards = []
                    for card in player.cards:
                        card_value = card.get_card_integer_value() if card.value not in ['jack', 'queen', 'king', 'ace'] else card.value
                        player_card_image = Image.open(os.path.dirname(os.path.abspath(__file__)) + f'/../data_pictures/playing_cards/{card_value}_{card.card_suit}.png')
                        card_size = tuple(int(ti / 4) for ti in player_card_image.size)
                        player_card_image = player_card_image.resize(card_size)
                        player_cards.append(player_card_image)

                    poker_background.paste(player_cards[0], (30, 30), player_cards[0])
                    poker_background.paste(player_cards[1], (30 + card_size[0], 30), player_cards[1])
                    poker_background.save("data_pictures/temp/final_image.png")

                    user = await self.client.fetch_user(player.player_id)
                    await user.send(file=discord.File("data_pictures/temp/final_image.png"))
                    poker_background.close()
                    os.remove("data_pictures/temp/final_image.png")
            except Exception as e:
                print(e)

    @commands.Cog.listener("on_reaction_remove")
    async def on_reaction_remove_poker(self, reaction: discord.Reaction, user: Union[discord.Member, discord.User]):
        if user.bot:
            return
        current_game = None
        games_obj = load_poker_games_from_file(self.filename)
        filtered_list_of_games: List[Game] = list(filter(lambda game: reaction.message.id == game.poker_start_message_id, games_obj.games))
        if len(filtered_list_of_games) > 0:
            current_game = filtered_list_of_games[0]

        if reaction.emoji == '✋' and current_game is not None:
            if len(current_game.players) == 1 and user.id == current_game.players[0].player_id:
                games_obj.remove_game(current_game)
                write_poker_games_to_file(self.filename, games_obj)
                await reaction.message.delete()
                return

            embed = reaction.message.embeds[0]
            embed.description = current_game.remove_player(user)
            await reaction.message.edit(embed=embed)
            write_poker_games_to_file(self.filename, games_obj)

    async def betting_round1(self, current_game: Game, channels: List[discord.channel.TextChannel]):
        while len(set(filter(lambda bet: bet != -1, list(map(lambda x: x.current_bet, current_game.players))))) != 1:
            await channels[current_game.current_player_index].send('It is your turn!')


async def setup(client):
    await client.add_cog(Poker(client))