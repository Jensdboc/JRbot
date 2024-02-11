from random import choice

import discord

from poker.card import Deck
from poker.constants import game_states


class Player:
    """
    Class representing a player object in a poker game.
    """
    def __init__(self, player_id: int, name: str, amount_of_credits: int):
        self.player_id = player_id
        self.name = name

        self.cards = []
        self.current_bet = 0
        self.amount_of_credits = amount_of_credits


class Game:
    """
    Class representing a poker game.
    """
    def __init__(self, player: discord.User, small_blind: int, start_amount: int, poker_start_message_id: int):
        self.players = [Player(player.id, player.display_name, amount_of_credits=start_amount)]
        self.small_blind = small_blind
        self.big_blind = 2 * self.small_blind
        self.start_amount = start_amount
        self.poker_start_message_id = poker_start_message_id

        self.state = game_states["Starting"]
        self.open_cards = []
        self.deck = Deck()
        self.current_player_index = 0
        self.pot = self.small_blind + self.big_blind

    def add_player(self, player: discord.User) -> str:
        """
        Add a player to the starting poker game.

        :param player: The player.
        :return: The description of the starting embed.
        """
        if (player.id, player.display_name) not in list(map(lambda x: (x.player_id, x.name), self.players)):
            self.players.append(Player(player.id, player.display_name, amount_of_credits=self.start_amount))
        return "Current players: \n>" + '\n'.join(list(map(lambda x: x.name, self.players)))

    def remove_player(self, player: discord.User) -> str:
        """
        Remove a player to the starting poker game.

        :param player: The player.
        :return: The description of the starting embed.
        """
        self.players = list(filter(lambda x: x.player_id != player.id or x.name != player.display_name, self.players))
        return "Current players: \n>" + '\n'.join(list(map(lambda x: x.name, self.players)))

    def next_player(self):
        # TODO
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def get_player_index(self, user_id: int) -> int:
        for index, player in enumerate(self.players):
            if user_id == player.player_id:
                return index

    def get_player_index_relative_to_other_player(self, player_id: int, other_player_id: int) -> int:
        other_player_index_in_current_game = self.get_player_index(other_player_id)
        players = self.players[other_player_index_in_current_game:] + self.players[:other_player_index_in_current_game]

        for index, player in enumerate(players):
            if player.player_id == player_id:
                return index

    def fold(self):
        # TODO
        players_in_game = []

        this_player_index = self.current_player_index
        self.pot += self.players[self.current_player_index].current_bet
        self.players[self.current_player_index].current_bet = -1
        self.next_player()
        while this_player_index != self.current_player_index:
            if self.players[self.current_player_index].current_bet != -1:
                players_in_game.append(self.current_player_index)
                if len(players_in_game) > 1:
                    self.current_player_index = players_in_game[0]
                    break
            self.next_player()

        if self.current_player_index == this_player_index:
            # TODO end game
            print('end round')
            self.start_new_round()

    def on_game_start(self):
        """
        Start the poker game with the selected settings and players.
        """
        dealer = choice(self.players)
        self.state = game_states["Playing"]

        # blinds
        self.current_player_index = (self.players.index(dealer) + 1) % len(self.players)
        small_blind, big_blind = self.players[self.current_player_index], self.players[(self.current_player_index + 1) % len(self.players)]
        small_blind.current_bet, big_blind.current_bet = self.small_blind, self.big_blind

        # deal player cards
        for _ in range(2):
            for player in self.players[self.current_player_index:] + self.players[:self.current_player_index]:
                player.cards.append(self.deck.cards[0])
                del self.deck.cards[0]

        # deal open cards
        for _ in range(5):
            self.open_cards.append(self.deck.cards[0])
            del self.deck.cards[0]

        self.current_player_index = (self.current_player_index + 2) % len(self.players)

    def start_new_round(self):
        # TODO
        print('start new round')
