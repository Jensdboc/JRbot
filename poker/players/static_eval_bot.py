import asyncio
import random
from typing import List

import numpy as np
import math

from poker.card import Card
from poker.constants import suits


async def static_eval_move(available_moves, raise_lower_bound, raise_upper_bound, bet_lower_bound, bet_upper_bound, cards: List[Card]):
    await asyncio.sleep(2)

    if 'raise' in available_moves and raise_lower_bound > raise_upper_bound:
        available_moves.remove('raise')

    if 'bet' in available_moves and bet_lower_bound > bet_upper_bound:
        available_moves.remove('bet')

    chosen_move = random.choice(available_moves)

    print(list(map(lambda x: f'Card: {x.card_suit} {x.value}', cards)))

    print(calculate_chance_on_royal_flush(cards))
    print(calculate_chance_on_straight_flush(cards))

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
        combination_result = math.comb(cards_left_of_suit, needed_cards_of_suit)
        if combination_result == 1:
            return combination_result

        if needed_cards_of_suit <= 7 - len(cards):
            number_of_good_combinations += combination_result

    return number_of_good_combinations / total_possibilities


def calculate_chance_on_straight_flush(cards: [Card]):
    total_possibilities = math.comb(52 - len(cards), 7 - len(cards))

    combinations = {suit: {} for suit in suits}

    for i in range(1, 11):
        for suit in suits:
            combinations[suit][(i, i + 1, i + 2, i + 3, i + 4)] = 5

    for card in cards:
        suit_combinations = combinations[card.card_suit]

        for straight_flush_combination, number_of_cards_needed in suit_combinations.items():
            if card.get_card_integer_value() in straight_flush_combination or (card.get_card_integer_value() == 14 and 1 in straight_flush_combination):
                suit_combinations[straight_flush_combination] -= 1
                if suit_combinations[straight_flush_combination] == 0:
                    return 1

    number_of_good_combinations = 0
    for straight_flush_possibilities in combinations.values():
        for possibility in straight_flush_possibilities.values():
            combination_result = math.comb(13 - (5 - min(list(straight_flush_possibilities.values()))), possibility)

            if possibility <= 7 - len(cards):
                number_of_good_combinations += combination_result

    return number_of_good_combinations / total_possibilities
