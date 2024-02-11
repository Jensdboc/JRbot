import os

import requests
from PIL import Image, ImageDraw, ImageOps

from poker.constants import player_places


def circular_avatar(image, size):
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255)
    output = ImageOps.fit(image, mask.size, centering=(0.5, 0.5))
    output.putalpha(mask)
    return output


def create_avatars_for_player(reaction, player, current_game, player_background):
    avatar_size = (42, 40)

    for p, player_place in zip(current_game.players[current_game.get_player_index(player.player_id) + 1:] + current_game.players[:current_game.get_player_index(player.player_id)], player_places):
        discord_user = reaction.message.guild.get_member(p.player_id)
        if not os.path.exists(f"data_pictures/avatars/{discord_user.id}.png"):
            avatar = discord_user.display_avatar
            if avatar is None:
                avatar = discord_user.default_avatar

            with requests.get(avatar.url) as r:
                img_data = r.content
            with open(f"data_pictures/avatars/{discord_user.id}.png", 'wb') as handler:
                handler.write(img_data)

            player_avatar = circular_avatar(Image.open(f"data_pictures/avatars/{discord_user.id}.png").convert('RGBA').resize(avatar_size), avatar_size)
            player_avatar.save(f"data_pictures/avatars/{discord_user.id}.png")
            player_avatar.close()

        player_avatar = Image.open(f"data_pictures/avatars/{discord_user.id}.png")
        player_background.paste(player_avatar, player_place, player_avatar)
        player_avatar.close()

    return player_background


def draw_cross(image, cross_upper_left_position, cross_upper_right_position, cross_bottom_right_position, cross_bottom_left_position):
    draw = ImageDraw.Draw(image)
    draw.line([cross_upper_left_position, cross_bottom_right_position], fill="black", width=40)

    # Draw the vertical line of the cross
    draw.line([cross_upper_right_position, cross_bottom_left_position], fill="black", width=40)
