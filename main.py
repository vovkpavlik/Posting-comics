from environs import Env
import os

import requests
import urllib3

from comics import get_comics_urls, get_random_comics, save_photos


def upload_url():
    params = {
        "access_token": access_token,
        "v": 5.77,
        "group_id": 202959616,
    }

    base_url = "https://api.vk.com/method/"
    response = requests.get(f"{base_url}photos.getWallUploadServer", params=params)
    return response.json()["response"]["upload_url"]


def upload_vk_photos(upload_url, directory, pic):
    with open(f"{directory}/{pic}", "rb") as file:
        files = {
            "photo": file,
        }
        response = requests.post(upload_url, files=files)
    return response.json()


def save_to_album(photos, hash, server, group_id):
    base_url = "https://api.vk.com/method/"
    params ={
        "access_token": access_token,
        "v": 5.77,
        "photo": photos,
        "hash": hash,
        "server": server,
        "group_id": group_id,
    }
    response = requests.post(f"{base_url}photos.saveWallPhoto", data=params)
    return response.json()


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
    response = requests.get(f"{base_url}wall.post", params=params)
    return response.json()


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

    upload_vk_photos = upload_vk_photos(upload_url(), directory, "comics.png")
    photos = upload_vk_photos["photo"]
    hash = upload_vk_photos["hash"]
    server = upload_vk_photos["server"]

    save_to_album = save_to_album(photos, hash, server, group_id)
    owner_id = save_to_album["response"][0]["album_id"]
    media_pic_id = save_to_album["response"][0]["id"]
    owner_pic_id = save_to_album["response"][0]["owner_id"]

    publish_comics(group_id, access_token, media_pic_id, owner_pic_id, message)
    os.remove(f"{directory}/comics.png")
