import json
import urllib.request

from utils.json_handler import load_breeds


def get_breeds_all():
    # TODO: This might not be used
    raise NotImplementedError
    '''
    Returns the list of dog breeds

    Returns:
    list: The list of dog breeds
    '''
    breeds = load_breeds('data/breeds.json')
    return breeds


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


def get_breed_id(breed_name: str) -> int:
    # TODO: This might not be used
    raise NotImplementedError
    '''
    Returns the breed id of the given breed name

    Parameters:
    breed_name (str): The name of the breed

    Returns:
    int: The breed id
    '''
    breeds = load_breeds('data/breeds.json')
    for breed in breeds:
        if breed['name'].lower() == breed_name.lower():
            return breed['id']
    return None


def get_random_dog():
    '''
    Returns a random dog image and its details

    Returns:
    tuple: A tuple containing the dog image url and its details
    '''
    # Gets a random dog image
    with urllib.request.urlopen(f"https://api.thedogapi.com/v1/images/search?") as url:
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
        with urllib.request.urlopen(f"https://api.thedogapi.com/v1/images/search?breed_ids={breed_id}") as url:
            dog = json.loads(url.read().decode())[0]
    except IndexError:
        return None, None

    # Gets the details of the dog
    with urllib.request.urlopen(f"https://api.thedogapi.com/v1/images/{dog['id']}") as url:
        detail = json.loads(url.read().decode())

    return dog['url'], detail
