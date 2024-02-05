import pytest

from cogs.poker.card import Card
from cogs.poker.card_combinations import royal_flush, straight_flush


@pytest.mark.run(order=1)
def test_royal_flush():
    cards = [Card('hearts', 'jack'), Card('hearts', 'king'), Card('hearts', 'ten'), Card('hearts', 'queen'), Card('hearts', 'ace')]

    assert royal_flush(cards), 'This should be a royal flush!'


@pytest.mark.run(order=2)
def test_straight_flush():
    cards_flush = [Card('hearts', 'jack'), Card('hearts', 'king'), Card('hearts', 'ten'), Card('hearts', 'queen'), Card('hearts', 'ace')]
    cards2_flush = [Card('hearts', 'five'), Card('hearts', 'deuce'), Card('hearts', 'ace'), Card('hearts', 'four'), Card('hearts', 'three')]
    cards3_flush = [Card('hearts', 'eight'), Card('hearts', 'five'), Card('hearts', 'nine'), Card('hearts', 'six'), Card('hearts', 'seven')]

    assert straight_flush(cards_flush) and straight_flush(cards2_flush) and straight_flush(cards3_flush), 'This should be a straight flush!'

    cards_no_flush = [Card('hearts', 'jack'), Card('hearts', 'king'), Card('hearts', 'nine'), Card('hearts', 'queen'), Card('hearts', 'ace')]
    cards2_no_flush = [Card('hearts', 'five'), Card('hearts', 'six'), Card('hearts', 'ace'), Card('hearts', 'four'), Card('hearts', 'three')]
    cards3_no_flush = [Card('hearts', 'eight'), Card('hearts', 'deuce'), Card('hearts', 'nine'), Card('hearts', 'six'), Card('hearts', 'seven')]

    assert not straight_flush(cards_no_flush) and not straight_flush(cards2_no_flush) and not straight_flush(cards3_no_flush), "This shouldn't be a straight flush!"
