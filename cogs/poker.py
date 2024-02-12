import os
import pickle
import traceback
from typing import List, Union

from PIL import Image, ImageDraw, ImageFont

import discord
from discord.ext import commands

from poker.constants import cross_places
from poker.draw import create_avatars_for_player, draw_cross, draw_text_on_image, draw_player_action_on_image
from poker.game import Game, Player
from poker.utils import contains_number

last_messages_to_players = []


class RaiseAmount(discord.ui.Modal, title='raise_amount'):
    def __init__(self, current_game: Game, current_player: Player, font_path, client, filename, games_obj, **kwargs):
        super().__init__(**kwargs)

        self.current_game = current_game
        self.current_player = current_player
        self.font_path = font_path
        self.client = client
        self.filename = filename
        self.games_obj = games_obj

    rai = discord.ui.TextInput(label="raise", style=discord.TextStyle.short, placeholder="Provide your bet:")

    async def on_submit(self, interaction: discord.Interaction):
        if contains_number(self.rai.value) and self.current_game.raise_lower_bound <= int(self.rai.value):
            self.current_game.raise_func(int(self.rai.value))

            for index, player in enumerate(self.current_game.players):
                player_image = Image.open(f'data_pictures/poker/message_{player.player_id}.png')
                if player.player_id != self.current_player.player_id:
                    draw_player_action_on_image(player_image, self.font_path, f'{self.current_player.name} raised to {self.current_player.current_bet}.')
                else:
                    draw_player_action_on_image(player_image, self.font_path, f'You raised to {self.current_player.current_bet}.')

                player_image.save(f'data_pictures/poker/message_action_{player.player_id}.png')
                player_image.close()

                discord_user = await self.client.fetch_user(player.player_id)
                await last_messages_to_players[index].delete()
                player_message = await discord_user.send(file=discord.File(f"data_pictures/poker/message_action_{player.player_id}.png"),
                                                         view=ButtonsMenu(self.filename, self.current_game, player.player_id, self.client, self.font_path))
                last_messages_to_players[index] = player_message

            write_poker_games_to_file(self.filename, self.games_obj)

        elif contains_number(self.rai.value):
            await interaction.response.send_message(f'You must raise by more than {self.current_game.raise_lower_bound} credits!', ephemeral=True)
        else:
            await interaction.response.send_message('This value has to be a number!', ephemeral=True)

        await interaction.response.defer()

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        # Make sure we know what the error actually is
        traceback.print_exception(type(error), error, error.__traceback__)


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


async def display_player_cards_and_avatars(filename, current_game, poker_background, client, font_path):
    for player in current_game.players:
        player_background = poker_background.copy()

        for index, card in enumerate(player.cards):
            card_value = card.get_card_integer_value() if card.value not in ['jack', 'queen', 'king', 'ace'] else card.value
            player_card_image = Image.open(f'data_pictures/playing_cards/{card_value}_{card.card_suit}.png')
            player_card_image = player_card_image.resize((72, 85))
            player_background.paste(player_card_image, (198 + index * player_card_image.size[0], 242), player_card_image)

        player_background = await create_avatars_for_player(client, player, current_game, player_background)

        player_background.save(f"data_pictures/poker/message_{player.player_id}.png")

        discord_user = await client.fetch_user(player.player_id)
        player_message = await discord_user.send(file=discord.File(f"data_pictures/poker/message_{player.player_id}.png"), view=ButtonsMenu(filename, current_game, player.player_id, client, font_path))
        last_messages_to_players.append(player_message)
        player_background.close()


class Poker(commands.Cog):
    """
    This class contains the filename in which the data is stored and the commands.
    """
    def __init__(self, client):
        self.client = client
        self.filename = 'poker.pkl'
        self.font_path = "data/cowboy-junk.ttf"

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
    async def poker(self, ctx: commands.Context, small_blind: int = 5, start_amount: int = 1000) -> None:
        games_obj = load_poker_games_from_file(self.filename)

        for game in games_obj.games:
            if (ctx.author.id, ctx.author.display_name) in list(map(lambda x: (x.player_id, x.name), game.players)):
                await ctx.reply("You are already in a game!")
                return

        if small_blind <= 0 or small_blind > 500000:
            await ctx.reply("The small blind must be greater than 0 and less than 500000!")
            return

        if start_amount < 100 or start_amount > 10000000:
            await ctx.reply("The start amount must be greater than 100 and less than 10000000!")
            return

        if small_blind > start_amount / 20:
            await ctx.reply(f"The max small blind for a start amount of {start_amount} is {start_amount / 20}!")
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
        elif reaction.emoji == '▶' and current_game is not None and user.id == current_game.players[0].player_id and 2 <= len(current_game.players) <= 10:

            current_game.on_game_start()
            write_poker_games_to_file(self.filename, games_obj)
            await reaction.message.delete()

            # Display general stats
            poker_background = Image.open("data_pictures/poker/poker_background_10.png").resize((768, 432))

            poker_background = draw_text_on_image(current_game, poker_background, self.font_path)

            if not os.path.exists('data_pictures/avatars'):
                os.mkdir('data_pictures/avatars')

            # Display player cards
            await display_player_cards_and_avatars(self.filename, current_game, poker_background, self.client, self.font_path)
            poker_background.close()

            write_poker_games_to_file(self.filename, games_obj)

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


