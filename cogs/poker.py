import asyncio
import os
import pickle
import traceback
from typing import List, Union

from PIL import Image

import discord
from discord.ext import commands

from poker.constants import cross_places, background_size, player_places
from poker.draw import draw_cross, draw_right_panel_on_image, draw_player_action_on_image, create_and_save_avatar, display_avatars, display_current_player_cards, display_cards_of_another_player, \
    display_open_cards, display_player_roles
from poker.game import Game
from poker.players.player import Player
from poker.utils import contains_number

last_messages_to_players = []
number_of_bots = -1
bots_level = None


async def delete_and_send_message(client, filename: str, buttons_to_enable: List[str], current_game: Game, font_path: str, player: Player, player_index: int, player_is_dead: bool = False, delete_messages: bool = True):
    """
        Display the action of the players and send a message to all real players.

        :param client: The client.
        :param filename: The filename.
        :param buttons_to_enable: The buttons that need to be enabled.
        :param current_game: The current game.
        :param font_path: The font path.
        :param player: The players to send a message to.
        :param player_index: The index of the players.
        :param player_is_dead: True if the players is dead.
        :param delete_messages: True if the previous messages need to be deleted.

        :return: True if the string contains a number.
        """
    discord_user = await client.fetch_user(player.player_id)
    if delete_messages:
        await last_messages_to_players[player_index].delete()
    player_message = await discord_user.send(file=discord.File(f"data_pictures/poker/message_action_{player.player_id}.png"),
                                             view=ButtonsMenu(filename, current_game, player.player_id, client, font_path, buttons_to_enable, player_is_dead=player_is_dead))
    if delete_messages:
        last_messages_to_players[player_index] = player_message
    else:
        last_messages_to_players.append(player_message)


async def display_player_action_and_send_messages(client, filename: str, buttons_to_enable: List[str], current_game: Game, current_player: Player, font_path: str, action_type: str) -> None:
    """
    Display the action of the players and send a message to all real players.

    :param client: The client.
    :param filename: The filename.
    :param buttons_to_enable: The buttons that need to be enabled.
    :param current_game: The current game.
    :param current_player: The current players.
    :param font_path: The font path.
    :param action_type: The action type (raise, bet, ...).

    :return: True if the string contains a number.
    """
    for index, player in enumerate(current_game.get_real_players()):
        player_image = Image.open(f'data_pictures/poker/message_{player.player_id}.png')
        if action_type == 'raise':
            action = f'Raised to {current_player.current_bet}.'
        elif action_type == 'bet':
            action = f'Placed a bet of {current_player.current_bet} credits.'
        else:
            action = ''

        draw_player_action_on_image(player_image, [current_player], font_path, action)

        draw_right_panel_on_image(player_image, current_game, font_path, player)
        player_image.close()

        await delete_and_send_message(client, filename, buttons_to_enable, current_game, font_path, player, index)


async def display_player_cards_and_avatars_and_send_messages(filename: str, current_game, poker_background, client, font_path, buttons_to_enable, draw_player_action=False):
    for index, player in enumerate(current_game.get_real_players()):
        player_background = poker_background.copy()

        if player.amount_of_credits != 0:
            # display the cards of the current players if he has credits
            player_background = await display_current_player_cards(player_background, player.cards)

        # display the avatars on the players places
        players_in_current_game = current_game.players[current_game.get_player_index(player.player_id) + 1:] + current_game.players[:current_game.get_player_index(player.player_id)]
        player_background = display_avatars(player_background, players_in_current_game, player_places, 'data_pictures/avatars/', '.png')

        # display a cross on the place of a players that has no credits anymore
        for other_player in current_game.players:
            if other_player.amount_of_credits == 0:
                user_index_in_game = current_game.get_player_index_relative_to_other_player(other_player.player_id, player.player_id)
                cross_place = cross_places[user_index_in_game]
                player_background = draw_cross(player_background, cross_place[0], cross_place[1], cross_place[2], cross_place[3])

        player_background = display_player_roles(player_background, current_game, font_path, player)

        player_background.save(f'data_pictures/poker/message_{player.player_id}.png')

        # display the cards of other players when a players has no credits anymore
        if player.amount_of_credits == 0:
            for other_player in list(filter(lambda p: p.player_id != player.player_id, current_game.players)):
                index_relative_to_player = current_game.get_player_index_relative_to_other_player(other_player.player_id, player.player_id)
                player_background = await display_cards_of_another_player(player_background, other_player.cards, index_relative_to_player)

        player_background.save(f"data_pictures/poker/message_{player.player_id}.png")

        draw_right_panel_on_image(player_background, current_game, font_path, player, draw_player_action=draw_player_action)
        player_background.close()

        await delete_and_send_message(client, filename, buttons_to_enable, current_game, font_path, player, index, player_is_dead=(player.amount_of_credits == 0), delete_messages=False)


