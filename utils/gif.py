import urllib.request
import json
from dotenv import load_dotenv
import os

load_dotenv()


def get_gif_laugh():
    '''
    Returns a random laughing gif

    Returns:
    str: The url of the gif
    '''
    try:
        with urllib.request.urlopen(f"https://api.giphy.com/v1/gifs/random?tag=anime+laugh&api_key={os.getenv('GIPHY_API_KEY')}") as url:
            gif = json.loads(url.read().decode())['data']

    except urllib.error.HTTPError as e:
        print(e)
        return None

    return gif['images']['original']['url']


def get_gif_slap():
    '''
    Returns a random gif of someone slapping someone else

    Returns:
    str: The url of the gif
    '''
    try:
        with urllib.request.urlopen(f"https://api.giphy.com/v1/gifs/random?tag=anime+slap&api_key={os.getenv('GIPHY_API_KEY')}") as url:
            gif = json.loads(url.read().decode())['data']

    except urllib.error.HTTPError as e:
        print(e)
        return None

    return gif['images']['original']['url']
