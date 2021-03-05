import random

import requests


def get_comics_urls(comics_num):
    url = f"https://xkcd.com/{comics_num}/info.0.json"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()["num"]


def get_random_comics(comics_num):
    comics_id = random.randint(1, comics_num)
    url = f"https://xkcd.com/{comics_id}/info.0.json"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def save_photos(url, directory):
    response = requests.get(url, verify=False)
    response.raise_for_status()
    with open(f"{directory}/comics.png", "wb") as file:
        file.write(response.content)
