map_card_value_to_integer = {
    'deuce': 2,
    'three': 3,
    'four': 4,
    'five': 5,
    'six': 6,
    'seven': 7,
    'eight': 8,
    'nine': 9,
    'ten': 10,
    'jack': 11,
    'queen': 12,
    'king': 13,
    'ace': 14
}


class Card:
    def __init__(self, card_suit: str, value: str):
        assert card_suit in ['diamonds', 'clubs', 'hearts', 'spades'], 'This is not one of the four card suits!'
        assert value in list(map_card_value_to_integer.keys()), f'The value ({value}) of this card is incorrect!'

        self.card_suit = card_suit
        self.value = value

    def get_card_integer_value(self):
        return map_card_value_to_integer[self.value]
