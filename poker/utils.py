from typing import Tuple


class Text:
    def __init__(self, string: str, position: Tuple[int, int], color: Tuple[int, int, int]):
        self.string = string
        self.position = position
        self.color = color


class Font:
    def __init__(self, font_path, font_size):
        self.path = font_path
        self.size = font_size


def contains_number(s):
    """
    Check if a string contains a number.

    :param s: The string.

    :return: True if the string contains a number.
    """
    for char in s:
        if char.isdigit():
            return True
    return False