async def raise_game_func(raise_value, client, filename, buttons_to_enable, current_game: Game, current_player, font_path):
    current_player = current_game.players[current_game.current_player_index]
    current_game.raise_func(raise_value)

    await display_player_action_and_send_messages(client, filename, buttons_to_enable, current_game, current_player, font_path, 'raise')


class RaiseAmount(discord.ui.Modal, title='raise'):
    def __init__(self, current_game: Game, current_player: Player, font_path, client, filename, games_obj, buttons_to_enable, **kwargs):
        super().__init__(**kwargs)

        self.current_game = current_game
        self.current_player = current_player
        self.font_path = font_path
        self.client = client
        self.filename = filename
        self.games_obj = games_obj
        self.buttons_to_enable = buttons_to_enable

    rai = discord.ui.TextInput(label="raise", style=discord.TextStyle.short, placeholder="Provide your bet or type 'all-in':")

    async def on_submit(self, interaction: discord.Interaction):
        if (contains_number(self.rai.value) and self.current_game.raise_lower_bound <= int(self.rai.value) <= self.current_player.amount_of_credits) or self.rai.value.lower() in ['all-in', 'all', 'all in']:
            raised_value = int(self.rai.value) if contains_number(self.rai.value) else self.current_player.amount_of_credits
            current_player = self.current_game.players[self.current_game.current_player_index]
            self.current_game.raise_func(raised_value)

            await display_player_action_and_send_messages(self.client, self.filename, self.buttons_to_enable, self.current_game, current_player, self.font_path, 'raise')
        elif contains_number(self.rai.value) and int(self.rai.value) <= self.current_player.amount_of_credits:
            await interaction.response.send_message(f'You must raise by more than {self.current_game.raise_lower_bound} credits!', ephemeral=True)
        elif contains_number(self.rai.value):
            await interaction.response.send_message(f"You don't have that amount of credits!", ephemeral=True)
        else:
            await interaction.response.send_message("This value has to be a number or 'all-in'!", ephemeral=True)

        await interaction.response.defer()

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        # Make sure we know what the error actually is
        traceback.print_exception(type(error), error, error.__traceback__)


async def bet_game_func(bet_value, client, filename, current_game: Game, current_player, font_path):
    current_player = current_game.players[current_game.current_player_index]
    current_game.raise_func(bet_value)

    await display_player_action_and_send_messages(client, filename, ['fold', 'call', 'raise'], current_game, current_player, font_path, 'bet')


class BetAmount(discord.ui.Modal, title='bet'):
    def __init__(self, current_game: Game, current_player: Player, font_path, client, filename, games_obj, buttons_to_enable, **kwargs):
        super().__init__(**kwargs)

        self.current_game = current_game
        self.current_player = current_player
        self.font_path = font_path
        self.client = client
        self.filename = filename
        self.games_obj = games_obj
        self.buttons_to_enable = buttons_to_enable

    bet = discord.ui.TextInput(label="bet", style=discord.TextStyle.short, placeholder="Provide your bet or type 'all-in':")

    async def on_submit(self, interaction: discord.Interaction):
        if (contains_number(self.bet.value) and self.current_game.big_blind + max(list(map(lambda x: x.current_bet, self.current_game.players))) <= int(self.bet.value) <= self.current_player.amount_of_credits) or self.bet.value.lower() in ['all-in', 'all', 'all in']:
            raised_value = int(self.bet.value) if contains_number(self.bet.value) else self.current_player.amount_of_credits
            current_player = self.current_game.players[self.current_game.current_player_index]
            self.current_game.raise_func(raised_value)

            await display_player_action_and_send_messages(self.client, self.filename, self.buttons_to_enable, self.current_game, current_player, self.font_path, 'bet')
        elif contains_number(self.bet.value) and int(self.bet.value) <= self.current_player.amount_of_credits:
            minimum_credits = self.current_game.big_blind + max(list(map(lambda x: x.current_bet, self.current_game.players)))
            await interaction.response.send_message(f'You must bet at least {minimum_credits} credits!', ephemeral=True)
        elif contains_number(self.bet.value):
            await interaction.response.send_message(f"You don't have that amount of credits!", ephemeral=True)
        else:
            await interaction.response.send_message("This value has to be a number or 'all-in'!", ephemeral=True)

        await interaction.response.defer()

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        # Make sure we know what the error actually is
        traceback.print_exception(type(error), error, error.__traceback__)


