import asyncio
import random


def random_score(current_game, current_player_index):
    return current_game.players[current_player_index].amount_of_credits - current_game.start_amount


async def random_move(available_moves):
    await asyncio.sleep(2)
    return random.choice(available_moves)
