import pytest

from cogs.poker.card import Card
from cogs.poker.card_combinations import royal_flush, straight_flush, four_of_a_kind


@pytest.mark.run(order=1)
def test_royal_flush():
    cards = [Card('hearts', 'jack'), Card('diamonds', 'ace'), Card('hearts', 'king'), Card('hearts', 'ten'), Card('spades', 'five'), Card('hearts', 'queen'), Card('hearts', 'ace')]

    assert royal_flush(cards), 'This should be a royal flush!'

    cards = [Card('hearts', 'five'), Card('diamonds', 'five'), Card('hearts', 'king'), Card('hearts', 'ten'), Card('spades', 'five'), Card('hearts', 'queen'), Card('hearts', 'ace')]

    assert not royal_flush(cards), "This shouldn't be a royal flush!"


@pytest.mark.run(order=2)
def test_straight_flush():
    cards_flush = [Card('hearts', 'jack'), Card('spades', 'four'), Card('hearts', 'king'), Card('hearts', 'ten'), Card('spades', 'five'), Card('hearts', 'queen'), Card('hearts', 'ace')]
    cards2_flush = [Card('hearts', 'five'), Card('spades', 'five'), Card('hearts', 'deuce'), Card('hearts', 'ace'), Card('hearts', 'four'), Card('spades', 'four'), Card('hearts', 'three')]
    cards3_flush = [Card('hearts', 'eight'), Card('spades', 'five'), Card('hearts', 'five'), Card('hearts', 'nine'), Card('hearts', 'six'), Card('spades', 'four'), Card('hearts', 'seven')]

    assert straight_flush(cards_flush) and straight_flush(cards2_flush) and straight_flush(cards3_flush), 'This should be a straight flush!'

    cards_no_flush = [Card('hearts', 'jack'), Card('spades', 'five'), Card('hearts', 'king'), Card('spades', 'four'), Card('hearts', 'nine'), Card('hearts', 'queen'), Card('hearts', 'ace')]
    cards2_no_flush = [Card('hearts', 'five'), Card('spades', 'five'), Card('hearts', 'six'), Card('hearts', 'ace'), Card('hearts', 'four'), Card('hearts', 'three'), Card('spades', 'four')]
    cards3_no_flush = [Card('hearts', 'eight'), Card('spades', 'five'), Card('hearts', 'deuce'), Card('hearts', 'nine'), Card('hearts', 'six'), Card('spades', 'four'), Card('hearts', 'seven')]

    assert not straight_flush(cards_no_flush) and not straight_flush(cards2_no_flush) and not straight_flush(cards3_no_flush), "This shouldn't be a straight flush!"


@pytest.mark.run(order=3)
def test_four_of_a_kind():
    cards = [Card('hearts', 'jack'), Card('diamonds', 'ace'), Card('diamonds', 'jack'), Card('spades', 'jack'), Card('spades', 'five'), Card('clubs', 'jack'), Card('hearts', 'ace')]

    assert four_of_a_kind(cards), 'This should be a four of a kind!'

    cards = [Card('hearts', 'jack'), Card('diamonds', 'ace'), Card('diamonds', 'jack'), Card('spades', 'jack'), Card('spades', 'five'), Card('clubs', 'ten'), Card('hearts', 'ace')]

    assert not four_of_a_kind(cards), "This shouldn't be a four of a kind!"