class SelectNumberOfBots(discord.ui.Select):
    def __init__(self, number_of_players):
        minimum_number_of_bots = 1 if number_of_players == 1 else 0

        options = [
            discord.SelectOption(label=f'{x} bot') if x == 1 else discord.SelectOption(label=f'{x} bots') for x in range(minimum_number_of_bots, 11 - number_of_players)
        ]
        super().__init__(placeholder="Select the number of bots", max_values=1, min_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        global number_of_bots
        number_of_bots = int(self.values[0][0])

        await interaction.response.defer()


class SelectNumberOfBotsView(discord.ui.View):
    def __init__(self, number_of_players, *, timeout=180):
        super().__init__(timeout=timeout)
        self.add_item(SelectNumberOfBots(number_of_players))


class SelectBotsLevel(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label='Easy'),
            discord.SelectOption(label='Medium')
        ]
        super().__init__(placeholder="Select the level of the bots", max_values=1, min_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        global bots_level

        bots_level = self.values[0]

        await interaction.response.defer()


class SelectBotsLevelView(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)
        self.add_item(SelectBotsLevel())


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
        self.font_path = "data/cowboy-junk.ttf"

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """
        Create the file in which the data will be stored.
        """
        write_poker_games_to_file(self.filename, Games())
        print(f"{self.filename} created")

    @commands.command(usage="!poker",
                      description="Start a poker game and wait for players to join.",
                      help="!poker")
    async def poker(self, ctx: commands.Context) -> None:
        games_obj = load_poker_games_from_file(self.filename)

        for game in games_obj.games:
            if (ctx.author.id, ctx.author.display_name) in list(map(lambda x: (x.player_id, x.name), game.players)):
                await ctx.reply("You are already in a game!")
                return

        poker_start_embed = discord.Embed(title="A poker game has started!", description=f"Current players: \n>{ctx.author.display_name}")
        poker_start_message = await ctx.send(embed=poker_start_embed)

        new_game = Game(ctx.author, poker_start_message.id)
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
            write_poker_games_to_file(self.filename, games_obj)
            await reaction.message.edit(embed=embed)
        elif reaction.emoji == '▶' and current_game is not None and user.id == current_game.players[0].player_id and 0 < len(current_game.players) <= 10:
            await reaction.message.delete()

            number_of_bots_message = await user.send("Choose the number of bots please!", view=SelectNumberOfBotsView(len(current_game.players)))

            while number_of_bots == -1:
                await asyncio.sleep(0.2)

            await number_of_bots_message.delete()

            if number_of_bots > 0:
                bots_level_message = await user.send("Choose the bots level!", view=SelectBotsLevelView())

                while bots_level is None:
                    await asyncio.sleep(0.2)

                await bots_level_message.delete()

            for _ in range(number_of_bots):
                current_game.add_bot(bots_level)

            write_poker_games_to_file(self.filename, games_obj)

            current_game.on_game_start()

            # Display general stats
            poker_background = Image.open("data_pictures/poker/poker_background_big_768x432.png").resize(background_size)

            if not os.path.exists('data_pictures/avatars'):
                os.mkdir('data_pictures/avatars')

            # create the avatars
            for player in current_game.players:
                await create_and_save_avatar(self.client, player, real_player=current_game.get_real_players()[0])

            # Display players cards and avatars
            await display_player_cards_and_avatars_and_send_messages(self.filename, current_game, poker_background, self.client, self.font_path, ['fold', 'call', 'raise'])

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
            if len(current_game.players) == 0:
                games_obj.remove_game(current_game)
                write_poker_games_to_file(self.filename, games_obj)
                await reaction.message.delete()
                return

            embed = reaction.message.embeds[0]
            embed.description = current_game.remove_player(user)
            await reaction.message.edit(embed=embed)
            write_poker_games_to_file(self.filename, games_obj)


class ButtonsMenu(discord.ui.View):
    """
    This class represents the view. It contains the filename in which the data is stored and the buttons.
    """
    def __init__(self, filename, current_game: Game, user_id: int, client, font_path, buttons_to_enable, player_is_dead=False):
        super().__init__()

        self.filename = filename
        self.games_obj = load_poker_games_from_file(filename)
        self.current_game = current_game
        self.user_id = user_id
        self.client = client
        self.font_path = font_path
        self.buttons_to_enable = buttons_to_enable

        if self.current_game.players[self.current_game.current_player_index].is_bot:
            if 'start_new_round' not in buttons_to_enable and 'end_game' not in buttons_to_enable:
                self.loop = asyncio.get_event_loop()
                self.loop.create_task(self.execute_bot_moves())
            else:
                if 'start_new_round' in buttons_to_enable:
                    self.enable_and_disable_button('start_new_round')

                if 'end_game' in buttons_to_enable:
                    self.enable_and_disable_button('end_game')
        else:
            if 'start_new_round' in buttons_to_enable:
                self.enable_and_disable_button('start_new_round')

            if 'end_game' in buttons_to_enable:
                self.enable_and_disable_button('end_game')

            if not player_is_dead and self.current_game.current_player_index == self.current_game.get_player_index(self.user_id):
                current_player = self.current_game.players[self.current_game.current_player_index]
                for move in self.check_if_moves_can_be_enabled(buttons_to_enable, current_player):
                    self.enable_and_disable_button(move)

    def check_if_moves_can_be_enabled(self, moves, current_player):
        result = []

        max_bet = max(list(map(lambda x: x.current_bet, self.current_game.players)))
        for move in moves:
            if not ((current_player.current_bet == current_player.amount_of_credits and move in ['fold', 'raise', 'bet']) or
                    (current_player.current_bet != current_player.amount_of_credits and max_bet > self.current_game.players[self.current_game.current_player_index].amount_of_credits and move in [
                        'raise', 'bet']) or
                    (current_player.current_bet != current_player.amount_of_credits and self.current_game.raise_lower_bound > self.current_game.players[
                        self.current_game.current_player_index].amount_of_credits and move in ['raise']) or
                    (current_player.current_bet != current_player.amount_of_credits and self.current_game.big_blind + max(list(map(lambda x: x.current_bet, self.current_game.players))) >
                     self.current_game.players[self.current_game.current_player_index].amount_of_credits and move in ['bet'])):
                result.append(move)

        return result

    async def get_bot_move(self, available_moves):
        raise_lower_bound, raise_upper_bound = self.current_game.raise_lower_bound, self.current_game.players[self.current_game.current_player_index].amount_of_credits
        bet_lower_bound, bet_upper_bound = self.current_game.big_blind + max(list(map(lambda x: x.current_bet, self.current_game.players))), self.current_game.players[self.current_game.current_player_index].amount_of_credits

        chosen_move, chosen_bet_value = await self.current_game.players[self.current_game.current_player_index].move(available_moves, raise_lower_bound, raise_upper_bound, bet_lower_bound, bet_upper_bound)

        if chosen_move == 'fold':
            await self.fold_func()
        elif chosen_move == 'call':
            await self.call_func()
        elif chosen_move == 'raise':
            current_player = self.current_game.players[self.current_game.current_player_index]

            if self.current_game.current_player_index in self.current_game.last_player_who_raised:
                self.current_game.last_player_who_raised.remove(self.current_game.current_player_index)
            self.current_game.last_player_who_raised.append(self.current_game.current_player_index)

            await raise_game_func(chosen_bet_value, self.client, self.filename, self.buttons_to_enable, self.current_game, current_player, self.font_path)
        elif chosen_move == 'bet':
            current_player = self.current_game.players[self.current_game.current_player_index]

            if self.current_game.current_player_index in self.current_game.last_player_who_raised:
                self.current_game.last_player_who_raised.remove(self.current_game.current_player_index)
            self.current_game.last_player_who_raised.append(self.current_game.current_player_index)

            await bet_game_func(chosen_bet_value, self.client, self.filename, self.current_game, current_player, self.font_path)
        else:
            await self.check_func()

    async def execute_bot_moves(self):
        available_moves = []
        current_player = self.current_game.players[self.current_game.current_player_index]
        for move in self.check_if_moves_can_be_enabled(self.buttons_to_enable, current_player):
            available_moves.append(move)
        await self.get_bot_move(available_moves)

    async def fold_func(self):
        global last_messages_to_players

        current_player = self.current_game.players[self.current_game.current_player_index]

        fold_result = self.current_game.fold()

        if fold_result == 'start_new_round':
            await self.showdown(round_winner=self.current_game.players[(self.current_game.current_player_index + 1) % len(self.current_game.players)])
        elif not self.current_game.check_same_bets() or not all(
                list(map(lambda p: p.had_possibility_to_raise_or_bet, list(filter(lambda x: not x.is_dead and x.amount_of_credits != 0, self.current_game.players))))):
            for index, player in enumerate(self.current_game.get_real_players()):
                user_index_in_game = self.current_game.get_player_index_relative_to_other_player(current_player.player_id, player.player_id)
                cross_place = cross_places[user_index_in_game]
                player_image = Image.open(f'data_pictures/poker/message_{player.player_id}.png')
                player_image = draw_cross(player_image, cross_place[0], cross_place[1], cross_place[2], cross_place[3])
                player_image.save(f'data_pictures/poker/message_{player.player_id}.png')

                draw_player_action_on_image(player_image, [current_player], self.font_path, 'Folded.')

                draw_right_panel_on_image(player_image, self.current_game, self.font_path, player)
                player_image.close()

                await delete_and_send_message(self.client, self.filename, self.buttons_to_enable, self.current_game, self.font_path, player, index)
        elif self.current_game.poker_round == 0:
            await self.flop([current_player], 'Folded.')
        elif self.current_game.poker_round == 1:
            await self.turn_or_river([current_player], 'Folded.')
        elif self.current_game.poker_round == 2:
            await self.turn_or_river([current_player], 'Folded.', 4)
        else:
            await self.showdown()

    @discord.ui.button(label="fold", style=discord.ButtonStyle.blurple, custom_id="fold", disabled=True)
    async def fold(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        """
        Fold.

        :param interaction: Used to handle the button interaction.
        :param button: The button object.
        """
        await self.fold_func()

        await interaction.response.defer()

    async def call_func(self):
        current_player = self.current_game.players[self.current_game.current_player_index]

        self.current_game.call()

        if not self.current_game.check_same_bets() or not all(
                list(map(lambda p: p.had_possibility_to_raise_or_bet, list(filter(lambda x: not x.is_dead and x.amount_of_credits != 0, self.current_game.players))))):
            for index, player in enumerate(self.current_game.get_real_players()):
                player_image = Image.open(f'data_pictures/poker/message_{player.player_id}.png')
                draw_player_action_on_image(player_image, [current_player], self.font_path, 'Called.')

                draw_right_panel_on_image(player_image, self.current_game, self.font_path, player)
                player_image.close()

                await delete_and_send_message(self.client, self.filename, self.buttons_to_enable, self.current_game, self.font_path, player, index)
        elif self.current_game.poker_round == 0:
            await self.flop([current_player], 'Called.')
        elif self.current_game.poker_round == 1:
            await self.turn_or_river([current_player], 'Called.')
        elif self.current_game.poker_round == 2:
            await self.turn_or_river([current_player], 'Called.', 4)
        else:
            await self.showdown()

    @discord.ui.button(label="call", style=discord.ButtonStyle.blurple, custom_id="call", disabled=True)
    async def call(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        """
        Call.

        :param interaction: Used to handle the button interaction.
        :param button: The button object.
        """
        await self.call_func()

        await interaction.response.defer()

    @discord.ui.button(label="raise", style=discord.ButtonStyle.blurple, custom_id="raise", disabled=True)
    async def raise_func(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        current_player = self.current_game.players[self.current_game.current_player_index]

        if self.current_game.current_player_index in self.current_game.last_player_who_raised:
            self.current_game.last_player_who_raised.remove(self.current_game.current_player_index)
        self.current_game.last_player_who_raised.append(self.current_game.current_player_index)

        await interaction.response.send_modal(RaiseAmount(self.current_game, current_player, self.font_path, self.client, self.filename, self.games_obj, self.buttons_to_enable))

    async def check_func(self):
        current_player = self.current_game.players[self.current_game.current_player_index]

        self.current_game.check_func()

        if not all(list(map(lambda p: p.had_possibility_to_raise_or_bet, list(filter(lambda x: not x.is_dead and x.amount_of_credits != 0, self.current_game.players))))):
            for index, player in enumerate(self.current_game.get_real_players()):
                player_image = Image.open(f'data_pictures/poker/message_{player.player_id}.png')
                draw_player_action_on_image(player_image, [current_player], self.font_path, 'Checked.')

                draw_right_panel_on_image(player_image, self.current_game, self.font_path, player)
                player_image.close()

                await delete_and_send_message(self.client, self.filename, ['fold', 'bet', 'check'], self.current_game, self.font_path, player, index)
        elif self.current_game.poker_round == 1:
            await self.turn_or_river([current_player], 'Checked.')
        elif self.current_game.poker_round == 2:
            await self.turn_or_river([current_player], 'Checked.', 4)
        else:
            await self.showdown()

    @discord.ui.button(label="check", style=discord.ButtonStyle.blurple, custom_id="check", disabled=True)
    async def check(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self.check_func()

        await interaction.response.defer()

    @discord.ui.button(label="bet", style=discord.ButtonStyle.blurple, custom_id="bet", disabled=True)
    async def bet_func(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        current_player = self.current_game.players[self.current_game.current_player_index]

        if self.current_game.current_player_index in self.current_game.last_player_who_raised:
            self.current_game.last_player_who_raised.remove(self.current_game.current_player_index)
        self.current_game.last_player_who_raised.append(self.current_game.current_player_index)

        await interaction.response.send_modal(BetAmount(self.current_game, current_player, self.font_path, self.client, self.filename, self.games_obj, ['fold', 'call', 'raise']))

    @discord.ui.button(label="start new round", style=discord.ButtonStyle.blurple, custom_id="start_new_round", disabled=True)
    async def start_new_round_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self.start_new_round()
        await interaction.response.defer()

    @discord.ui.button(label="end game", style=discord.ButtonStyle.blurple, custom_id="end_game", disabled=True)
    async def end_game_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self.end_game(self.current_game.round_winners[0])
        await interaction.response.defer()

    async def flop(self, players_action: List[Player], action_to_draw: str):
        self.current_game.reset_possibility_to_raise()
        self.current_game.poker_round += 1
        self.current_game.current_player_index = self.current_game.get_player_index(self.current_game.dealer.player_id)
        self.current_game.next_player_who_is_not_dead()

        for player_index, player in enumerate(self.current_game.get_real_players()):
            player_image = Image.open(f'data_pictures/poker/message_{player.player_id}.png')

            # display the open cards
            player_image = await display_open_cards(player_image, self.current_game.open_cards[:3], cards_range_start=0, cards_range_end=3)

            # display a cross for each dead players
            for dead_player in self.current_game.get_dead_players():
                user_index_in_game = self.current_game.get_player_index_relative_to_other_player(dead_player.player_id, player.player_id)
                cross_place = cross_places[user_index_in_game]
                player_image = draw_cross(player_image, cross_place[0], cross_place[1], cross_place[2], cross_place[3])

            player_image.save(f"data_pictures/poker/message_{player.player_id}.png")

            player_image = draw_player_action_on_image(player_image, players_action, self.font_path, action_to_draw)

            draw_right_panel_on_image(player_image, self.current_game, self.font_path, player)
            player_image.close()

            await delete_and_send_message(self.client, self.filename, ['fold', 'bet', 'check'], self.current_game, self.font_path, player, player_index)

    async def turn_or_river(self, players_action: List[Player], action_to_draw: str, index=3):
        self.current_game.reset_possibility_to_raise()
        self.current_game.poker_round += 1

        for player_index, player in enumerate(self.current_game.get_real_players()):
            player_image = Image.open(f'data_pictures/poker/message_{player.player_id}.png')

            # display the open cards
            player_image = await display_open_cards(player_image, [self.current_game.open_cards[index]], cards_range_start=index, cards_range_end=(index + 1))

            for dead_player in self.current_game.get_dead_players():
                user_index_in_game = self.current_game.get_player_index_relative_to_other_player(dead_player.player_id, player.player_id)
                cross_place = cross_places[user_index_in_game]
                player_image = draw_cross(player_image, cross_place[0], cross_place[1], cross_place[2], cross_place[3])


            player_image.save(f"data_pictures/poker/message_{player.player_id}.png")

            player_image = draw_player_action_on_image(player_image, players_action, self.font_path, action_to_draw)

            draw_right_panel_on_image(player_image, self.current_game, self.font_path, player)
            player_image.close()

            await delete_and_send_message(self.client, self.filename, ['fold', 'bet', 'check'], self.current_game, self.font_path, player, player_index)

    async def showdown(self, round_winner: Player = None):
        player_status = list(map(lambda p: p.amount_of_credits, self.current_game.players))
        round_winners = self.current_game.showdown(round_winner)

        game_finished = self.current_game.game_finished()

        for player_index, player in enumerate(self.current_game.get_real_players()):
            poker_background = Image.open("data_pictures/poker/poker_background_big_768x432.png")

            if not os.path.exists('data_pictures/avatars'):
                os.mkdir('data_pictures/avatars')

            # display the winner message
            if len(round_winners) == 1:
                draw_player_action_on_image(poker_background, round_winners, self.font_path, 'Winner of this round!')
            else:
                draw_player_action_on_image(poker_background, round_winners, self.font_path, 'Winners of this round!')

            # display the cards of the current players
            if player_status[player_index]:
                poker_background = await display_current_player_cards(poker_background, player.cards)

            # display the open cards
            poker_background = await display_open_cards(poker_background, self.current_game.open_cards, cards_range_start=0, cards_range_end=5)

            # display the cards of other players
            for other_player_index, other_player in enumerate(self.current_game.players):
                if player_status[other_player_index] != 0 and other_player_index != player_index:
                    index_relative_to_player = self.current_game.get_player_index_relative_to_other_player(other_player.player_id, player.player_id)
                    poker_background = await display_cards_of_another_player(poker_background, other_player.cards, index_relative_to_player)

                if player_status[other_player_index] == 0:
                    user_index_in_game = self.current_game.get_player_index_relative_to_other_player(other_player.player_id, player.player_id)
                    cross_place = cross_places[user_index_in_game]
                    poker_background = draw_cross(poker_background, cross_place[0], cross_place[1], cross_place[2], cross_place[3])

            draw_right_panel_on_image(poker_background, self.current_game, self.font_path, player)

            poker_background.close()

            if player.player_id == self.current_game.game_author_id:
                if game_finished:
                    buttons_to_enable = ['end_game']
                else:
                    buttons_to_enable = ['start_new_round']
            else:
                buttons_to_enable = []

            await delete_and_send_message(self.client, self.filename, buttons_to_enable, self.current_game, self.font_path, player, player_index)

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

    async def start_new_round(self):
        global last_messages_to_players

        self.current_game.start_new_round()

        for index, player in enumerate(self.current_game.get_real_players()):
            await last_messages_to_players[index].delete()

        last_messages_to_players = []

        # Display general stats
        poker_background = Image.open("data_pictures/poker/poker_background_big_768x432.png")

        if not os.path.exists('data_pictures/avatars'):
            os.mkdir('data_pictures/avatars')

        # Display players cards
        await display_player_cards_and_avatars_and_send_messages(self.filename, self.current_game, poker_background, self.client, self.font_path, ['fold', 'call', 'raise'], draw_player_action=True)

        for player in self.current_game.get_real_players():
            player_background = poker_background.copy()
            draw_right_panel_on_image(player_background, self.current_game, self.font_path, player)
            player_background.close()
        poker_background.close()

    async def end_game(self, winner: Player):
        for player_index, player in enumerate(self.current_game.get_real_players()):
            discord_user = await self.client.fetch_user(player.player_id)
            await last_messages_to_players[player_index].delete()

            if winner.player_id == player.player_id:
                await discord_user.send(embed=discord.Embed(title="Game result:", description='Congrats, you won the game!'))
            else:
                await discord_user.send(embed=discord.Embed(title="Game result:", description=f'{winner.name} won the game!'))

        self.games_obj.remove_game(self.current_game)
        write_poker_games_to_file(self.filename, self.games_obj)


async def setup(client):
    await client.add_cog(Poker(client))
