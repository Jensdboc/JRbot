import asyncio
import random

import numpy as np


def random_score(current_game, current_player_index):
    return current_game.players[current_player_index].amount_of_credits - current_game.start_amount


async def random_move(available_moves, raise_lower_bound, raise_upper_bound, bet_lower_bound, bet_upper_bound):
    await asyncio.sleep(2)

    if 'raise' in available_moves and raise_lower_bound > raise_upper_bound:
        available_moves.remove('raise')

    if 'bet' in available_moves and bet_lower_bound > bet_upper_bound:
        available_moves.remove('bet')

    chosen_move = random.choice(available_moves)

    if chosen_move in ['raise', 'bet']:
        if chosen_move == 'raise':
            possible_values = np.array(list(range(raise_lower_bound, raise_upper_bound + 1)))
        else:
            possible_values = np.array(list(range(bet_lower_bound, bet_upper_bound + 1)))
        probabilities = np.exp(-0.01 * possible_values)
        probabilities /= probabilities.sum()
        return chosen_move, np.random.choice(possible_values, p=probabilities)

    return chosen_move, None
