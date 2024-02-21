import os


class Player:
    """
    Class representing a player object in a poker game.
    """
    def __init__(self, player_id: int, name: str, amount_of_credits: int, is_bot=False):
        self.player_id = player_id
        self.name = name

        self.cards = []
        self.current_bet = 0
        self.amount_of_credits = amount_of_credits

        self.is_dead = False
        self.is_bot = is_bot

        self.had_possibility_to_raise_or_bet = False
        self.elo = None

        if not os.path.exists("poker_elo.txt"):
            # Create file and set elo for first player
            with open("poker_elo.txt", 'w') as elo_file:
                print("poker_elo.txt created")
                self.elo = 1000
                elo_file.write(f"{player_id} {self.elo}\n")
        else:
            # Check if player present in file and set elo
            with open("poker_elo.txt", 'r') as elo_file:
                for line in elo_file.readlines():
                    split_line = line.rstrip("\n").split(" ")
                    if self.player_id == split_line[0]:
                        self.elo = int(split_line[1])
                        pass
            # If player not present, set elo for player
            if not self.elo:
                with open("poker_elo.txt", 'a') as elo_file:
                    self.elo = 1000
                    elo_file.write(f"{player_id} {self.elo}\n")

    async def move(self, available_moves, raise_lower_bound, raise_upper_bound, bet_lower_bound, bet_upper_bound):
        pass