class ButtonsMenu(discord.ui.View):
    """
    This class represents the view. It contains the filename in which the data is stored and the buttons.
    """
    def __init__(self, filename, current_game: Game, user_id: int, client, font_path):
        super().__init__()

        self.filename = filename
        self.games_obj = load_poker_games_from_file(filename)
        self.current_game = current_game
        self.user_id = user_id
        self.client = client
        self.font_path = font_path

        if self.current_game.current_player_index == self.current_game.get_player_index(self.user_id):
            self.enable_and_disable_button('fold')
            self.enable_and_disable_button('call')
            self.enable_and_disable_button('raise')

    @discord.ui.button(label="fold", style=discord.ButtonStyle.blurple, custom_id="fold", disabled=True)
    async def fold(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        """
        Fold.

        :param interaction: Used to handle the button interaction.
        :param button: The button object.
        """
        global last_messages_to_players

        current_player = self.current_game.players[self.current_game.current_player_index]

        fold_result = self.current_game.fold()
        write_poker_games_to_file(self.filename, self.games_obj)

        if fold_result == 'start_new_round':
            for index, player in enumerate(self.current_game.players):
                await last_messages_to_players[index].delete()
            last_messages_to_players = []
            await self.start_new_round(self.current_game)
        else:
            for index, player in enumerate(self.current_game.players):
                user_index_in_game = self.current_game.get_player_index_relative_to_other_player(self.user_id, player.player_id)
                cross_place = cross_places[user_index_in_game]
                player_image = Image.open(f'data_pictures/poker/message_{player.player_id}.png')
                if player.player_id != current_player.player_id:
                    draw_player_action_on_image(player_image, self.font_path, f'{current_player.name} folded.')
                else:
                    draw_player_action_on_image(player_image, self.font_path, f'You folded.')
                draw_cross(player_image, cross_place[0], cross_place[1], cross_place[2], cross_place[3])
                player_image.save(f'data_pictures/poker/message_{player.player_id}.png')
                player_image.close()

                discord_user = await self.client.fetch_user(player.player_id)
                await last_messages_to_players[index].delete()
                player_message = await discord_user.send(file=discord.File(f"data_pictures/poker/message_{player.player_id}.png"), view=ButtonsMenu(self.filename, self.current_game, player.player_id, self.client, self.font_path))
                last_messages_to_players[index] = player_message

        await interaction.response.defer()

    @discord.ui.button(label="call", style=discord.ButtonStyle.blurple, custom_id="call", disabled=True)
    async def call(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        """
        Call.

        :param interaction: Used to handle the button interaction.
        :param button: The button object.
        """
        current_player = self.current_game.players[self.current_game.current_player_index]

        self.current_game.call()
        write_poker_games_to_file(self.filename, self.games_obj)

        for index, player in enumerate(self.current_game.players):
            player_image = Image.open(f'data_pictures/poker/message_{player.player_id}.png')
            if player.player_id != current_player.player_id:
                draw_player_action_on_image(player_image, self.font_path, f'{current_player.name} called.')
            else:
                draw_player_action_on_image(player_image, self.font_path, f'You called.')

            player_image.save(f'data_pictures/poker/message_action_{player.player_id}.png')
            player_image.close()

            discord_user = await self.client.fetch_user(player.player_id)
            await last_messages_to_players[index].delete()
            player_message = await discord_user.send(file=discord.File(f"data_pictures/poker/message_action_{player.player_id}.png"),
                                                     view=ButtonsMenu(self.filename, self.current_game, player.player_id, self.client, self.font_path))
            last_messages_to_players[index] = player_message

        await interaction.response.defer()

    @discord.ui.button(label="raise", style=discord.ButtonStyle.blurple, custom_id="raise", disabled=True)
    async def raise_func(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        current_player = self.current_game.players[self.current_game.current_player_index]

        await interaction.response.send_modal(RaiseAmount(self.current_game, current_player, self.font_path, self.client, self.filename, self.games_obj))

    def enable_and_disable_button(self, custom_id: str, disabled: bool = False) -> None:
        """
        Enable or disable the button with a certain custom id.

        :param custom_id: The custom id of the button to enable or disable.
        :param disabled: True if the button needs to be disabled, else False.
        """
        child_index = 0
        while child_index < len(self.children) and self.children[child_index].custom_id != custom_id:
            child_index += 1

        self.children[child_index].disabled = disabled

    async def start_new_round(self, current_game: Game):
        games_obj: Games = load_poker_games_from_file(self.filename)

        current_game.start_new_round()

        # Display general stats
        poker_background = Image.open("data_pictures/poker/poker_background_10.png").resize((768, 432))

        poker_background = draw_text_on_image(current_game, poker_background, self.font_path)

        if not os.path.exists('data_pictures/avatars'):
            os.mkdir('data_pictures/avatars')

        # Display player cards
        await display_player_cards_and_avatars(self.filename, current_game, poker_background, self.client, self.font_path)
        poker_background.close()

        write_poker_games_to_file(self.filename, games_obj)


async def setup(client):
    await client.add_cog(Poker(client))
