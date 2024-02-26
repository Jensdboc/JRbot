import random

from poker.constants import map_card_value_to_integer, suits


class Card:
    """
    Class representing a card.
    """
    def __init__(self, card_suit: str, value: str):
        assert card_suit in suits, 'This is not one of the four card suits!'
        assert value in list(map_card_value_to_integer.keys()), f'The value ({value}) of this card is incorrect!'

        self.card_suit = card_suit
        self.value = value

    def get_card_integer_value(self) -> int:
        """
        Get the value of a card.

        :return: The value.
        """
        return map_card_value_to_integer[self.value]


class Deck:
    """
    Class representing a deck of cards.
    """
    def __init__(self):
        self.cards = []

        for suit in suits:
            for card_value in list(map_card_value_to_integer.keys()):
                self.cards.append(Card(suit, card_value))

        random.shuffle(self.cards)
