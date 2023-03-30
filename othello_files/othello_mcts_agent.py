import random
import numpy as np
import copy
from othello_files.othello_board import Board


class Node:
    """Een top in de MCTS spelboom"""
    def __init__(self, parent, action):
        self.parent = parent  # ouder van deze top (None voor de wortel)
        self.action = action  # actie die genomen werd om hier te geraken vanuit de ouder
        self.children = []  # de kinderen van deze top
        self.explored_children = 0  # aantal kinderen die we al verkend hebben
        self.visits = 0  # aantal keer dat de top bezocht is
        self.value = 0  # lopend gemiddelde van de rollouts vanaf deze top


class MCTSAgent:
    def __init__(self, player, max_depth, rollouts, base_agent, uct_const):
        self.player = player  # voor welke speler krijgen wij rewards
        self.max_depth = max_depth  # maximale diepte per iteratie
        self.rollouts = rollouts  # aantal rollouts per iteratie
        self.base_agent = base_agent  # agent die we gebruiken als default policy
        self.uct_const = uct_const  # UCT constante

    def uct(self, node):
        """Upper Confidence Bound for trees formule"""
        if node.visits > 0 and node.parent is not None:
            return node.value + 2 * self.uct_const * np.sqrt(2 * np.log(node.parent.visits) / node.visits)
        else:
            return np.inf

    def move(self, board, coords):
        root = Node(None, None)
        for _ in range(self.rollouts):
            # start iteratie
            iter_board = Board(board.author, board.message)
            iter_board.board = copy.deepcopy(board.board)
            iter_board.turn = copy.deepcopy(board.turn)
            iter_board.number_of_moves = copy.deepcopy(board.number_of_moves)
            iter_board.black_played = copy.deepcopy(board.black_played)
            iter_board.white_played = copy.deepcopy(board.white_played)
            iter_board.possible_moves_with_direction = copy.deepcopy(board.possible_moves_with_direction)

            node = root

            # selectie
            game_finished = iter_board.game_finished()
            legal_moves = iter_board.legal_moves()
            while node.children and not game_finished and len(legal_moves) > 0:
                if node.explored_children < len(node.children):
                    child = node.children[node.explored_children]
                    node.explored_children += 1
                    node = child
                else:
                    node = max(node.children, key=self.uct)

                if iter_board.turn == 'white':
                    iter_board.board[node.action[0]][node.action[1]] = '⬜'
                    iter_board.turn_token(node.action, '⬜', '⬛')
                    iter_board.turn = 'black'
                    iter_board.white_played.append(node.action[0] * 8 + node.action[1])
                else:
                    iter_board.board[node.action[0]][node.action[1]] = '⬛'
                    iter_board.turn_token(node.action, '⬛', '⬜')
                    iter_board.turn = 'white'
                    iter_board.black_played.append(node.action[0] * 8 + node.action[1])

                game_finished = iter_board.game_finished()
                legal_moves = iter_board.legal_moves()

            # expansie
            game_finished = iter_board.game_finished()
            legal_moves = iter_board.legal_moves()
            if not game_finished and len(legal_moves) > 0:
                node.children = [Node(node, a) for a in legal_moves]
                random.shuffle(node.children)

            # rollout
            node_depth = iter_board.number_of_moves
            white_can_play = True
            black_can_play = True
            game_finished = iter_board.game_finished()
            legal_moves = iter_board.legal_moves()
            while not game_finished and iter_board.number_of_moves - node_depth < self.max_depth and len(legal_moves) > 0:
                if not white_can_play and not black_can_play:
                    break
                self.base_agent.player = iter_board.turn
                move = self.base_agent.move(iter_board, coords)
                if len(move) == 0:
                    if iter_board.turn == 'white':
                        white_can_play = False
                    else:
                        black_can_play = False
                else:
                    if iter_board.turn == 'white':
                        white_can_play = True
                        iter_board.board[move[0]][move[1]] = '⬜'
                        iter_board.turn_token(move, '⬜', '⬛')
                        iter_board.turn = 'black'
                        iter_board.white_played.append(move[0] * 8 + move[1])
                    else:
                        black_can_play = True
                        iter_board.board[move[0]][move[1]] = '⬛'
                        iter_board.turn_token(move, '⬛', '⬜')
                        iter_board.turn = 'white'
                        iter_board.black_played.append(move[0] * 8 + move[1])

                game_finished = iter_board.game_finished()
                legal_moves = iter_board.legal_moves()

            self.base_agent.player = self.player
            reward = self.base_agent.score(iter_board)

            # negamax back-propagation
            flag = -1 if iter_board.turn == self.player else 1
            while node:
                node.visits += 1
                # update de node value met een lopend gemiddelde
                node.value += (flag * reward - node.value) / node.visits
                flag *= -1
                node = node.parent
        # Maak een zet met de huidige MCTS-boom
        if len(root.children) == 0:
            return []
        node = max(root.children, key=self.uct)
        board.legal_moves()
        return node.action
