import discord
from random import choice


def get_annoying_messages() -> list:
    '''
    Returns the list of annoying messages

    Returns:
    list: The list of annoying messages
    '''
    with open("./data/messages/annoying_messages.txt", "r") as f:
        return [line.strip() for line in f]


def get_laugh_message(target: discord.Member = None) -> str:
    '''
    Returns a single random message for the laugh command

    Args:
    target (discord.Member): The target of the message

    Returns:
    str: The laugh message
    '''
    if target:
        with open(".//data/messages//laugh_messages_targeted.txt", "r") as f:
            return choice([line.strip() for line in f])

    with open(".//data//messages//laugh_messages_single.txt", "r") as f:
        return choice([line.strip() for line in f])


def get_slap_message(target: discord.Member = None) -> str:
    '''
    Returns a single random message for the slap command

    Args:
    target (discord.Member): The target of the message

    Returns:
    str: The slap message
    '''
    if target:
        with open(".//data//messages//slap_messages_targeted.txt", "r") as f:
            return choice([line.strip() for line in f])

    with open(".//data//messages//slap_messages_single.txt", "r") as f:
        return choice([line.strip() for line in f])
