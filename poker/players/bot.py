from poker.players.player import Player
from poker.players.random_bot import random_move
from poker.players.static_eval_bot import static_eval_move


class Bot(Player):
    def __init__(self, player_id: int, name: str, amount_of_credits: int, bots_level: int = 'Easy'):
        super().__init__(player_id, name, amount_of_credits)
        self.is_bot = True
        self.level = bots_level

    async def move(self, available_moves, raise_lower_bound, raise_upper_bound, bet_lower_bound, bet_upper_bound):
        if self.level == 'Easy':
            return await random_move(available_moves, raise_lower_bound, raise_upper_bound, bet_lower_bound, bet_upper_bound)

        if self.level == 'Medium':
            return await static_eval_move(available_moves, raise_lower_bound, raise_upper_bound, bet_lower_bound, bet_upper_bound, self.cards)

