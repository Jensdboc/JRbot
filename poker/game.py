import math
from random import choice
from typing import List

import discord

from poker.card import Deck
from poker.card_combinations import compare_card_combinations_of_players
from poker.constants import game_states
from poker.players.bot import Bot
from poker.players.player import Player


class Game:
    """
    Class representing a poker game.
    """
    def __init__(self, player: discord.User, poker_start_message_id: int):
        self.game_author_id = player.id
        self.start_amount = 1000
        self.players: List[Player] = [Player(player.id, player.display_name, amount_of_credits=self.start_amount)]
        self.small_blind = 5
        self.big_blind = 2 * self.small_blind
        self.raise_lower_bound = 10
        self.poker_start_message_id = poker_start_message_id
        self.round_number = 0

        self.state = game_states["Starting"]
        self.open_cards = []
        self.deck = Deck()
        self.current_player_index = 0
        self.last_player_who_raised = []
        self.pot = self.small_blind + self.big_blind
        self.dealer: Player = self.players[0]
        self.small_blind_player, self.big_blind_player = None, None
        self.round_winners: List[Player] = []

        self.poker_round = 0

    def add_player(self, player: discord.User) -> str:
        """
        Add a players to the starting poker game.

        :param player: The players.
        :return: The description of the starting embed.
        """
        if (player.id, player.display_name) not in list(map(lambda x: (x.player_id, x.name), self.players)):
            self.players.append(Player(player.id, player.display_name, amount_of_credits=self.start_amount))
        return "Current players: \n>" + '\n'.join(list(map(lambda x: x.name, self.players)))

    def add_bot(self, bots_level) -> None:
        """
        Add a bot to the starting poker game.

        :param bots_level: The level of the bot.
        :return: The description of the starting embed.
        """
        possible_ids = set(range(10)).difference(set(map(lambda p: p.player_id, self.players)))
        bot_id = choice(list(possible_ids))
        bot = Bot(bot_id, f'bot_{bot_id}', self.start_amount, bots_level)
        self.players.append(bot)

    def remove_player(self, player: discord.User) -> str:
        """
        Remove a players to the starting poker game.

        :param player: The players.
        :return: The description of the starting embed.
        """
        self.players = list(filter(lambda x: x.player_id != player.id or x.name != player.display_name, self.players))
        return "Current players: \n>" + '\n'.join(list(map(lambda x: x.name, self.players)))

    def get_real_players(self):
        return list(filter(lambda p: not p.is_bot, self.players))

    def get_dead_players(self):
        return list(filter(lambda p: p.is_dead, self.players))

    def get_player_from_id(self, player_id: int) -> Player:
        index = 0
        p = self.players[index]
        while p.player_id != player_id:
            index += 1
            p = self.players[index]
        return p

    def next_player(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def next_player_who_is_not_dead(self):
        self.next_player()
        while self.players[self.current_player_index].is_dead or self.players[self.current_player_index].amount_of_credits == 0:
            self.next_player()

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
        self.players[self.current_player_index].amount_of_credits -= self.players[self.current_player_index].current_bet
        self.players[self.current_player_index].is_dead = True
        self.next_player_who_is_not_dead()

        next_player = self.current_player_index

        self.next_player_who_is_not_dead()

        if self.current_player_index == next_player:
            return 'start_new_round'

        self.current_player_index = next_player
        return 'continue_round'

    def call(self):
        max_bet = max(list(map(lambda x: x.current_bet, self.players)))
        if max_bet <= self.players[self.current_player_index].amount_of_credits:
            self.pot += (max_bet - self.players[self.current_player_index].current_bet)
            self.players[self.current_player_index].current_bet = max_bet
        elif self.players[self.current_player_index].current_bet != self.players[self.current_player_index].amount_of_credits:
            self.pot += (self.players[self.current_player_index].amount_of_credits - self.players[self.current_player_index].current_bet)
            self.players[self.current_player_index].current_bet = self.players[self.current_player_index].amount_of_credits
        self.players[self.current_player_index].had_possibility_to_raise_or_bet = True

        self.next_player()
        while self.players[self.current_player_index].is_dead or self.players[self.current_player_index].amount_of_credits == 0:
            self.next_player()

    def raise_func(self, value):
        self.pot += (value - self.players[self.current_player_index].current_bet)
        self.players[self.current_player_index].current_bet = value
        self.players[self.current_player_index].had_possibility_to_raise_or_bet = True

        self.raise_lower_bound = value * 2

        self.next_player()
        while self.players[self.current_player_index].is_dead or self.players[self.current_player_index].amount_of_credits == 0:
            self.next_player()

    def check_func(self):
        self.players[self.current_player_index].had_possibility_to_raise_or_bet = True

        self.next_player()
        while self.players[self.current_player_index].is_dead or self.players[self.current_player_index].amount_of_credits == 0:
            self.next_player()

    def showdown(self, round_winner: Player = None) -> List[Player]:
        undead_players = list(filter(lambda p: not p.is_dead and p.amount_of_credits != 0, self.players))

        if round_winner is None:
            best_players = [undead_players[0]]

            for player in undead_players[1:]:
                card_comparison = compare_card_combinations_of_players(best_players[0].cards + self.open_cards, player.cards + self.open_cards)

                if card_comparison == 'player_two':
                    best_players = [player]
                elif card_comparison == 'tie':
                    best_players.append(player)
        else:
            best_players = [round_winner]

        pot_split, unused_credits = math.floor(self.pot / len(best_players)), self.pot % len(best_players)

        for player in best_players:
            player.amount_of_credits += (pot_split - player.current_bet)

        for player in list(filter(lambda p: p.player_id not in list(map(lambda x: x.player_id, best_players)) and p.amount_of_credits != 0, undead_players)):
            player.amount_of_credits -= player.current_bet

        for player_index in self.last_player_who_raised[::-1]:
            if self.players[player_index].amount_of_credits != 0:
                self.players[player_index].amount_of_credits += unused_credits
                break

        self.round_winners = best_players

        return best_players

    def check_same_bets(self):
        undead_players = list(filter(lambda x: not x.is_dead and x.amount_of_credits != 0, self.players))
        return len(set(map(lambda player: player.current_bet, list(filter(lambda p: p.amount_of_credits != p.current_bet, undead_players))))) in [0, 1]

    def deal_player_cards(self):
        for _ in range(2):
            for player in self.players[self.current_player_index:] + self.players[:self.current_player_index]:
                player.cards.append(self.deck.cards[0])
                del self.deck.cards[0]

    def deal_open_cards(self):
        self.open_cards.extend(self.deck.cards[:5])

    def reset_possibility_to_raise(self):
        for player in self.players:
            player.had_possibility_to_raise_or_bet = False

    def reset_game_logic(self):
        # blinds
        self.current_player_index = self.players.index(self.dealer)
        self.next_player_who_is_not_dead()
        small_blind_index, big_blind_index = self.current_player_index, (self.current_player_index + 1) % len(self.players)

        self.small_blind_player, self.big_blind_player = self.players[small_blind_index], self.players[big_blind_index]
        while self.small_blind_player.amount_of_credits == 0:
            small_blind_index = (small_blind_index + 1) % len(self.players)
            self.small_blind_player = self.players[small_blind_index]
        while self.big_blind_player.amount_of_credits == 0:
            big_blind_index = (big_blind_index + 1) % len(self.players)
            self.big_blind_player = self.players[big_blind_index]

        self.last_player_who_raised = [self.current_player_index]
        self.small_blind_player.current_bet = self.small_blind if self.small_blind <= self.small_blind_player.amount_of_credits else self.small_blind_player.amount_of_credits
        self.big_blind_player.current_bet = self.big_blind if self.big_blind <= self.big_blind_player.amount_of_credits else self.big_blind_player.amount_of_credits

        self.pot = self.small_blind_player.current_bet + self.big_blind_player.current_bet

        self.raise_lower_bound = int(self.start_amount / 100)

        # deal players cards
        self.deal_player_cards()

        # deal open cards
        self.deal_open_cards()

        self.next_player_who_is_not_dead()
        self.next_player_who_is_not_dead()

        self.poker_round = 0

        self.reset_possibility_to_raise()

    def on_game_start(self):
        """
        Start the poker game with the selected settings and players.
        """
        possible_starters = []
        for index, player in enumerate(self.players):
            if not player.is_bot:
                possible_starters.append(self.players[(index - 3) % len(self.players)])

        self.dealer = choice(possible_starters)
        self.state = game_states["Playing"]

        self.reset_game_logic()

    def start_new_round(self):
        # game logic
        for player in self.players:
            if player.amount_of_credits != 0:
                player.is_dead = False

            player.cards = []
            player.current_bet = 0

        self.open_cards = []
        self.deck = Deck()
        self.current_player_index = 0
        self.round_number += 1
        if self.round_number % 20 == 0:
            self.big_blind += 10
            self.small_blind = self.big_blind // 2

        dealer_index = (self.get_player_index(self.dealer.player_id) + 1) % len(self.players)
        self.dealer = self.players[dealer_index]
        while self.dealer.amount_of_credits == 0:
            dealer_index = (dealer_index + 1) % len(self.players)
            self.dealer = self.players[dealer_index]
        self.reset_game_logic()

    def game_finished(self):
        return len(list(filter(lambda p: p.amount_of_credits > 0, self.players))) == 1
