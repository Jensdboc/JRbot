import os
import pickle
import traceback
from typing import List, Union

from PIL import Image

import discord
from discord.ext import commands

from poker.constants import cross_places, card_places_center, open_card_size, background_size, own_card_size, other_players_card_size, other_players_card_rotations, other_players_card_places, \
    other_players_card_places_offsets
from poker.draw import create_avatars_for_player, draw_cross, draw_right_panel_on_image, draw_player_action_on_image, draw_pot
from poker.game import Game, Player
from poker.utils import contains_number

last_messages_to_players = []


class RaiseAmount(discord.ui.Modal, title='raise_amount'):
    def __init__(self, current_game: Game, current_player: Player, font_path, client, filename, games_obj, buttons_to_enable, **kwargs):
        super().__init__(**kwargs)

        self.current_game = current_game
        self.current_player = current_player
        self.font_path = font_path
        self.client = client
        self.filename = filename
        self.games_obj = games_obj
        self.buttons_to_enable = buttons_to_enable

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

                draw_pot(player_image, self.current_game, self.font_path, player)
                player_image.close()

                discord_user = await self.client.fetch_user(player.player_id)
                await last_messages_to_players[index].delete()
                player_message = await discord_user.send(file=discord.File(f"data_pictures/poker/message_action_{player.player_id}.png"),
                                                         view=ButtonsMenu(self.filename, self.current_game, player.player_id, self.client, self.font_path, self.buttons_to_enable))
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


class BetAmount(discord.ui.Modal, title='bet_amount'):
    def __init__(self, current_game: Game, current_player: Player, font_path, client, filename, games_obj, buttons_to_enable, **kwargs):
        super().__init__(**kwargs)

        self.current_game = current_game
        self.current_player = current_player
        self.font_path = font_path
        self.client = client
        self.filename = filename
        self.games_obj = games_obj
        self.buttons_to_enable = buttons_to_enable

    bet = discord.ui.TextInput(label="bet", style=discord.TextStyle.short, placeholder="Provide your bet:")

    async def on_submit(self, interaction: discord.Interaction):
        if contains_number(self.bet.value) and self.current_game.big_blind + max(list(map(lambda x: x.current_bet, self.current_game.players))) <= int(self.bet.value):
            self.current_game.raise_func(int(self.bet.value))

            for index, player in enumerate(self.current_game.players):
                player_image = Image.open(f'data_pictures/poker/message_{player.player_id}.png')
                if player.player_id != self.current_player.player_id:
                    draw_player_action_on_image(player_image, self.font_path, f'{self.current_player.name} has placed a bet of {self.current_player.current_bet} credits.')
                else:
                    draw_player_action_on_image(player_image, self.font_path, f'You have placed a bet of {self.current_player.current_bet} credits.')

                draw_pot(player_image, self.current_game, self.font_path, player)
                player_image.close()

                discord_user = await self.client.fetch_user(player.player_id)
                await last_messages_to_players[index].delete()
                player_message = await discord_user.send(file=discord.File(f"data_pictures/poker/message_action_{player.player_id}.png"),
                                                         view=ButtonsMenu(self.filename, self.current_game, player.player_id, self.client, self.font_path, self.buttons_to_enable))
                last_messages_to_players[index] = player_message

            write_poker_games_to_file(self.filename, self.games_obj)

        elif contains_number(self.bet.value):
            minimum_credits = self.current_game.big_blind + max(list(map(lambda x: x.current_bet, self.current_game.players)))
            await interaction.response.send_message(f'You must bet at least {minimum_credits} credits!', ephemeral=True)
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


