import pytest

from poker.card import Card
from poker.players.static_eval_bot import calculate_chance_on_royal_flush, calculate_chance_on_straight_flush, calculate_chance_on_four_of_a_kind, calculate_chance_on_full_house, calculate_chance_on_flush, \
    calculate_chance_on_straight, calculate_chance_on_three_of_a_kind, calculate_chance_on_two_pairs, calculate_chance_on_one_pair


@pytest.mark.run(order=11)
def test_royal_flush_chance():
    cards = [Card('hearts', 'jack'), Card('hearts', 'ace')]

    assert calculate_chance_on_royal_flush(cards), 'This is not the right probability of a royal flush!'


@pytest.mark.run(order=12)
def test_straight_flush_chance():
    cards = [Card('hearts', 'jack'), Card('hearts', 'ace')]

    assert calculate_chance_on_straight_flush(cards), 'This is not the right probability of a straight flush!'


@pytest.mark.run(order=13)
def test_four_of_a_kind_chance():
    cards = [Card('hearts', 'jack'), Card('hearts', 'ace'), Card('clubs', 'ace'), Card('diamonds', 'ace')]

    assert calculate_chance_on_four_of_a_kind(cards, 4), 'This is not the right probability of a four of a kind!'


@pytest.mark.run(order=14)
def test_full_house_chance():
    cards = [Card('hearts', 'jack'), Card('diamonds', 'jack'), Card('clubs', 'ace')]

    assert calculate_chance_on_full_house(cards), 'This is not the right probability of a full house!'


@pytest.mark.run(order=15)
def test_flush_chance():
    cards = [Card('hearts', 'jack'), Card('hearts', 'deuce')]

    assert calculate_chance_on_flush(cards), 'This is not the right probability of a flush!'


@pytest.mark.run(order=16)
def test_straight_chance():
    cards = [Card('hearts', 'jack'), Card('hearts', 'deuce'), Card('diamonds', 'deuce')]

    assert calculate_chance_on_straight(cards), 'This is not the right probability of a straight!'


@pytest.mark.run(order=17)
def test_three_of_a_kind_chance():
    cards = [Card('hearts', 'jack'), Card('clubs', 'ace'), Card('diamonds', 'ace')]

    assert calculate_chance_on_three_of_a_kind(cards), 'This is not the right probability of a three of a kind!'


@pytest.mark.run(order=18)
def test_two_pairs_chance():
    cards = [Card('hearts', 'jack'), Card('clubs', 'ace'), Card('diamonds', 'ace')]

    assert calculate_chance_on_two_pairs(cards), 'This is not the right probability of a two pair!'


@pytest.mark.run(order=19)
def test_one_pairs_chance():
    cards = [Card('hearts', 'jack'), Card('diamonds', 'ace'), Card('hearts', 'three')]

    assert calculate_chance_on_one_pair(cards), 'This is not the right probability of a one pair!'
