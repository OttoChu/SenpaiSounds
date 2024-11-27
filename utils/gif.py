import urllib.request
import json
from dotenv import load_dotenv
import os
import random

load_dotenv()


def get_gif_laugh():
    '''
    Returns a random laughing gif

    Returns:
    str: The url of the gif
    '''
    query = "anime laughing"
    url = f"https://api.giphy.com/v1/gifs/search?q={urllib.parse.quote(query)}&api_key={os.getenv('GIPHY_API_KEY')}&limit=10"

    with urllib.request.urlopen(url) as response:
        try:
            data = json.load(response)
            if data["data"]:
                random_gif = random.choice(data["data"])
                gif_url = random_gif["images"]["original"]["url"]
                return gif_url
        except Exception as e:
            print(e)
    return None


def get_gif_slap():
    '''
    Returns a random gif of someone slapping someone else

    Returns:
    str: The url of the gif
    '''
    query = "anime slapping"
    url = f"https://api.giphy.com/v1/gifs/search?q={urllib.parse.quote(query)}&api_key={os.getenv('GIPHY_API_KEY')}&limit=10"

    with urllib.request.urlopen(url) as response:
        try:
            data = json.load(response)
            if data["data"]:
                random_gif = random.choice(data["data"])
                gif_url = random_gif["images"]["original"]["url"]
                return gif_url
        except Exception as e:
            print(e)
    return None