async def display_player_cards_and_avatars(filename, current_game, poker_background, client, font_path, buttons_to_enable, draw_player_action=False):
    for player in current_game.players:
        player_background = poker_background.copy()

        for index, card in enumerate(player.cards):
            card_value = card.get_card_integer_value() if card.value not in ['jack', 'queen', 'king', 'ace'] else card.value
            player_card_image = Image.open(f'data_pictures/playing_cards/{card_value}_{card.card_suit}.png')
            player_card_image = player_card_image.resize(own_card_size)
            player_background.paste(player_card_image, (198 + index * player_card_image.size[0], 242), player_card_image)

        player_background = await create_avatars_for_player(client, player, current_game, player_background)

        player_background.save(f"data_pictures/poker/message_{player.player_id}.png")

        draw_pot(player_background, current_game, font_path, player, draw_player_action=draw_player_action)

        discord_user = await client.fetch_user(player.player_id)
        player_message = await discord_user.send(file=discord.File(f"data_pictures/poker/message_action_{player.player_id}.png"),
                                                 view=ButtonsMenu(filename, current_game, player.player_id, client, font_path, buttons_to_enable))
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

    @commands.command(usage="!poker small_blind",
                      description="Start a poker game and wait for players to join.",
                      help="!poker 5")
    async def poker(self, ctx: commands.Context, small_blind: int = 5) -> None:
        games_obj = load_poker_games_from_file(self.filename)
        start_amount = 1000

        for game in games_obj.games:
            if (ctx.author.id, ctx.author.display_name) in list(map(lambda x: (x.player_id, x.name), game.players)):
                await ctx.reply("You are already in a game!")
                return

        if small_blind <= 0 or small_blind > 500000:
            await ctx.reply("The small blind must be greater than 0 and less than 500000!")
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
            poker_background = Image.open("data_pictures/poker/poker_background_big_768x432.png").resize(background_size)

            if not os.path.exists('data_pictures/avatars'):
                os.mkdir('data_pictures/avatars')

            poker_background = await draw_right_panel_on_image(self.client, current_game, poker_background, self.font_path)

            # Display player cards
            await display_player_cards_and_avatars(self.filename, current_game, poker_background, self.client, self.font_path, ['fold', 'call', 'raise'])
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


