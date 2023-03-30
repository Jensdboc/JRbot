import copy
from othello_files.othello_board import Board


class StaticEvalAgent:
    def __init__(self, player):
        self.player = player

    def score(self, board):
        score = 0
        # calculate score based on the number of each color
        for row in range(0, 8):
            for column in range(0, 8):
                if not len(board.board[row][column]) == 0:
                    if (row == 0 and (column == 0 or column == 7)) or (row == 7 and (column == 0 or column == 7)):
                        if self.player == 'white':
                            score = score + 5 if board.board[row][column] == '⬜' else score - 5
                        else:
                            score = score + 5 if board.board[row][column] == '⬛' else score - 5
                    elif row == 0 or row == 7 or column == 0 or column == 7:
                        if self.player == 'white':
                            score = score + 3 if board.board[row][column] == '⬜' else score - 3
                        else:
                            score = score + 3 if board.board[row][column] == '⬛' else score - 3
                    else:
                        if self.player == 'white':
                            score = score + 1 if board.board[row][column] == '⬜' else score - 1
                        else:
                            score = score + 1 if board.board[row][column] == '⬛' else score - 1

        return score

    def move(self, board, coords):
        board_copy = Board(board.author, board.message)
        board_copy.board = copy.deepcopy(board.board)
        board_copy.turn = copy.deepcopy(board.turn)
        board_copy.number_of_moves = copy.deepcopy(board.number_of_moves)
        board_copy.black_played = copy.deepcopy(board.black_played)
        board_copy.white_played = copy.deepcopy(board.white_played)
        board_copy.possible_moves_with_direction = copy.deepcopy(board.possible_moves_with_direction)

        actions = board.legal_moves()
        scores = {}
        if len(actions) == 0:
            return []

        for a in actions:
            if self.player == 'white':
                board_copy.board[a[0]][a[1]] = '⬜'
                board_copy.turn_token(a, '⬜', '⬛')
                board_copy.white_played.append(a[0] * 8 + a[1])
            else:
                board_copy.board[a[0]][a[1]] = '⬛'
                board_copy.turn_token(a, '⬛', '⬜')
                board_copy.white_played.append(a[0] * 8 + a[1])

            scores[str(a[0]) + ' ' + str(a[1])] = self.score(board_copy)

            board_copy = Board(board.author, board.message)
            board_copy.board = copy.deepcopy(board.board)
            board_copy.turn = copy.deepcopy(board.turn)
            board_copy.number_of_moves = copy.deepcopy(board.number_of_moves)
            board_copy.black_played = copy.deepcopy(board.black_played)
            board_copy.white_played = copy.deepcopy(board.white_played)
            board_copy.possible_moves_with_direction = copy.deepcopy(board.possible_moves_with_direction)

        m = max(scores, key=scores.get).split(' ')
        return [int(m[0]), int(m[1])]
