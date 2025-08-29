import os
import random
import sys
import time

import bettercam as dxcam
import cv2
from easyocr import easyocr
import numpy as np
from difflib import SequenceMatcher

sys.path.append(os.path.abspath('../'))
from utils import count_hsv_pixels, load_toml_as_dict

orig_screen_width, orig_screen_height = 1920, 1080

path = r"./state_finder/images_to_detect/"
images_with_star_drop = []

for file in os.listdir("./state_finder/images_to_detect"):
    if "star_drop" in file:
        images_with_star_drop.append(file)
# path = r"./images_to_detect/"
region_data = load_toml_as_dict("./cfg/lobby_config.toml")['template_matching']
check_brawl_stars_crashed = str(load_toml_as_dict("./cfg/general_config.toml")['check_if_brawl_stars_crashed']).lower()

def is_template_in_region(image, template_path, region):
    current_height, current_width = image.shape[:2]
    orig_x, orig_y, orig_width, orig_height = region
    width_ratio, height_ratio = current_width / orig_screen_width, current_height / orig_screen_height
    new_x, new_y = int(orig_x * width_ratio), int(orig_y * height_ratio)
    new_width, new_height = int(orig_width * width_ratio), int(orig_height * height_ratio)
    cropped_image = image[new_y:new_y + new_height, new_x:new_x + new_width]
    current_height, current_width = image.shape[:2]
    result = cv2.matchTemplate(cropped_image, load_template(template_path, current_width, current_height),
                               cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    return max_val > 0.8


def load_template(image_path, width, height):
    width_ratio, height_ratio = width / orig_screen_width, height / orig_screen_height
    image = cv2.imread(image_path)
    orig_height, orig_width = image.shape[:2]
    resized_image = cv2.resize(image, (int(orig_width * width_ratio), int(orig_height * height_ratio)))
    return resized_image

crop_region = load_toml_as_dict("./cfg/lobby_config.toml")['lobby']['trophy_observer']
reader = easyocr.Reader(['en'])


def rework_game_result(res_string):
    res_string = res_string.lower()
    if res_string in ["victory", "defeat", "draw"]:
        return res_string, 1.0

    ratios = {
        "victory": SequenceMatcher(None, res_string, 'victory').ratio(),
        "defeat": SequenceMatcher(None, res_string, 'defeat').ratio(),
        "draw": SequenceMatcher(None, res_string, "draw").ratio()
    }
    highest_ratio_string = max(ratios, key=ratios.get)

    return highest_ratio_string, ratios[highest_ratio_string]



def find_game_result(screenshot):
    # Vérifiez que screenshot est bien un numpy.ndarray
    if not isinstance(screenshot, np.ndarray):
        raise TypeError("Expected a numpy.ndarray, but got {}".format(type(screenshot)))

    # Effectuez le recadrage directement sur l'array numpy
    x1, y1, x2, y2 = crop_region
    screenshot = screenshot[y1:y2, x1:x2]

    # Appliquez l'OCR
    result = reader.readtext(screenshot)

    if len(result) == 0:
        return False

    _, text, conf = result[0]
    game_result, ratio = rework_game_result(text)
    if ratio < 0.5:
        print("Couldn't find game result")
        return False
    return True


def get_in_game_state(image):
    if is_in_end_of_a_match(image): return "end"
    if is_in_shop(image): return "shop"
    if is_in_offer_popup(image): return "popup"
    if is_in_lobby(image): return "lobby"
    if is_in_brawler_selection(image):
        return "brawler_selection"

    if count_hsv_pixels(image, (0, 0, 255), (0, 0, 255)) > 200000:
        return "play_store"

    if not is_template_in_region(image, path + "brawl_stars_icon.PNG", region_data['brawl_stars_icon']) and (check_brawl_stars_crashed == "yes" or check_brawl_stars_crashed == "true"):
        return "brawl_stars_crashed"

    if is_in_brawl_pass(image) or is_in_star_road(image):
        return "shop"

    if is_in_star_drop(image):
        return "star_drop"

    return "match"


def is_in_shop(image) -> bool:
    return is_template_in_region(image, path + 'powerpoint.png', region_data["powerpoint"])


def is_in_brawler_selection(image) -> bool:
    return is_template_in_region(image, path + 'brawler_menu_task.png', region_data["brawler_menu_task"])


def is_in_offer_popup(image) -> bool:
    return is_template_in_region(image, path + 'close_popup.png', region_data["close_popup"])


def is_in_lobby(image) -> bool:
    return is_template_in_region(image, path + 'lobby_menu.png', region_data["lobby_menu"])


def is_in_end_of_a_match(image):
    return find_game_result(image)


def is_in_brawl_pass(image):
    return is_template_in_region(image, path + 'brawl_pass_house.PNG',
                                 region_data['brawl_pass_house'])


def is_in_star_road(image):
    return is_template_in_region(image, path + "go_back_arrow.png", region_data['go_back_arrow'])


def is_in_star_drop(image):
    for image_filename in images_with_star_drop: #kept getting errors so tried changing from image to image_filename
        if is_template_in_region(image, path + image_filename, region_data['star_drop']):
            return True
    return False

def get_state(screenshot):
    screenshot = np.array(screenshot)
    screenshot_bgr = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
    start_time = time.time()
    state = get_in_game_state(screenshot_bgr)
    print(state)
    return state


