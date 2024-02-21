import asyncio
import random
from typing import List

import numpy as np

from poker.card import Card
from poker.constants import map_card_value_to_integer, suits


def random_score(current_game, current_player_index):
    return current_game.players[current_player_index].amount_of_credits - current_game.start_amount


async def random_move(available_moves, raise_lower_bound, raise_upper_bound, bet_lower_bound, bet_upper_bound, viewable_cards: List[Card]):
    await asyncio.sleep(2)

    if 'raise' in available_moves and raise_lower_bound > raise_upper_bound:
        available_moves.remove('raise')

    if 'bet' in available_moves and bet_lower_bound > bet_upper_bound:
        available_moves.remove('bet')

    print(list(map(lambda card: f'{card.card_suit} {card.value}', viewable_cards)))
    print(calculate_chance_on_winning(viewable_cards))

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


# inspiration: https://ggpoker.be/leren-pokeren/poker-school/poker-hands-odds/
def calculate_chance_on_winning(cards: List[Card]):
    probabilities = [0.00000154, 0.0000139, 0.000240, 0.001441, 0.001965, 0.003925, 0.021128, 0.047539, 0.422569, 0.501177]
    odds = [649739 / 649740, 72192 / 72193, 4164 / 4165, 693 / 694, 508 / 509, 254 / 255, 46.3 / 47.3, 20 / 21, 1.37 / 2.37, 0.995 / 1.995]

    if len(cards) >= 5:
        if has_royal_flush(cards):
            return odds[0]

        if has_straight_flush(cards):
            return odds[1]

    if len(cards) >= 4 and has_x_of_a_kind(cards, 4):
        return odds[2]

    if len(cards) >= 5:
        if has_full_house(cards):
            return odds[3]

        if has_flush(cards):
            return odds[4]

        if has_straight(cards):
            return odds[5]

    if len(cards) >= 3 and has_x_of_a_kind(cards, 3):
        return odds[6]

    if len(cards) >= 4 and has_x_pair(cards, 2):
        return odds[7]

    if len(cards) >= 2 and has_x_pair(cards, 1):
        return odds[8]

    return (len(cards) / 7) * sum([x * y for x, y in zip(probabilities, odds)])


def has_royal_flush(cards: List[Card]) -> bool:
    """
    Check if a royal flush is present.

    :param cards: List of cards.

    :return: True if royal flush, else False.
    """
    suit_to_cards = {suit: [] for suit in suits}
    for card in cards:
        suit_to_cards[card.card_suit].append(card)

    for suit, suit_cards in suit_to_cards.items():
        card_values = list(map(lambda card: card.get_card_integer_value(), suit_cards))

        card_values.sort()
        if len(card_values) >= 5 and card_values[-5:] == [10, 11, 12, 13, 14]:
            return True

    return False


def has_straight_flush(cards: List[Card]) -> bool:
    """
    Check if a straight flush is present.

    :param cards: List of cards.

    :return: True if straight flush, else False.
    """
    suit_to_cards = {suit: [] for suit in suits}
    for card in cards:
        suit_to_cards[card.card_suit].append(card)

    for suit, suit_cards in suit_to_cards.items():
        card_integer_values = [list(sorted(map(lambda card: card.get_card_integer_value(), suit_cards)))]

        if len(card_integer_values[0]) >= 5:
            if 14 in card_integer_values[0]:
                flush_with_ace = card_integer_values[0][:]
                flush_with_ace[flush_with_ace.index(14)] = 1
                card_integer_values.append(list(sorted(flush_with_ace)))

            for chance_on_flush in card_integer_values:
                for i in range(len(chance_on_flush) - 4):
                    if chance_on_flush[i:i + 5] == list(range(chance_on_flush[i], chance_on_flush[i] + 5)):
                        return True

    return False


def has_x_of_a_kind(cards: List[Card], n: int) -> bool:
    """
    Check if an x of a kind is present.

    :param cards: List of cards.
    :param n: The amount of a kind.

    :return: True if x of a kind, else False.
    """
    card_values_to_occurrences = {value: 0 for value in list(map_card_value_to_integer.keys())}
    for card in cards:
        card_values_to_occurrences[card.value] += 1

    if n in list(card_values_to_occurrences.values()):
        return True

    return False


def has_full_house(cards: List[Card]) -> bool:
    """
    Check if a full house is present.

    :param cards: List of cards.

    :return: True if full house, else False.
    """
    card_values_to_occurrences = {value: 0 for value in list(map_card_value_to_integer.keys())}
    for card in cards:
        card_values_to_occurrences[card.value] += 1

    occurrences = list(card_values_to_occurrences.values())

    if occurrences.count(3) == 2 or (3 in occurrences and 2 in occurrences):
        return True

    return False


def has_flush(cards: List[Card]) -> bool:
    """
    Check if a flush is present.

    :param cards: List of cards.

    :return: True if flush, else False.
    """
    card_suits_to_occurrences = {suit: 0 for suit in suits}
    for card in cards:
        card_suits_to_occurrences[card.card_suit] += 1

    return len(list(filter(lambda x: x >= 5, list(card_suits_to_occurrences.values())))) > 0


def has_straight(cards: List[Card]) -> bool:
    """
    Check if a straight is present.

    :param cards: List of cards.

    :return: True if straight, else False.
    """
    card_integer_values_to_occurrences = [0 for _ in range(len(map_card_value_to_integer.values()) + 1)]
    for card in cards:
        if card.value == 'ace':
            card_integer_values_to_occurrences[0] += 1
        card_integer_values_to_occurrences[map_card_value_to_integer[card.value] - 1] += 1

    consecutive_count = 0
    for index, num in enumerate(card_integer_values_to_occurrences[::-1]):
        if num > 0:
            consecutive_count += 1
            if consecutive_count == 5:
                return True
        else:
            consecutive_count = 0
    return False


def has_x_pair(cards: List[Card], n: int) -> bool:
    """
    Check if an x pair is present.

    :param cards: List of cards.
    :param n: The amount of pairs.

    :return: True if x pair, else False.
    """
    card_values_to_occurrences = {value: 0 for value in list(map_card_value_to_integer.keys())}
    for card in cards:
        card_values_to_occurrences[card.value] += 1

    occurrences = list(card_values_to_occurrences.values())

    if n == 2 and occurrences.count(2) in [2, 3]:
        return True

    return n == 1 and occurrences.count(2) == 1
