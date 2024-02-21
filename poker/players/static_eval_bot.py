import asyncio
import random
from typing import List, Dict

import numpy as np
import math

from poker.card import Card
from poker.constants import suits, map_card_value_to_integer


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


def calculate_chance(turned_cards: int, combinations: Dict):
    chance = 0
    for needed_cards in combinations.values():
        if needed_cards <= 7 - turned_cards:
            temp_res = 1
            divisor = 52 - turned_cards
            for i in range(needed_cards, 0, -1):
                temp_res *= (i / divisor)
                divisor -= 1

            chance += (temp_res * math.comb(7 - turned_cards, needed_cards))

    return chance


def calculate_chance_on_royal_flush(cards: [Card]):
    combinations = {suit: 5 for suit in suits}

    for card in cards:
        combinations[card.card_suit] = combinations[card.card_suit] - 1 if card.get_card_integer_value() >= 10 else combinations[card.card_suit]
        if combinations[card.card_suit] == 0:
            return 1

    return calculate_chance(len(cards), combinations)


def calculate_chance_on_straight_flush(cards: [Card]):
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

    chance = 0
    for straight_flush_possibilities in combinations.values():
        chance += calculate_chance(len(cards), straight_flush_possibilities)

    return chance


def calculate_chance_on_x_of_a_kind(cards: [Card], n: int):
    combinations = {val: n for val in map_card_value_to_integer.values()}

    for card in cards:
        combinations[card.get_card_integer_value()] -= 1
        if combinations[card.get_card_integer_value()] == 0:
            return 1

    return calculate_chance(len(cards), combinations)


def calculate_chance_on_full_house(cards: [Card]):
    combinations = {}
    # fill combinations
    for index1, val1 in enumerate(list(map_card_value_to_integer.values())):
        for index2, val2 in enumerate(list(map_card_value_to_integer.values())[index1 + 1:]):
            if val1 != val2:
                combinations[(val1, val2)] = (3, 3)

    for card in cards:
        card_value = card.get_card_integer_value()

        for value in range(2, card_value):
            tup = combinations[(value, card_value)]
            res = (tup[0], tup[1] - 1)
            if res in [(0, 1), (1, 0)]:
                return 1
            combinations[(value, card_value)] = res

        for value in range(card_value + 1, 15):
            tup = combinations[(card_value, value)]
            res = (tup[0] - 1, tup[1])
            if res in [(0, 1), (1, 0)]:
                return 1
            combinations[(card_value, value)] = res

    chance = 0
    for needed_cards_of_values in combinations.values():
        needed_cards = needed_cards_of_values[0] + needed_cards_of_values[1] - 1 if needed_cards_of_values[0] != -1 and needed_cards_of_values[1] != -1 else needed_cards_of_values[0] + needed_cards_of_values[1]

        if needed_cards <= 7 - len(cards):
            temp_res = 1
            divisor = 52 - len(cards)

            if needed_cards_of_values[0] < 1:
                i = needed_cards_of_values[1] + 1
                for _ in range(needed_cards_of_values[1], 1, -1):
                    temp_res *= ((i + 1) / divisor)
                    i -= 1
                    divisor -= 1

                chance += (temp_res * math.comb(7 - len(cards), needed_cards_of_values[1] - 1))
            elif needed_cards_of_values[1] < 1:
                i = needed_cards_of_values[0] + 1
                for _ in range(needed_cards_of_values[0], 1, -1):
                    temp_res *= ((i + 1) / divisor)
                    i -= 1
                    divisor -= 1

                chance += (temp_res * math.comb(7 - len(cards), needed_cards_of_values[0] - 1))
            else:
                i = needed_cards_of_values[0] + needed_cards_of_values[1] + 2
                for _ in range(needed_cards_of_values[0] + needed_cards_of_values[1] - 1, 0, -1):
                    temp_res *= (i / divisor)
                    i -= 1
                    divisor -= 1

                chance += (temp_res * math.comb(7 - len(cards), needed_cards_of_values[0] - 1))

    return chance


def calculate_chance_on_flush(cards: [Card]):
    combinations = {suit: 5 for suit in suits}

    for card in cards:
        combinations[card.card_suit] -= 1
        if combinations[card.card_suit] == 0:
            return 1

    chance = 0
    for needed_cards in combinations.values():
        if needed_cards <= 7 - len(cards):
            temp_res = 1
            divisor = 52 - len(cards)
            i = (13 - (5 - needed_cards))
            for _ in range(needed_cards, 0, -1):
                temp_res *= (i / divisor)
                i -= 1
                divisor -= 1

            chance += (temp_res * math.comb(7 - len(cards), needed_cards))

    return chance


def calculate_chance_on_straight(cards: [Card]):
    combinations = {}

    for i in range(1, 11):
        combinations[(i, i + 1, i + 2, i + 3, i + 4)] = 5

    for card in cards:
        for straight_combination, number_of_cards_needed in combinations.items():
            if card.get_card_integer_value() in straight_combination or (card.get_card_integer_value() == 14 and 1 in straight_combination):
                combinations[straight_combination] -= 1
                if combinations[straight_combination] == 0:
                    return 1

    chance = 0
    for needed_cards in combinations.values():
        if needed_cards <= 7 - len(cards):
            temp_res = 1
            divisor = 52 - len(cards)
            i = 4 * needed_cards
            for _ in range(needed_cards, 0, -1):
                temp_res *= (i / divisor)
                i -= 1
                divisor -= 1

            chance += (temp_res * math.comb(7 - len(cards), needed_cards))

    return chance