class ButtonsMenu(discord.ui.View):
    """
    This class represents the view. It contains the filename in which the data is stored and the buttons.
    """
    def __init__(self, filename, current_game: Game, user_id: int, client, font_path, buttons_to_enable):
        super().__init__()

        self.filename = filename
        self.games_obj = load_poker_games_from_file(filename)
        self.current_game = current_game
        self.user_id = user_id
        self.client = client
        self.font_path = font_path
        self.buttons_to_enable = buttons_to_enable

        if 'start_new_round' in buttons_to_enable:
            self.enable_and_disable_button('start_new_round')

        if self.current_game.current_player_index == self.current_game.get_player_index(self.user_id):
            for button_to_enable in buttons_to_enable:
                self.enable_and_disable_button(button_to_enable)

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
            await self.showdown(draw_open_cards=True)
        elif not self.current_game.check_same_bets() or not all(list(map(lambda p: p.had_possibility_to_raise_or_bet, list(filter(lambda x: x.current_bet != -1, self.current_game.players))))):
            for index, player in enumerate(self.current_game.players):
                user_index_in_game = self.current_game.get_player_index_relative_to_other_player(self.user_id, player.player_id)
                cross_place = cross_places[user_index_in_game]
                player_image = Image.open(f'data_pictures/poker/message_{player.player_id}.png')
                draw_cross(player_image, cross_place[0], cross_place[1], cross_place[2], cross_place[3])
                player_image.save(f'data_pictures/poker/message_{player.player_id}.png')

                if player.player_id != current_player.player_id:
                    draw_player_action_on_image(player_image, self.font_path, f'{current_player.name} folded.')
                else:
                    draw_player_action_on_image(player_image, self.font_path, 'You folded.')

                draw_pot(player_image, self.current_game, self.font_path, player)
                player_image.close()

                discord_user = await self.client.fetch_user(player.player_id)
                await last_messages_to_players[index].delete()
                player_message = await discord_user.send(file=discord.File(f"data_pictures/poker/message_action_{player.player_id}.png"),
                                                         view=ButtonsMenu(self.filename, self.current_game, player.player_id, self.client, self.font_path, self.buttons_to_enable))
                last_messages_to_players[index] = player_message
        elif self.current_game.players[self.current_game.current_player_index].current_bet == max(list(map(lambda x: x.current_bet, self.current_game.players))) and self.current_game.poker_round == 0:
            await self.flop()
        elif self.current_game.players[self.current_game.current_player_index].current_bet == max(list(map(lambda x: x.current_bet, self.current_game.players))) and self.current_game.poker_round == 1:
            await self.turn_or_river()
        elif self.current_game.players[self.current_game.current_player_index].current_bet == max(list(map(lambda x: x.current_bet, self.current_game.players))) and self.current_game.poker_round == 2:
            await self.turn_or_river(4)
        else:
            await self.showdown()

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

        if not self.current_game.check_same_bets() or not all(list(map(lambda p: p.had_possibility_to_raise_or_bet, list(filter(lambda x: x.current_bet != -1, self.current_game.players))))):
            for index, player in enumerate(self.current_game.players):
                player_image = Image.open(f'data_pictures/poker/message_{player.player_id}.png')
                if player.player_id != current_player.player_id:
                    draw_player_action_on_image(player_image, self.font_path, f'{current_player.name} called.')
                else:
                    draw_player_action_on_image(player_image, self.font_path, 'You called.')

                draw_pot(player_image, self.current_game, self.font_path, player)
                player_image.close()

                discord_user = await self.client.fetch_user(player.player_id)
                await last_messages_to_players[index].delete()
                player_message = await discord_user.send(file=discord.File(f"data_pictures/poker/message_action_{player.player_id}.png"),
                                                         view=ButtonsMenu(self.filename, self.current_game, player.player_id, self.client, self.font_path, self.buttons_to_enable))
                last_messages_to_players[index] = player_message
        elif self.current_game.poker_round == 0:
            await self.flop()
        elif self.current_game.poker_round == 1:
            await self.turn_or_river()
        elif self.current_game.poker_round == 2:
            await self.turn_or_river(4)
        else:
            await self.showdown()

        await interaction.response.defer()

    @discord.ui.button(label="raise", style=discord.ButtonStyle.blurple, custom_id="raise", disabled=True)
    async def raise_func(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        current_player = self.current_game.players[self.current_game.current_player_index]

        self.current_game.last_player_who_raised = self.current_game.players[self.current_game.current_player_index]

        await interaction.response.send_modal(RaiseAmount(self.current_game, current_player, self.font_path, self.client, self.filename, self.games_obj, self.buttons_to_enable))

    @discord.ui.button(label="check", style=discord.ButtonStyle.blurple, custom_id="check", disabled=True)
    async def check_func(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        current_player = self.current_game.players[self.current_game.current_player_index]

        self.current_game.check_func()
        write_poker_games_to_file(self.filename, self.games_obj)

        if not all(list(map(lambda p: p.had_possibility_to_raise_or_bet, list(filter(lambda x: x.current_bet != -1, self.current_game.players))))):
            for index, player in enumerate(self.current_game.players):
                player_image = Image.open(f'data_pictures/poker/message_{player.player_id}.png')
                if player.player_id != current_player.player_id:
                    draw_player_action_on_image(player_image, self.font_path, f'{current_player.name} checked.')
                else:
                    draw_player_action_on_image(player_image, self.font_path, 'You checked.')

                draw_pot(player_image, self.current_game, self.font_path, player)
                player_image.close()

                discord_user = await self.client.fetch_user(player.player_id)
                await last_messages_to_players[index].delete()
                player_message = await discord_user.send(file=discord.File(f"data_pictures/poker/message_action_{player.player_id}.png"),
                                                         view=ButtonsMenu(self.filename, self.current_game, player.player_id, self.client, self.font_path, ['fold', 'bet', 'check']))
                last_messages_to_players[index] = player_message
        elif self.current_game.poker_round == 1:
            await self.turn_or_river()
        elif self.current_game.poker_round == 2:
            await self.turn_or_river(4)
        else:
            await self.showdown()

        await interaction.response.defer()

    @discord.ui.button(label="bet", style=discord.ButtonStyle.blurple, custom_id="bet", disabled=True)
    async def bet_func(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        current_player = self.current_game.players[self.current_game.current_player_index]

        self.current_game.last_player_who_raised = self.current_game.players[self.current_game.current_player_index]

        await interaction.response.send_modal(BetAmount(self.current_game, current_player, self.font_path, self.client, self.filename, self.games_obj, ['fold', 'call', 'raise']))

    @discord.ui.button(label="start new round", style=discord.ButtonStyle.blurple, custom_id="start_new_round", disabled=True)
    async def start_new_round_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self.start_new_round(self.current_game)
        await interaction.response.defer()

    async def flop(self):
        self.current_game.reset_possibility_to_raise()
        self.current_game.poker_round += 1
        self.current_game.current_player_index = self.current_game.get_player_index(self.current_game.dealer.player_id)
        self.current_game.next_player_who_is_not_dead()

        for player_index, player in enumerate(self.current_game.players):
            player_image = Image.open(f'data_pictures/poker/message_{player.player_id}.png')

            for index, card in enumerate(self.current_game.open_cards[:3]):
                card_value = card.get_card_integer_value() if card.value not in ['jack', 'queen', 'king', 'ace'] else card.value
                player_card_image = Image.open(f'data_pictures/playing_cards/{card_value}_{card.card_suit}.png')
                player_card_image = player_card_image.resize(open_card_size)
                x_coord, y_coord = card_places_center[index]
                player_image.paste(player_card_image, (x_coord, y_coord), player_card_image)

            for dead_player in list(filter(lambda p: p.current_bet == -1, self.current_game.players)):
                user_index_in_game = self.current_game.get_player_index_relative_to_other_player(dead_player.player_id, player.player_id)
                cross_place = cross_places[user_index_in_game]
                draw_cross(player_image, cross_place[0], cross_place[1], cross_place[2], cross_place[3])

            player_image.save(f"data_pictures/poker/message_{player.player_id}.png")

            draw_pot(player_image, self.current_game, self.font_path, player)

            discord_user = await self.client.fetch_user(player.player_id)
            await last_messages_to_players[player_index].delete()
            player_message = await discord_user.send(file=discord.File(f"data_pictures/poker/message_action_{player.player_id}.png"),
                                                     view=ButtonsMenu(self.filename, self.current_game, player.player_id, self.client, self.font_path, ['fold', 'bet', 'check']))
            last_messages_to_players[player_index] = player_message
            player_image.close()

    async def turn_or_river(self, index=3):
        self.current_game.reset_possibility_to_raise()
        self.current_game.poker_round += 1

        for player_index, player in enumerate(self.current_game.players):
            player_image = Image.open(f'data_pictures/poker/message_{player.player_id}.png')

            card = self.current_game.open_cards[index]
            card_value = card.get_card_integer_value() if card.value not in ['jack', 'queen', 'king', 'ace'] else card.value
            player_card_image = Image.open(f'data_pictures/playing_cards/{card_value}_{card.card_suit}.png')
            player_card_image = player_card_image.resize(open_card_size)
            x_coord, y_coord = card_places_center[index]
            player_image.paste(player_card_image, (x_coord, y_coord), player_card_image)

            for dead_player in list(filter(lambda p: p.current_bet == -1, self.current_game.players)):
                user_index_in_game = self.current_game.get_player_index_relative_to_other_player(dead_player.player_id, player.player_id)
                cross_place = cross_places[user_index_in_game]
                draw_cross(player_image, cross_place[0], cross_place[1], cross_place[2], cross_place[3])

            player_image.save(f"data_pictures/poker/message_{player.player_id}.png")

            draw_pot(player_image, self.current_game, self.font_path, player)

            discord_user = await self.client.fetch_user(player.player_id)
            await last_messages_to_players[player_index].delete()
            player_message = await discord_user.send(file=discord.File(f"data_pictures/poker/message_action_{player.player_id}.png"),
                                                     view=ButtonsMenu(self.filename, self.current_game, player.player_id, self.client, self.font_path, ['fold', 'bet', 'check']))
            last_messages_to_players[player_index] = player_message
            player_image.close()

    async def showdown(self, draw_open_cards=False):
        round_winners = self.current_game.showdown()
        winner_names = ', '.join(list(map(lambda p: p.name, round_winners)))

        write_poker_games_to_file(self.filename, self.games_obj)

        for player_index, player in enumerate(self.current_game.players):
            player_image = Image.open(f'data_pictures/poker/message_{player.player_id}.png')

            draw_player_action_on_image(player_image, self.font_path, f'{winner_names} won the round!')

            draw_pot(player_image, self.current_game, self.font_path, player)

            # draw_open_cards
            if draw_open_cards:
                for card_index, card in enumerate(self.current_game.open_cards):
                    card_value = card.get_card_integer_value() if card.value not in ['jack', 'queen', 'king', 'ace'] else card.value
                    player_card_image = Image.open(f'data_pictures/playing_cards/{card_value}_{card.card_suit}.png')
                    player_card_image = player_card_image.resize(open_card_size)
                    x_coord, y_coord = card_places_center[card_index]
                    player_image.paste(player_card_image, (x_coord, y_coord), player_card_image)

            for other_player_index, other_player in enumerate(self.current_game.players):
                if other_player_index != player_index:
                    index_relative_to_player = self.current_game.get_player_index_relative_to_other_player(other_player.player_id, player.player_id)
                    for card_index, card in enumerate(other_player.cards):
                        card_value = card.get_card_integer_value() if card.value not in ['jack', 'queen', 'king', 'ace'] else card.value
                        player_card_image = Image.open(f'data_pictures/playing_cards/{card_value}_{card.card_suit}.png')
                        player_card_image = player_card_image.resize(other_players_card_size)
                        player_card_image = player_card_image.rotate(other_players_card_rotations[index_relative_to_player], expand=True)
                        other_players_cards_place_x = other_players_card_places[index_relative_to_player][0] + card_index * other_players_card_places_offsets[index_relative_to_player][0]
                        other_players_cards_place_y = other_players_card_places[index_relative_to_player][1] + card_index * other_players_card_places_offsets[index_relative_to_player][1]
                        player_image.paste(player_card_image, (other_players_cards_place_x, other_players_cards_place_y), player_card_image)

            player_image.save(f"data_pictures/poker/message_{player.player_id}.png")

            draw_pot(player_image, self.current_game, self.font_path, player)
            player_image.close()

            discord_user = await self.client.fetch_user(player.player_id)
            await last_messages_to_players[player_index].delete()

            buttons_to_enable_after_showdown = ['start_new_round'] if player.player_id == self.current_game.game_author_id else []

            player_message = await discord_user.send(file=discord.File(f"data_pictures/poker/message_action_{player.player_id}.png"),
                                                     view=ButtonsMenu(self.filename, self.current_game, player.player_id, self.client, self.font_path, buttons_to_enable_after_showdown))
            last_messages_to_players[player_index] = player_message
            player_image.close()

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
        poker_background = Image.open("data_pictures/poker/poker_background_big_768x432.png")

        if not os.path.exists('data_pictures/avatars'):
            os.mkdir('data_pictures/avatars')

        poker_background = await draw_right_panel_on_image(self.client, current_game, poker_background, self.font_path)

        # Display player cards
        await display_player_cards_and_avatars(self.filename, current_game, poker_background, self.client, self.font_path, ['fold', 'call', 'raise'], draw_player_action=True)
        poker_background.close()

        write_poker_games_to_file(self.filename, games_obj)


async def setup(client):
    await client.add_cog(Poker(client))
