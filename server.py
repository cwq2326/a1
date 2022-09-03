from socket import *
import sys

# key-value store
key_value = {}
# counter store
counter = {} 

def parse(header):
    method = ""
    path = ""
    key = ""
    length = -1

    if (header[0:3].upper() == "GET"):
        method = "GET"
    elif (header[0:6].upper() == "DELETE"):
        method = "DELETE"
    else:
        method ="POST"

    if (header[len(method)+2:len(method)+5] == "key"):
        path = "key"
    elif (header[len(method)+2:len(method)+9] == "counter"):
        path = "counter"

    # GET/DELETE CLAUSE
    if (method == "GET" or method == "DELETE"):
        key = header[len(method) + len(path) + 3:]
        return [method, path, key]
    # POST CLAUSE
    else:
        for i in range(len(method) + len(path) + 3, len(header)):
          if (header[i] == " "):
            break
          key+=header[i]
        length = header[len(method) + len(path) + len(key) + 19:]
        return [method, path, key, length]

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
# if GET/DELETE, validate path and key
# if POST, get body and validate path, key and length