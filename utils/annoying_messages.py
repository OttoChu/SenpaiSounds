def get_annoying_messages():
    '''
    Returns the list of annoying messages

    Returns:
    list: The list of annoying messages
    '''
    with open("./data/annoying_messages.txt", "r") as f:
        return [line.strip() for line in f]
