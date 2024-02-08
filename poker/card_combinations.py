from typing import List

from poker.card import Card
from poker.constants import suits, map_card_value_to_integer


def royal_flush(cards: List[Card]) -> bool:
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


def straight_flush(cards: List[Card]) -> bool:
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


def x_of_a_kind(cards: List[Card], n: int) -> bool:
    """
    Check if a x of a kind is present.

    :param cards: List of cards.
    :param x: The amount of a kind.
    :return: True if x of a kind, else False.
    """
    card_values_to_occurrences = {value: 0 for value in list(map_card_value_to_integer.keys())}
    for card in cards:
        card_values_to_occurrences[card.value] += 1

    return n in list(card_values_to_occurrences.values())


def four_of_a_kind(cards: List[Card]) -> bool:
    """
    Check if a 4 of a kind is present.

    :param cards: List of cards.
    :return: True if 4 of a kind, else False.
    """
    return x_of_a_kind(cards, 4)


def full_house(cards: List[Card]) -> bool:
    """
    Check if a full house is present.

    :param cards: List of cards.
    :return: True if full house, else False.
    """
    card_values_to_occurrences = {value: 0 for value in list(map_card_value_to_integer.keys())}
    for card in cards:
        card_values_to_occurrences[card.value] += 1

    occurrences = list(card_values_to_occurrences.values())

    return occurrences.count(3) == 2 or (3 in occurrences and 2 in occurrences)


def flush(cards: List[Card]) -> bool:
    """
    Check if a flush is present.

    :param cards: List of cards.
    :return: True if flush, else False.
    """
    card_suits_to_occurrences = {suit: 0 for suit in suits}
    for card in cards:
        card_suits_to_occurrences[card.card_suit] += 1

    return len(list(filter(lambda x: x >= 5, list(card_suits_to_occurrences.values())))) > 0


def straight(cards: List[Card]) -> bool:
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
    for num in card_integer_values_to_occurrences:
        if num > 0:
            consecutive_count += 1
            if consecutive_count == 5:
                return True
        else:
            consecutive_count = 0
    return False


def three_of_a_kind(cards: List[Card]) -> bool:
    """
    Check if a 3 of a kind is present.

    :param cards: List of cards.
    :return: True if 3 of a kind, else False.
    """
    return x_of_a_kind(cards, 3)


def x_pair(cards: List[Card], n: int) -> bool:
    """
    Check if a x pair is present.

    :param cards: List of cards.
    :param x: The amount of pairs.
    :return: True if x pair, else False.
    """
    card_values_to_occurrences = {value: 0 for value in list(map_card_value_to_integer.keys())}
    for card in cards:
        card_values_to_occurrences[card.value] += 1

    occurrences = list(card_values_to_occurrences.values())

    return len(list(filter(lambda x: x >= 2, occurrences))) >= n


def two_pair(cards: List[Card]) -> bool:
    """
    Check if a 2 pair is present.

    :param cards: List of cards.
    :return: True if 2 pair, else False.
    """
    return x_pair(cards, 2)


def one_pair(cards: List[Card]) -> bool:
    """
    Check if a pair is present.

    :param cards: List of cards.
    :return: True if pair, else False.
    """
    return x_pair(cards, 1)
