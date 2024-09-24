import json
import urllib.request
from utils.json_handler import load_breeds
from dotenv import load_dotenv
import os

load_dotenv()


def get_breeds_keys():
    '''
    Returns the list of dog breeds keys

    Returns:
    list: The list of dog breeds keys
    '''
    breeds = load_breeds('data/breeds.json')
    return [str(keys) for keys in breeds.keys()]


def get_breeds_value():
    '''
    Returns the list of dog breeds values

    Returns:
    list: The list of dog breeds values
    '''
    breeds = load_breeds('data/breeds.json')
    return [str(values) for values in breeds.values()]


def get_random_dog():
    '''
    Returns a random dog image and its details

    Returns:
    tuple: A tuple containing the dog image url and its details
    '''
    # Gets a random dog image
    with urllib.request.urlopen(f"https://api.thedogapi.com/v1/images/search?api_key={os.getenv('CAT_TOKEN')}") as url:
        dog = json.loads(url.read().decode())[0]

    # Gets the details of the dog
    with urllib.request.urlopen(f"https://api.thedogapi.com/v1/images/{dog['id']}") as url:
        detail = json.loads(url.read().decode())

    return dog['url'], detail


def get_specific_breed_dog(breed_id):
    '''
    Returns a random dog image of a specific breed and its details

    Parameters:
    breed_id (int): The id of the breed

    Returns:
    tuple: A tuple containing the dog image url and its details
    '''
    # Gets a random dog image
    try:
        with urllib.request.urlopen(f"https://api.thedogapi.com/v1/images/search?breed_ids={breed_id}&api_key={os.getenv('CAT_TOKEN')}") as url:
            dog = json.loads(url.read().decode())[0]
    except IndexError:
        return None, None

    # Gets the details of the dog
    with urllib.request.urlopen(f"https://api.thedogapi.com/v1/images/{dog['id']}") as url:
        detail = json.loads(url.read().decode())

    return dog['url'], detail
