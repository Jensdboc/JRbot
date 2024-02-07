from random import choice

import discord

from poker.constants import game_states


class Game:
    def __init__(self, player: discord.User, small_blind: int, start_amount: int, poker_start_message_id: int):
        self.players = [(player.id, player.display_name)]
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
        if (player.id, player.display_name) not in self.players:
            self.players.append((player.id, player.display_name))
        return "Current players: \n>" + '\n'.join(list(map(lambda player: player[1], self.players)))

    def remove_player(self, player: discord.User) -> str:
        self.players.remove((player.id, player.display_name))
        return "Current players: \n>" + '\n'.join(list(map(lambda player: player[1], self.players)))
