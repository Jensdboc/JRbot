import os
from typing import List, Tuple

import discord
import requests
from PIL import Image, ImageDraw, ImageOps, ImageFont

from poker.card import Card
from poker.constants import right_panel_player_places, right_panel_start, avatar_size, right_panel_avatar_size, right_panel_credit_places, lower_panel_actions, background_size, own_card_size, \
    other_players_card_size, other_players_card_rotations, other_players_card_places, other_players_card_places_offsets, open_card_size, card_places_center, player_role_places
from poker.game import Player, Game
from poker.utils import Font, Text


def display_text_on_image(background: Image, font: Font, text: Text) -> Image:
    """
    Display some text on the poker background.

    :param background: The display background.
    :param font: The font of the text.
    :param text: The text to display.

    :return: The edited poker background.
    """
    font = ImageFont.truetype(font.path, font.size)
    draw = ImageDraw.Draw(background)
    draw.text(text.position, text.string, fill=text.color, font=font)

    return background


def create_circular_avatar(image: Image, size: int) -> Image:
    """
    Crop an image to a circle.

    :param image: The input image.
    :param size: The size of the circle.

    :return: The cropped image.
    """
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255)
    output = ImageOps.fit(image, mask.size, centering=(0.5, 0.5))
    output.putalpha(mask)
    return output


def display_avatars(background: Image, players: List[Player], places: List[Tuple[int, int]], directory: str, last_part_of_filename: str) -> Image:
    """
    Display avatars on the poker background.

    :param background: The display background.
    :param players: The players that took part in the action.
    :param places: The places where the avatars should be drawn
    :param directory: The directory in which the avatars are stored.
    :param last_part_of_filename: The last part of the filename of an avatar.

    :return: The edited poker background.
    """
    for p, player_place in zip(players, places):
        player_avatar = Image.open(f"{directory}{p.player_id}{last_part_of_filename}")
        background.paste(player_avatar, player_place, player_avatar)
        player_avatar.close()

    return background


async def create_and_save_avatar(client: discord.Client, player: Player, real_player: Player) -> None:
    """
    Create and save the avatar of a players if not saved yet.

    :param client: The discord client.
    :param player: The players.
    :param real_player: One of the real players in the game.
    """
    if not os.path.exists(f"data_pictures/avatars/{player.player_id}.png") or not os.path.exists(f"data_pictures/avatars/{player.player_id}_right_panel.png"):
        if player.is_bot:
            # if a players is a bot, use the default avatar
            real_discord_user = await client.fetch_user(real_player.player_id)
            avatar = real_discord_user.default_avatar
        else:
            discord_user = await client.fetch_user(player.player_id)
            avatar = discord_user.display_avatar
            if avatar is None:
                avatar = discord_user.default_avatar

        with requests.get(avatar.url) as r:
            img_data = r.content
        with open(f"data_pictures/avatars/{player.player_id}.png", 'wb') as handler:
            handler.write(img_data)

        # create the avatars and save them
        player_avatar = create_circular_avatar(Image.open(f"data_pictures/avatars/{player.player_id}.png").convert('RGBA').resize(avatar_size), avatar_size)
        player_avatar.save(f"data_pictures/avatars/{player.player_id}.png")
        player_avatar_right_panel = player_avatar.resize(right_panel_avatar_size)
        player_avatar_right_panel.save(f"data_pictures/avatars/{player.player_id}_right_panel.png")
        player_avatar.close()
        player_avatar_right_panel.close()


def draw_cross(image: Image, cross_upper_left_position: int, cross_upper_right_position: int, cross_bottom_right_position: int, cross_bottom_left_position: int) -> Image:
    """
    Draw a cross on an image.

    :param image: The image.
    :param cross_upper_left_position: The upper left position.
    :param cross_upper_right_position: The upper right position.
    :param cross_bottom_right_position: The bottom right position.
    :param cross_bottom_left_position: The bottom left position.

    :return: The edited image
    """
    draw = ImageDraw.Draw(image)
    draw.line([cross_upper_left_position, cross_bottom_right_position], fill="black", width=8)
    draw.line([cross_upper_right_position, cross_bottom_left_position], fill="black", width=8)

    return image


def draw_player_action_on_image(poker_background: Image, players: List[Player], font_path: str, action: str) -> Image:
    """
    Display the current action on the poker background.

    :param poker_background: The display background.
    :param players: The players that took part in the action.
    :param font_path: The path to the font file.
    :param action: The action to be displayed.

    :return: The edited poker background.
    """
    if len(players) == 0:
        # only display some text
        return display_text_on_image(poker_background, Font(font_path, 24), Text(action, (54, 354), (255, 255, 255)))

    # display the avatars of the players that took part in the action
    poker_background = display_avatars(poker_background, players, lower_panel_actions[len(players) - 1], 'data_pictures/avatars/', '_right_panel.png')

    # display the action of the players(s)
    font = ImageFont.truetype(font_path, 24)
    draw = ImageDraw.Draw(poker_background)
    text_width = draw.textlength(action, font=font)

    return display_text_on_image(poker_background, Font(font_path, 24), Text(action, (int(41 + ((458 - text_width) / 2)), 390), (255, 255, 255)))


