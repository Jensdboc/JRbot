def contains_number(s):
    for char in s:
        if char.isdigit():
            return True
    return False
