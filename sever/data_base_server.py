import os


path = 'data/'

def read() -> dict:
    result = {}
    clients = os.listdir(path)
    for client in clients:
        file = open(path + client, "r")
        file_names = file.read().split("\n")
        result[client] = file_names
        file.close()
    return result