def draw_right_panel_on_image(background: Image, current_game: Game, font_path: str, player: Player, draw_player_action: bool = False) -> Image:
    """
    Display the right panel of the poker background.

    :param background: The display background.
    :param current_game: The current poker game.
    :param font_path: The path to the font file.
    :param player: The players.
    :param draw_player_action: True if a players action has to be displayed (in this case that a new round started).

    :return: The edited poker background.
    """
    # display the blinds and the pot
    background = display_text_on_image(background, Font(font_path, 32), Text(f"Players: {len(current_game.players)}\nBlind: {current_game.small_blind}\n", right_panel_start, (255, 255, 255)))
    background = display_text_on_image(background, Font(font_path, 32), Text(f"Pot: {current_game.pot}", (545, 88), (255, 255, 255)))

    # display the avatars and credits + current bet on the right panel
    draw = ImageDraw.Draw(background)
    font = ImageFont.truetype(font_path, 30)
    text_color = (255, 255, 255)
    for p, player_place, text_place in zip(current_game.players, right_panel_player_places, right_panel_credit_places):
        player_avatar_right_panel = Image.open(f"data_pictures/avatars/{p.player_id}_right_panel.png")
        background.paste(player_avatar_right_panel, player_place, player_avatar_right_panel)
        player_avatar_right_panel.close()
        draw.text(text_place, f"{p.amount_of_credits}~{p.current_bet}", fill=text_color, font=font)

    # display when a new round started
    if draw_player_action:
        draw_player_action_on_image(background, [], font_path, 'A new round started!')

    # save the result
    background.save(f"data_pictures/poker/message_action_{player.player_id}.png")


async def display_current_player_cards(background: Image, cards: List[Card]) -> Image:
    """
    Display the cards of the current players.

    :param background: The display background.
    :param cards: The cards of the current players.

    :return: The edited poker background.
    """
    for index, card in enumerate(cards):
        card_value = card.get_card_integer_value() if card.value not in ['jack', 'queen', 'king', 'ace'] else card.value

        player_card_image = Image.open(f'data_pictures/playing_cards/{card_value}_{card.card_suit}.png')
        player_card_image = player_card_image.resize(own_card_size)
        background.paste(player_card_image, (198 + index * player_card_image.size[0], 242), player_card_image)

        player_card_image.close()

    return background


async def display_cards_of_another_player(background: Image, cards: List[Card], index_relative_to_current_player: int) -> Image:
    """
    Display the cards of another players.

    :param background: The display background.
    :param cards: The cards of the other players.
    :param index_relative_to_current_player: The index of the other players relative to the current players.

    :return: The edited poker background.
    """
    for card_index, card in enumerate(cards):
        card_value = card.get_card_integer_value() if card.value not in ['jack', 'queen', 'king', 'ace'] else card.value
        player_card_image = Image.open(f'data_pictures/playing_cards/{card_value}_{card.card_suit}.png').resize(other_players_card_size)
        player_card_image = player_card_image.rotate(other_players_card_rotations[index_relative_to_current_player], expand=True)
        other_players_cards_place_x = other_players_card_places[index_relative_to_current_player][0] + card_index * other_players_card_places_offsets[index_relative_to_current_player][0]
        other_players_cards_place_y = other_players_card_places[index_relative_to_current_player][1] + card_index * other_players_card_places_offsets[index_relative_to_current_player][1]
        background.paste(player_card_image, (other_players_cards_place_x, other_players_cards_place_y), player_card_image)

        player_card_image.close()

    return background


async def display_open_cards(background: Image, cards: List[Card], cards_range_start: int = 0, cards_range_end: int = 3) -> Image:
    """
    Display the open cards.

    :param background: The display background.
    :param cards: The open cards.
    :param cards_range_start: The start index.
    :param cards_range_end: The end index.

    :return: The edited poker background.
    """
    for index in range(cards_range_start, cards_range_end):
        card = cards[index - cards_range_start]
        card_value = card.get_card_integer_value() if card.value not in ['jack', 'queen', 'king', 'ace'] else card.value
        player_card_image = Image.open(f'data_pictures/playing_cards/{card_value}_{card.card_suit}.png')
        player_card_image = player_card_image.resize(open_card_size)

        x_coord, y_coord = card_places_center[index]
        background.paste(player_card_image, (x_coord, y_coord), player_card_image)

        player_card_image.close()

    return background


def display_player_roles(background: Image, current_game: Game, font_path: str, player: Player) -> Image:
    font = ImageFont.truetype(font_path, 30)
    text_color = (255, 255, 255)
    draw = ImageDraw.Draw(background)

    roles = ['S', 'B', 'D']
    role_players = [current_game.small_blind_player, current_game.big_blind_player, current_game.dealer]
    role_player_indices = list(map(lambda x: current_game.get_player_index_relative_to_other_player(x.player_id, player.player_id), role_players))

    index = 0
    for text_position_index, role in zip(role_player_indices, roles):
        if text_position_index not in role_player_indices[:index] and text_position_index != 0:
            draw.text(player_role_places[text_position_index], role, fill=text_color, font=font)
        index += 1

    return background

