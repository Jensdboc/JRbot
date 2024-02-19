from poker.players.player import Player
from poker.players.random_bot import random_move


class Bot(Player):
    def __init__(self, player_id: int, name: str, amount_of_credits: int, bots_level: int = 'Easy'):
        super().__init__(player_id, name, amount_of_credits)
        self.is_bot = True
        self.level = bots_level

    def move(self, available_moves):
        if self.level == 'Easy':
            print('test')
            return await random_move(available_moves)

        return 'fold'

