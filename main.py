import os
import random

from environs import Env
import requests
import urllib3

from comics import get_comics, save_photo


class VKError(Exception):
    pass


def raise_for_error(response):
    if response.get("error"):
        raise VKError(response["error"]["error_msg"])


def get_upload_url(group_id):
    params = {
        "access_token": vk_access_token,
        "v": 5.77,
        "group_id": group_id,
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


def save_to_album(photos, hash_, server, group_id):
    base_url = "https://api.vk.com/method/"
    params = {
        "access_token": vk_access_token,
        "v": 5.77,
        "photo": photos,
        "hash": hash_,
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


if __name__ == "__main__":
    urllib3.disable_warnings()

    env = Env()
    env.read_env()
    vk_app_id = env.str("VK_APP_ID")

    vk_access_token = env.str("VK_ACCESS_TOKEN")
    vk_group_id = env.str("VK_GROUP_ID")
    directory = "Files"

    os.makedirs(directory, exist_ok=True)

    comics_count = get_comics()["num"]
    random_number = random.randint(1, comics_count)
    comics_description = get_comics(random_number)

    message = comics_description["safe_title"]

    save_photo(comics_description["img"], directory, "comics.png")
    try:
        group_description = upload_vk_photos(get_upload_url(vk_group_id), directory, "comics.png")
        photos = group_description["photo"]
        hash_ = group_description["hash"]
        server = group_description["server"]

        album_description = save_to_album(photos, hash_, server, vk_group_id)["response"][0]
        owner_id = album_description["album_id"]
        media_pic_id = album_description["id"]
        owner_pic_id = album_description["owner_id"]

        publish_comics(vk_group_id, vk_access_token, media_pic_id, owner_pic_id, message)

    finally:
        os.remove(f"{directory}/comics.png")
