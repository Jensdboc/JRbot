from typing import List

from game import Player


def calc_probability_of_winning(players: List[Player], winners: List[Player], pot) -> None:
    # https://sradack.blogspot.com/2008/06/elo-rating-system-multiple-players.html
    N = len(players)
    K = 40
    D = 600
    new_elos = []
    denomenator = N * (N - 1) / 2

    pot_bonus = pot // (100 * N) if pot > 1000 else 0

    for player in players:
        numerator = 0
        for player_x in players:
            if player_x != player:
                numerator += 1 / (1 + 10**((player_x.elo - player.elo) / D))
        Ex = numerator / denomenator

        Sx = 1 if player in winners else 0
        difference = K * (Sx - Ex) + (lambda x: 1 if x == 1 else -1)(Sx) * pot_bonus
        new_elos.append(player.elo + difference)

    for player, new_elo in zip(players, new_elos):
        player.elo = new_elo


def print_elo(players: List[Player]):
    for player in players:
        print(f"{player.player_id}: {player.elo} elo")
    print("-------------------")


def get_players(elos: List[int]):
    players = []
    for i, elo in enumerate(elos):
        players.append(Player(f"player{i}", f"player{i}", elo))
    return players


def show_results(players, amount_of_games, winners, pot):
    print_elo(players)
    for _ in range(amount_of_games):
        calc_probability_of_winning(players, [players[winner] for winner in winners], pot)
        print_elo(players)


def test_elo():

    players = get_players([1000, 1000])
    show_results(players, 1, [0], 1001)

    # players = get_players([1000, 750])
    # show_results(players, 1, [0])

    # players = get_players([1000, 500])
    # show_results(players, 1, [0])

    # players = get_players([1000, 250])
    # show_results(players, 1, [0])

    # show_results(players, 1, [0])

    # players = get_players([1000, 750, 750])
    # show_results(players, 1, [0])

    # players = get_players([1000, 500, 500])
    # show_results(players, 1, [0])

    # players = get_players([1000, 250, 250])
    # show_results(players, 1, [0])

    # players = get_players([1000, 250, 250, 250, 250, 250, 250, 250, 250])
    # show_results(players, 10, [0])

    # players = get_players([1000, 750, 750, 750, 750, 750, 750, 750, 750])
    # show_results(players, 10, [0])

    # players = get_players([1000 for _ in range(10)])
    # show_results(players, 1, [0], 6000)

    # players = get_players([1000 for _ in range(3)])
    # show_results(players, 1, [0], 2000)

    # N = 10
    # dict = {i: 0 for i in range(0, N)}
    # players = get_players([1000 for _ in range(N)])
    # for _ in range(10):
    #     winner = min(np.random.randint(0, N) + 2, N - 1)
    #     dict[winner] += 1
    #     print(winner)
    #     show_results(players, 1, [winner])

    # print(dict)


test_elo()
