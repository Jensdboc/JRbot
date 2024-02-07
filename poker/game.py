from random import choice

import discord

from poker.constants import game_states


class Player:
    def __init__(self, player_id: int, name: str):
        self.player_id = player_id
        self.name = name

        self.cards = []


class Game:
    def __init__(self, player: discord.User, small_blind: int, start_amount: int, poker_start_message_id: int):
        self.players = [Player(player.id, player.display_name)]
        self.small_blind = small_blind
        self.big_blind = 2 * self.small_blind
        self.start_amount = start_amount
        self.poker_start_message_id = poker_start_message_id

        self.dealer = None
        self.state = game_states["Starting"]

    def on_game_start(self):
        self.dealer = choice(self.players)
        self.state = game_states["Playing"]

    def add_player(self, player: discord.User) -> str:
        if (player.id, player.display_name) not in list(map(lambda x: (x.player_id, x.name), self.players)):
            self.players.append(Player(player.id, player.display_name))
        return "Current players: \n>" + '\n'.join(list(map(lambda x: x.name, self.players)))

    def remove_player(self, player: discord.User) -> str:
        self.players = list(filter(lambda x: x.player_id != player.id or x.name != player.display_name, self.players))
        return "Current players: \n>" + '\n'.join(list(map(lambda x: x.name, self.players)))
