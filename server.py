from socket import *
import sys

# key-value store
key_value = {}
# counter store
counter = {} 

def parse(header):
    # array of non-empty substrings delimited with white-spaces 
    split = header.split(" ")
    method = split[0]
    path = (split[1].split("/"))[1]
    key = (split[1].split("/"))[2]
    len = -1

    if (not (path == "key" or path == "counter")): # path here is case-sensitive
        path = ""
    
    if (method.upper() == "GET" or method.upper() == "DELETE"):
        return [method, path, key]

    if ("Content-Length" in split):
        idx = split.index("Content-Length")
        len = int(split[idx + 1])
    
    return [method, path, key, len]


serverPort = 2105
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen()
print('Server is ready to receive message')
connectionSocket, clientAddr = serverSocket.accept()
message = connectionSocket.recv(2048)
connectionSocket.send(message)
connectionSocket.close()

# TODO
# Read header request 1 byte at a time to account for intermittent transmission
# if GET/DELETE, validate path and key -> if path empty means is wrong
# if POST, get body and validate path, key and length -> if path empty or len == -1 means its wrong