from typing import List, Tuple

from poker.card import Card
from poker.constants import suits, map_card_value_to_integer, order_of_card_combinations


def compare_ints(card_player_one: int, card_player_two: int):
    if card_player_one == card_player_two:
        return 'tie'

    if card_player_one > card_player_two:
        return 'player_one'

    return 'player_two'


def compare_list_of_ints(cards_player_one: List[int], cards_player_two: List[int]):
    for c1, c2 in zip(cards_player_one, cards_player_two):
        if c1 > c2:
            return 'player_one'

        if c2 > c1:
            return 'player_two'

    return 'tie'


def compare_card_combinations_of_players(cards_player_one: List[Card], cards_player_two: List[Card]):
    card_combination_player_one = get_card_combination_of_player(cards_player_one)
    card_combination_player_two = get_card_combination_of_player(cards_player_two)

    if order_of_card_combinations.index(card_combination_player_one[2]) < order_of_card_combinations.index(card_combination_player_two[2]):
        return 'player_one'

    if order_of_card_combinations.index(card_combination_player_one[2]) > order_of_card_combinations.index(card_combination_player_two[2]):
        return 'player_two'

    if card_combination_player_one[2] in ['straight_flush', 'four_of_a_kind', 'straight', 'three_of_a_kind']:
        return compare_ints(card_combination_player_one[1], card_combination_player_two[1])

    if card_combination_player_one[2] in ['full_house', 'flush', 'two_pair', 'one_pair', 'high_card']:
        return compare_list_of_ints(card_combination_player_one[1], card_combination_player_two[1])


def get_card_combination_of_player(cards: List[Card]):
    royal_flush_res = royal_flush(cards)
    if royal_flush_res[0]:
        return royal_flush_res

    straight_flush_res = straight_flush(cards)
    if straight_flush_res[0]:
        return straight_flush_res

    four_of_a_kind_res = four_of_a_kind(cards)
    if four_of_a_kind_res[0]:
        return four_of_a_kind_res

    full_house_res = full_house(cards)
    if full_house_res[0]:
        return full_house_res

    flush_res = flush(cards)
    if flush_res[0]:
        return flush_res

    straight_res = straight(cards)
    if straight_res[0]:
        return straight_res

    three_of_a_kind_res = three_of_a_kind(cards)
    if three_of_a_kind_res[0]:
        return three_of_a_kind_res

    two_pair_res = two_pair(cards)
    if two_pair_res[0]:
        return two_pair_res

    one_pair_res = one_pair(cards)
    if one_pair_res[0]:
        return one_pair_res

    cards = list(map(lambda card: card.get_card_integer_value(), cards))
    cards.sort()

    return True, cards[::-1], 'high_card'


def royal_flush(cards: List[Card]) -> Tuple[bool, List[int], str]:
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
            return True, [10, 11, 12, 13, 14], 'royal_flush'

    return False, [], 'royal_flush'


def straight_flush(cards: List[Card]) -> Tuple[bool, int, str]:
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
                        return True, chance_on_flush[-1], 'straight_flush'

    return False, -1, 'straight_flush'


def x_of_a_kind(cards: List[Card], n: int, kind: str = 'four_of_a_kind') -> Tuple[bool, int, str]:
    """
    Check if an x of a kind is present.

    :param cards: List of cards.
    :param x: The amount of a kind.
    :return: True if x of a kind, else False.
    """
    card_values_to_occurrences = {value: 0 for value in list(map_card_value_to_integer.keys())}
    for card in cards:
        card_values_to_occurrences[card.value] += 1

    if n in list(card_values_to_occurrences.values()):
        return True, map_card_value_to_integer[list(card_values_to_occurrences.keys())[12 - list(card_values_to_occurrences.values())[::-1].index(n)]], kind

    return False, -1, kind


def four_of_a_kind(cards: List[Card]) -> Tuple[bool, int, str]:
    """
    Check if a 4 of a kind is present.

    :param cards: List of cards.
    :return: True if 4 of a kind, else False.
    """
    return x_of_a_kind(cards, 4)


