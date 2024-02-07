from typing import List

from cogs.poker.card import Card
from cogs.poker.constants import suits, map_card_value_to_integer


def royal_flush(cards: List[Card]):
    suit_to_cards = {suit: [] for suit in suits}
    for card in cards:
        suit_to_cards[card.card_suit].append(card)

    for suit, suit_cards in suit_to_cards.items():
        card_values = list(map(lambda card: card.get_card_integer_value(), suit_cards))

        card_values.sort()
        if len(card_values) >= 5 and card_values[-5:] == [10, 11, 12, 13, 14]:
            return True

    return False


def straight_flush(cards: List[Card]):
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


def four_of_a_kind(cards: List[Card]):
    card_values_to_occurrences = {value: 0 for value in list(map_card_value_to_integer.keys())}
    for card in cards:
        card_values_to_occurrences[card.value] += 1

    return 4 in list(card_values_to_occurrences.values())


def full_house(cards: List[Card]):
    card_values_to_occurrences = {value: 0 for value in list(map_card_value_to_integer.keys())}
    for card in cards:
        card_values_to_occurrences[card.value] += 1

    occurrences = list(card_values_to_occurrences.values())

    return occurrences.count(3) == 2 or (3 in occurrences and 2 in occurrences)
