from environs import Env
import os

import requests
import urllib3

from comics import get_comics_urls, get_random_comics, save_photos


class VKError(Exception):
    pass


def raise_for_error(response):
    if response.get("error"):
        raise VKError(response["error"]["error_msg"])


def upload_url():
    params = {
        "access_token": access_token,
        "v": 5.77,
        "group_id": 202959616,
    }

    base_url = "https://api.vk.com/method/"
    response = requests.get(f"{base_url}photos.getWallUploadServer", params=params).json()
    raise_for_error(response)
    return response["response"]["upload_url"]


def upload_vk_photos(upload_url, directory, pic):
    with open(f"{directory}/{pic}", "rb") as file:
        files = {
            "photo": file,
        }
        response = requests.post(upload_url, files=files).json()
    raise_for_error(response)
    return response


def save_to_album(photos, hash, server, group_id):
    base_url = "https://api.vk.com/method/"
    params = {
        "access_token": access_token,
        "v": 5.77,
        "photo": photos,
        "hash": hash,
        "server": server,
        "group_id": group_id,
    }
    response = requests.post(f"{base_url}photos.saveWallPhoto", data=params).json()
    raise_for_error(response)
    return response


def publish_comics(group_id, access_token, media_pic_id, owner_pic_id, message):
    base_url = "https://api.vk.com/method/"
    params = {
        "access_token": access_token,
        "v": 5.77,
        "owner_id": f"-{group_id}",
        "from_group": 1,
        "message": message,
        "attachments": f"photo{owner_pic_id}_{media_pic_id}"
    }
    response = requests.get(f"{base_url}wall.post", params=params).json()
    raise_for_error(response)
    return response


if __name__ == '__main__':
    urllib3.disable_warnings()

    env = Env()
    env.read_env()
    app_id = env.str("APP_ID")

    if not os.path.isdir("Files"):
        os.mkdir("Files")

    access_token = env.str("ACCESS_TOKEN")
    group_id = env.str("GROUP_ID")
    directory = "Files"

    comics_urls = get_comics_urls("")
    message = get_random_comics(comics_urls)["safe_title"]

    save_photos(get_random_comics(comics_urls)["img"], directory)

    load_vk_info = upload_vk_photos(upload_url(), directory, "comics.png")
    photos = load_vk_info["photo"]
    hash = load_vk_info["hash"]
    server = "eUISWGH"
    # server = load_vk_info["server"]

    load_album_info = save_to_album(photos, hash, server, group_id)["response"][0]
    owner_id = load_album_info["album_id"]
    media_pic_id = load_album_info["id"]
    owner_pic_id = load_album_info["owner_id"]

    publish_comics(group_id, access_token, media_pic_id, owner_pic_id, message)

    os.remove(f"{directory}/comics.png")