def full_house(cards: List[Card]) -> Tuple[bool, List[int], str]:
    """
    Check if a full house is present.

    :param cards: List of cards.
    :return: True if full house, else False.
    """
    card_values_to_occurrences = {value: 0 for value in list(map_card_value_to_integer.keys())}
    for card in cards:
        card_values_to_occurrences[card.value] += 1

    occurrences = list(card_values_to_occurrences.values())

    if occurrences.count(3) == 2:
        return True, [occurrences.index(3, occurrences.index(3) + 1), occurrences.index(3)], 'full_house'

    if 3 in occurrences and 2 in occurrences:
        return True, [occurrences.index(3), 12 - occurrences[::-1].index(2)], 'full_house'

    return False, [], 'full_house'


def flush(cards: List[Card]) -> Tuple[bool, List[Card], str]:
    """
    Check if a flush is present.

    :param cards: List of cards.
    :return: True if flush, else False.
    """
    card_suits_to_occurrences = {suit: 0 for suit in suits}
    for card in cards:
        card_suits_to_occurrences[card.card_suit] += 1

    card_suits_to_occurrences_keys, card_suits_to_occurrences_values = list(card_suits_to_occurrences.keys()), list(card_suits_to_occurrences.values())

    flush_list = list(filter(lambda x: x >= 5, list(card_suits_to_occurrences.values())))

    if len(flush_list) > 0:
        suit = card_suits_to_occurrences_keys[card_suits_to_occurrences_values.index(flush_list[0])]
        return True, list(sorted(list(map(lambda x: x.get_card_integer_value(), list(filter(lambda c: c.card_suit == suit, cards))[:5])), reverse=True)), 'flush'

    return False, [], 'flush'


def straight(cards: List[Card]) -> Tuple[bool, int, str]:
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
                return True, 12 - index, 'straight'
        else:
            consecutive_count = 0
    return False, -1, 'straight'


def three_of_a_kind(cards: List[Card]) -> Tuple[bool, int, str]:
    """
    Check if a 3 of a kind is present.

    :param cards: List of cards.
    :return: True if 3 of a kind, else False.
    """
    return x_of_a_kind(cards, 3, kind='three_of_a_kind')


def x_pair(cards: List[Card], n: int, kind = 'two_pair') -> Tuple[bool, List[int], str]:
    """
    Check if an x pair is present.

    :param cards: List of cards.
    :param x: The amount of pairs.
    :return: True if x pair, else False.
    """
    card_values_to_occurrences = {value: 0 for value in list(map_card_value_to_integer.keys())}
    for card in cards:
        card_values_to_occurrences[card.value] += 1

    occurrences = list(card_values_to_occurrences.values())

    if n == 2 and occurrences.count(2) == 3:
        return True, [12 - occurrences[::-1].index(2), 12 - occurrences[::-1].index(2, occurrences[::-1].index(2) + 1),
                      [12 - index for index, value in enumerate(occurrences[::-1]) if value > 0 and 12 - index not in [12 - occurrences[::-1].index(2), 12 - occurrences[::-1].index(2, occurrences[::-1].index(2) + 1)]][0]], kind

    if n == 2 and occurrences.count(2) == 2:
        return True, [12 - occurrences[::-1].index(2), 12 - occurrences[::-1].index(2, occurrences[::-1].index(2) + 1), [12 - index for index, value in enumerate(occurrences[::-1]) if value > 0 and value != 2][0]], kind

    if n == 1 and occurrences.count(2) == 1:
        sorted_card_values = [12 - index for index, value in enumerate(occurrences[::-1]) if value > 0 and value != 2]
        return True, [occurrences.index(2), sorted_card_values[0], sorted_card_values[1], sorted_card_values[2]], kind

    return False, [], kind


def two_pair(cards: List[Card]) -> Tuple[bool, List[int], str]:
    """
    Check if a 2 pair is present.

    :param cards: List of cards.
    :return: True if 2 pair, else False.
    """
    return x_pair(cards, 2)


def one_pair(cards: List[Card]) -> Tuple[bool, List[int], str]:
    """
    Check if a pair is present.

    :param cards: List of cards.
    :return: True if pair, else False.
    """
    return x_pair(cards, 1, 'one_pair')
