from poker.players.player import Player


class Bot(Player):
    def __init__(self, player_id: int, name: str, amount_of_credits: int):
        super().__init__(player_id, name, amount_of_credits)
        self.is_bot = True
