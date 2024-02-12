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
        self.raise_lower_bound = int(start_amount / 100)
        self.start_amount = start_amount
        self.poker_start_message_id = poker_start_message_id

        self.state = game_states["Starting"]
        self.open_cards = []
        self.deck = Deck()
        self.current_player_index = 0
        self.pot = self.small_blind + self.big_blind
        self.dealer: Player = self.players[0]

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
        # TODO check if all players have the same amount of credits
        players_in_game = []

        this_player_index = self.current_player_index
        self.pot += self.players[self.current_player_index].current_bet
        self.players[self.current_player_index].amount_of_credits -= self.players[self.current_player_index].current_bet
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
            return 'start_new_round'

        return 'continue_round'

    def call(self):
        # TODO check if all players have the same amount of credits
        self.players[self.current_player_index].current_bet = max(list(map(lambda x: x.current_bet, self.players)))

        self.next_player()
        while self.players[self.current_player_index].current_bet == -1:
            self.next_player()

    def raise_func(self, value):
        self.players[self.current_player_index].current_bet = value

        self.raise_lower_bound = value * 2

        self.next_player()
        while self.players[self.current_player_index].current_bet == -1:
            self.next_player()

    def check_same_bets(self):
        undead_players = list(filter(lambda x: x.current_bet != -1, self.players))
        return all(list(map(lambda player: player.current_bet, undead_players))) == undead_players[0].current_bet

    def deal_player_cards(self):
        for _ in range(2):
            for player in self.players[self.current_player_index:] + self.players[:self.current_player_index]:
                player.cards.append(self.deck.cards[0])
                del self.deck.cards[0]

    def deal_open_cards(self):
        self.open_cards.extend(self.deck.cards[:5])

    def reset_game_logic(self):
        # blinds
        self.current_player_index = (self.players.index(self.dealer) + 1) % len(self.players)
        small_blind, big_blind = self.players[self.current_player_index], self.players[(self.current_player_index + 1) % len(self.players)]
        small_blind.current_bet, big_blind.current_bet = self.small_blind, self.big_blind

        # deal player cards
        self.deal_player_cards()

        # deal open cards
        self.deal_open_cards()

        self.current_player_index = (self.current_player_index + 2) % len(self.players)

    def on_game_start(self):
        """
        Start the poker game with the selected settings and players.
        """
        self.dealer = choice(self.players)
        self.state = game_states["Playing"]

        self.reset_game_logic()

    def start_new_round(self):
        # player logic
        player_with_bet = list(filter(lambda player: player.current_bet != -1, self.players))
        player_that_won_previous_round = player_with_bet[0]
        player_that_won_previous_round.current_bet = 0
        player_that_won_previous_round.amount_of_credits += (self.pot + sum(list(map(lambda x: x.current_bet, player_with_bet))))

        # game logic
        for player in self.players:
            player.cards = []
            player.current_bet = 0

        self.open_cards = []
        self.deck = Deck()
        self.current_player_index = 0
        self.pot = self.small_blind + self.big_blind

        self.dealer = self.players[(self.get_player_index(self.dealer.player_id) + 1) % len(self.players)]
        self.reset_game_logic()
