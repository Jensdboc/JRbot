import random


class RandomAgent:
    def __init__(self, player):
        self.player = player

    def score(self, board):
        score = 0
        # We kijken enkel of het spel gedaan is
        if board.game_finished():
            if board.turn == self.player:
                score -= 100
            else:
                score += 100
        return score

    def move(self, board, coords):
        actions = board.legal_moves()
        return random.choice(actions) if len(actions) > 0 else []
