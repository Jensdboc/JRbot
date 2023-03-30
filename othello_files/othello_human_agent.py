class HumanAgent:
    def __init__(self, player):
        self.player = player

    def score(self, board):
        score = 0
        # We kijken enkel of het spel gedaan is
        if all(len(row[j]) != 0 for row in board.board for j in range(8)):
            if board.turn == self.player:
                score -= 100
            else:
                score += 100
        return score

    def move(self, board, coords):
        actions = board.legal_moves()
        if len(actions) == 0:
            return []

        # x = (input('Row and column of your move: ')).split(' ')
        # x = [int(x[0]), int(x[1])]
        if coords in board.legal_moves():
            return coords
        # print('Give a valid position\n')
        # return self.move(board, coords)
        return 'Give a valid position!'
