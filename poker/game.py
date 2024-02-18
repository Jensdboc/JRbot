import math
from random import choice
from typing import List

import os
import discord

from poker.card import Deck
from poker.card_combinations import compare_card_combinations_of_players
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

        self.had_possibility_to_raise_or_bet = False
        self.elo = None

        if not os.path.exists("poker_elo.txt"):
            # Create file and set elo for first player
            with open("poker_elo.txt", 'w') as elo_file:
                print("poker_elo.txt created")
                self.elo = 1000
                elo_file.write(f"{player_id} {self.elo}\n")
        else:
            # Check if player present in file and set elo
            with open("poker_elo.txt", 'r') as elo_file:
                for line in elo_file.readlines():
                    split_line = line.rstrip("\n").split(" ")
                    if self.player_id == split_line[0]:
                        self.elo = int(split_line[1])
                        pass
            # If player not present, set elo for player
            if not self.elo:
                with open("poker_elo.txt", 'a') as elo_file:
                    self.elo = 1000
                    elo_file.write(f"{player_id} {self.elo}\n")


class Game:
    """
    Class representing a poker game.
    """
    def __init__(self, player: discord.User, small_blind: int, start_amount: int, poker_start_message_id: int):
        self.game_author_id = player.id
        self.players: List[Player] = [Player(player.id, player.display_name, amount_of_credits=start_amount)]
        self.small_blind = small_blind
        self.big_blind = 2 * self.small_blind
        self.raise_lower_bound = int(start_amount / 100)
        self.start_amount = start_amount
        self.poker_start_message_id = poker_start_message_id

        self.state = game_states["Starting"]
        self.open_cards = []
        self.deck = Deck()
        self.current_player_index = 0
        self.last_player_who_raised = []
        self.pot = self.small_blind + self.big_blind
        self.dealer: Player = self.players[0]
        self.round_winners: List[Player] = []

        self.poker_round = 0

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
        while self.players[self.current_player_index].current_bet == -1 or self.players[self.current_player_index].amount_of_credits == 0:
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
        # TODO check if all players have the same amount of credits
        players_in_game = []

        this_player_index = self.current_player_index
        self.players[self.current_player_index].amount_of_credits -= self.players[self.current_player_index].current_bet
        self.players[self.current_player_index].current_bet = -1
        self.next_player()
        while this_player_index != self.current_player_index:
            if self.players[self.current_player_index].current_bet != -1 and self.players[self.current_player_index].amount_of_credits != 0:
                players_in_game.append(self.current_player_index)
                if len(players_in_game) > 1:
                    self.current_player_index = players_in_game[0]
                    break
            self.next_player()

        if self.current_player_index == this_player_index:
            return 'start_new_round'

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
        while self.players[self.current_player_index].current_bet == -1 or self.players[self.current_player_index].amount_of_credits == 0:
            self.next_player()

    def raise_func(self, value):
        self.pot += (value - self.players[self.current_player_index].current_bet)
        self.players[self.current_player_index].current_bet = value
        self.players[self.current_player_index].had_possibility_to_raise_or_bet = True

        self.raise_lower_bound = value * 2

        self.next_player()
        while self.players[self.current_player_index].current_bet == -1 or self.players[self.current_player_index].amount_of_credits == 0:
            self.next_player()

    def check_func(self):
        self.players[self.current_player_index].had_possibility_to_raise_or_bet = True

        self.next_player()
        while self.players[self.current_player_index].current_bet == -1 or self.players[self.current_player_index].amount_of_credits == 0:
            self.next_player()

    def showdown(self) -> List[Player]:
        undead_players = list(filter(lambda p: p.current_bet != -1 and p.amount_of_credits != 0, self.players))

        best_players = [undead_players[0]]

        for player in undead_players[1:]:
            card_comparison = compare_card_combinations_of_players(best_players[0].cards + self.open_cards, player.cards + self.open_cards)

            if card_comparison == 'player_two':
                best_players = [player]
            elif card_comparison == 'tie':
                best_players.append(player)

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
        undead_players = list(filter(lambda x: x.current_bet != -1 and x.amount_of_credits != 0, self.players))
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
        # TODO check if a player has enough credits
        self.current_player_index = self.players.index(self.dealer)
        self.next_player_who_is_not_dead()
        small_blind_index, big_blind_index = self.current_player_index, (self.current_player_index + 1) % len(self.players)

        small_blind, big_blind = self.players[small_blind_index], self.players[big_blind_index]
        while small_blind.amount_of_credits == 0:
            small_blind_index = (small_blind_index + 1) % len(self.players)
            small_blind = self.players[small_blind_index]
        while big_blind.amount_of_credits == 0:
            big_blind_index = (big_blind_index + 1) % len(self.players)
            big_blind = self.players[big_blind_index]

        self.last_player_who_raised = [self.current_player_index]
        small_blind.current_bet = self.small_blind if self.small_blind <= small_blind.amount_of_credits else small_blind.amount_of_credits
        big_blind.current_bet = self.big_blind if self.big_blind <= big_blind.amount_of_credits else big_blind.amount_of_credits

        self.pot = small_blind.current_bet + big_blind.current_bet

        self.raise_lower_bound = int(self.start_amount / 100)

        # deal player cards
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
        self.dealer = choice(self.players)
        self.state = game_states["Playing"]

        self.reset_game_logic()

    def start_new_round(self):
        # game logic
        for player in self.players:
            player.cards = []
            player.current_bet = 0

        self.open_cards = []
        self.deck = Deck()
        self.current_player_index = 0

        dealer_index = (self.get_player_index(self.dealer.player_id) + 1) % len(self.players)
        self.dealer = self.players[dealer_index]
        while self.dealer.amount_of_credits == 0:
            dealer_index = (dealer_index + 1) % len(self.players)
            self.dealer = self.players[dealer_index]
        self.reset_game_logic()

    def game_finished(self):
        return len(list(filter(lambda p: p.amount_of_credits > 0, self.players))) == 1
