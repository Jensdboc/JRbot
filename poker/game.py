from random import choice

import discord

from poker.card import PlayingCards
from poker.constants import game_states


class Player:
    def __init__(self, player_id: int, name: str, amount_of_credits: int):
        self.player_id = player_id
        self.name = name

        self.cards = []
        self.current_bet = 0
        self.amount_of_credits = amount_of_credits


class Game:
    def __init__(self, player: discord.User, small_blind: int, start_amount: int, poker_start_message_id: int):
        self.players = [Player(player.id, player.display_name, amount_of_credits=start_amount)]
        self.small_blind = small_blind
        self.big_blind = 2 * self.small_blind
        self.start_amount = start_amount
        self.poker_start_message_id = poker_start_message_id

        self.state = game_states["Starting"]
        self.playing_cards = PlayingCards()
        self.current_player_index = 0

    def add_player(self, player: discord.User) -> str:
        if (player.id, player.display_name) not in list(map(lambda x: (x.player_id, x.name), self.players)):
            self.players.append(Player(player.id, player.display_name, amount_of_credits=self.start_amount))
        return "Current players: \n>" + '\n'.join(list(map(lambda x: x.name, self.players)))

    def remove_player(self, player: discord.User) -> str:
        self.players = list(filter(lambda x: x.player_id != player.id or x.name != player.display_name, self.players))
        return "Current players: \n>" + '\n'.join(list(map(lambda x: x.name, self.players)))

    def on_game_start(self):
        dealer = choice(self.players)
        self.state = game_states["Playing"]

        # blinds
        self.current_player_index = (self.players.index(dealer) + 1) % len(self.players)
        small_blind, big_blind = self.players[self.current_player_index], self.players[(self.current_player_index + 1) % len(self.players)]
        small_blind.current_bet, big_blind.current_bet = self.small_blind, self.big_blind

        # deal cards
        for _ in range(2):
            for player in self.players[self.current_player_index:] + self.players[:self.current_player_index]:
                player.cards.append(self.playing_cards.cards[0])
                del self.playing_cards.cards[0]

        self.current_player_index = (self.current_player_index + 2) % len(self.players)
