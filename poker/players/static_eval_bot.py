import asyncio
import random

import numpy as np
import math

from poker.card import Card
from poker.constants import suits


def random_score2(current_game, current_player_index):
    return current_game.players[current_player_index].amount_of_credits - current_game.start_amount


async def static_eval_move(available_moves, raise_lower_bound, raise_upper_bound, bet_lower_bound, bet_upper_bound):
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


def calculate_chance_on_royal_flush(cards: [Card]):
    total_possibilities = math.comb(52 - len(cards), 7 - len(cards))

    combinations = {suit: (5, 13) for suit in suits}

    for card in cards:
        tup = combinations[card.card_suit]
        combinations[card.card_suit] = (tup[0] - 1 if card.get_card_integer_value() >= 10 else tup[0], tup[1] - 1)

    number_of_good_combinations = 0
    for needed_cards_of_suit, cards_left_of_suit in combinations.values():
        number_of_good_combinations += math.comb(cards_left_of_suit, needed_cards_of_suit)

    return number_of_good_combinations / total_possibilities
