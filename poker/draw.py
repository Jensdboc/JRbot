import os
from typing import List

import discord
import requests
from PIL import Image, ImageDraw, ImageOps, ImageFont

from poker.constants import player_places, right_panel_player_places, right_panel_start, avatar_size, right_panel_avatar_size, right_panel_credit_places, lower_panel_actions, background_size
from poker.game import Game, Player


async def create_and_save_avatar(client: discord.Client, player: Player, real_player: Player) -> None:
    """
    Create and save the avatar of a player if not saved yet.

    :param client: The discord client.
    :param player: The player.
    :param real_player: One of the real players in the game.
    """
    if not os.path.exists(f"data_pictures/avatars/{player.player_id}.png") or not os.path.exists(f"data_pictures/avatars/{player.player_id}_right_panel.png"):
        if player.is_bot:
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

        player_avatar = circular_avatar(Image.open(f"data_pictures/avatars/{player.player_id}.png").convert('RGBA').resize(avatar_size), avatar_size)
        player_avatar.save(f"data_pictures/avatars/{player.player_id}.png")
        player_avatar_right_panel = player_avatar.resize(right_panel_avatar_size)
        player_avatar_right_panel.save(f"data_pictures/avatars/{player.player_id}_right_panel.png")
        player_avatar.close()
        player_avatar_right_panel.close()


def draw_player_action_on_image(poker_background: Image, players: List[Player], font_path: str, action: str) -> Image:
    """
    Display current action on the poker background.

    :param poker_background: The display background.
    :param players: The players that took part in the action.
    :param font_path: The path to the font file.
    :param action: The action to be displayed.
    :return: The edited poker background.
    """
    if len(players) == 0:
        font = ImageFont.truetype(font_path, 24)
        draw = ImageDraw.Draw(poker_background)
        text_position = (54, 354)
        text_color = (255, 255, 255)
        draw.text(text_position, action, fill=text_color, font=font)

        return poker_background

    for player, player_avatar_place in zip(players, lower_panel_actions[len(players) - 1]):
        player_avatar_lower_panel = Image.open(f"data_pictures/avatars/{player.player_id}_right_panel.png")
        poker_background.paste(player_avatar_lower_panel, player_avatar_place, player_avatar_lower_panel)

    font = ImageFont.truetype(font_path, 24)
    draw = ImageDraw.Draw(poker_background)
    text_width = draw.textlength(action, font=font)
    image_width, _ = background_size

    x = 41 + ((458 - text_width) / 2)
    y = 390

    text_color = (255, 255, 255)
    draw.text((x, y), action, fill=text_color, font=font)

    return poker_background


def circular_avatar(image: Image, size: int) -> Image:
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


async def create_avatars_for_player(player: Player, current_game: Game, player_background: Image) -> Image:
    """
    Display avatars for players on their card spots.

    :param player: The player.
    :param current_game: The poker game.
    :param player_background: The display background.
    :return: The edited poker background.
    """
    for p, player_place in zip(current_game.players[current_game.get_player_index(player.player_id) + 1:] + current_game.players[:current_game.get_player_index(player.player_id)], player_places):
        player_avatar = Image.open(f"data_pictures/avatars/{p.player_id}.png")
        player_background.paste(player_avatar, player_place, player_avatar)
        player_avatar.close()

    return player_background


def draw_cross(image: Image, cross_upper_left_position: int, cross_upper_right_position: int, cross_bottom_right_position: int, cross_bottom_left_position: int) -> None:
    """
    Draw a cross on an image.

    :param image: The image.
    :param cross_upper_left_position: The upper left position.
    :param cross_upper_right_position: The upper right position.
    :param cross_bottom_right_position: The bottom right position.
    :param cross_bottom_left_position: The bottom left position.
    """
    draw = ImageDraw.Draw(image)
    draw.line([cross_upper_left_position, cross_bottom_right_position], fill="black", width=8)
    draw.line([cross_upper_right_position, cross_bottom_left_position], fill="black", width=8)


async def draw_right_panel_on_image(background, current_game, font_path, player, draw_player_action=False):
    font = ImageFont.truetype(font_path, 32)
    draw = ImageDraw.Draw(background)
    text = f"Players: {len(current_game.players)}\nBlind: {current_game.small_blind}\n"
    text_color = (255, 255, 255)
    draw.text(right_panel_start, text, fill=text_color, font=font)

    text = f"Pot: {current_game.pot}"
    text_color = (255, 255, 255)
    draw.text((545, 88), text, fill=text_color, font=ImageFont.truetype(font_path, 32))

    font = ImageFont.truetype(font_path, 30)
    for p, player_place, text_place in zip(current_game.players, right_panel_player_places, right_panel_credit_places):
        player_avatar_right_panel = Image.open(f"data_pictures/avatars/{p.player_id}_right_panel.png")
        background.paste(player_avatar_right_panel, player_place, player_avatar_right_panel)
        draw.text(text_place, f"{p.amount_of_credits}~{p.current_bet}", fill=text_color, font=font)

    if draw_player_action:
        draw_player_action_on_image(background, [], font_path, 'A new round started!')

    background.save(f"data_pictures/poker/message_action_{player.player_id}.png")
    return background
