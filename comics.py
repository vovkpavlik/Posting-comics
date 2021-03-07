import requests


def get_comics(num=""):
    url = f"https://xkcd.com/{num}/info.0.json"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def save_photo(url, directory, pic):
    response = requests.get(url, verify=False)
    response.raise_for_status()
    with open(f"{directory}/{pic}", "wb") as file:
        file.write(response.content)
