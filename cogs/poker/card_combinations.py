from typing import List

from cogs.poker.card import Card


def royal_flush(cards: List[Card]):
    return len(cards) == 5 and all(map(lambda card: card.card_suit == cards[0].card_suit, cards)) and list(sorted(list(map(lambda card: card.get_card_integer_value(), cards)))) == [10, 11, 12, 13, 14]


def straight_flush(cards: List[Card]):
    if len(cards) != 5 or any(map(lambda card: card.card_suit != cards[0].card_suit, cards[1:])):
        return False

    if 'ace' in list(map(lambda card: card.value, cards)):
        card_values = [list(sorted(map(lambda card: card.get_card_integer_value() if card.value != 'ace' else 1, cards))), list(sorted(map(lambda card: card.get_card_integer_value(), cards)))]
    else:
        card_values = [list(sorted(map(lambda card: card.get_card_integer_value(), cards)))]

    for values in card_values:
        if all([True if i == 0 else values[i] - 1 == values[i - 1] for i in range(len(values))]):
            return True

    return False
