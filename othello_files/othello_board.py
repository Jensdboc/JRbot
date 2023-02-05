import itertools

def get_neighbors(row, column):
    return [[x2, y2] for x2 in range(row - 1, row + 2)
                     for y2 in range(column - 1, column + 2)
                     if (-1 < row <= 7 and
                               -1 < column <= 7 and
                               (row != x2 or column != y2) and
                               (0 <= x2 <= 7) and
                               (0 <= y2 <= 7))]

def no_wall_hit(position):
    return -1 < position[0] < 8 and -1 < position[1] < 8

def map_neutral_to_space(token):
    if len(token) == 0:
        return '🟩'
    return token

class Board:
    def __init__(self, author, message):
        board = [[''] * 8 for _ in range(8)]
        for j in range(3, 5):
            board[j][j] = '⬜'
            board[-j - 1][j] = '⬛'

        self.board = board
        self.turn = 'black'
        self.number_of_moves = 0
        self.black_played = [28, 35]
        self.white_played = [27, 36]
        self.possible_moves_with_direction = {}

        self.author = author
        self.message = message

    def display(self):
        numbers = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']
        copy_board = self.board.copy()
        for index, row in enumerate(copy_board):
            copy_board[index] = list(map(map_neutral_to_space, row))
        te_printen = '🟦0️⃣1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣\n'
        for index, row in enumerate(copy_board):
            #te_printen += ('    ' + ' '.join(['-'] * 8) + '\n')
            te_printen += (numbers[index] + ''.join(row) + '\n')
        #te_printen += ('    ' + ' '.join(['-'] * 8))
        return te_printen

    def turn_token(self, position, player, other_player):
        self.number_of_moves += 1
        start_position = position

        for direction in self.possible_moves_with_direction.get(position[0] * 8 + position[1]):
            position = [position[0] + direction[0], position[1] + direction[1]]
            while no_wall_hit(position):
                if self.board[position[0]][position[1]] == other_player:
                    if player == '⬜':
                        self.white_played.append(position[0] * 8 + position[1])
                        self.black_played.remove(position[0] * 8 + position[1])
                    else:
                        self.black_played.append(position[0] * 8 + position[1])
                        self.white_played.remove(position[0] * 8 + position[1])
                    self.board[position[0]][position[1]] = player
                    position = [position[0] + direction[0], position[1] + direction[1]]
                else:
                    break

            position = start_position

        self.possible_moves_with_direction = {}

    def legal_moves(self):
        player = '⬛' if self.turn == 'black' else '⬜'
        other_player = '⬛' if player == '⬜' else '⬜'
        actions = []

        tokens_other_player = self.black_played if player == '⬜' else self.white_played

        for index in tokens_other_player:
            row, column = index // 8, index % 8
            neighbors = get_neighbors(row, column)
            for neighbor in neighbors:
                if len(self.board[neighbor[0]][neighbor[1]]) == 0:
                    position = neighbor
                    direction = [row - neighbor[0], column - neighbor[1]]
                    position = [position[0] + direction[0], position[1] + direction[1]]
                    first_other_color = False
                    enclosed = False
                    while no_wall_hit(position):
                        if self.board[position[0]][position[1]] == other_player:
                            first_other_color = True
                        elif self.board[position[0]][position[1]] == player:
                            if first_other_color:
                                enclosed = True
                            break
                        else:
                            break
                        position = [position[0] + direction[0], position[1] + direction[1]]

                    if first_other_color and enclosed:
                        actions.append(neighbor)
                        if neighbor[0] * 8 + neighbor[1] in self.possible_moves_with_direction:
                            self.possible_moves_with_direction.get(neighbor[0] * 8 + neighbor[1]).append(direction)
                        else:
                            self.possible_moves_with_direction[neighbor[0] * 8 + neighbor[1]] = [direction]

        actions.sort()
        actions = list(actions for actions,_ in itertools.groupby(actions))
        return actions

    def game_finished(self):
        dic = self.possible_moves_with_direction.copy()
        legal_moves_player = self.legal_moves()
        self.turn = 'white' if self.turn == 'black' else 'black'
        legal_moves_other_player = self.legal_moves()
        self.turn = 'white' if self.turn == 'black' else 'black'
        self.possible_moves_with_direction = dic
        return len(legal_moves_player) == 0 and len(legal_moves_other_player) == 0
