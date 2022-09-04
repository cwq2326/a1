from socket import *
from sqlite3 import connect
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
def execute(parsedMessage):
    method = parsedMessage[0]
    path = parsedMessage[1]
    key = parsedMessage[2]
    
    if method == "GET":
        if key not in key_value:
            return '404 NotFound  '
        # get key-value
        if path == "key":
            body = key_value.get(key)
            # get counter
            count = counter.get(key, 'Infinity')
            # decrement counter
            if count != 'Infinity':
                counter.update({key: count - 1})
        # get counter
        if path == "counter":
            body = counter.get(key, 'Infinity')
        
        return '200 OK content-length ' + len(body) + '  ' + body

    if method == "POST":
        length = parsedMessage[3]
        # POST key-value
        if path == "key":
            if key in key_value:
                return '405 MethodNotAllowed  '
            value = b'' # value is a binary string
            while (value < length):
                connectionSocket.recv(1) # handle intermittent connection
            key_value.update({key: value})
        # POST counter
        if path == "counter":
            # key does not exist in key-value
            if key not in key_value:
                return '405 MethodNotAllowed  '
            # key does not exist in key-value
            else:
                # insertion
                if counter.get(key) == None:
                    counter.update({key: length})
                # update
                else:
                    counter[key] += value
                return '200 OK  '

    if method == "DELETE":
        # non-existent key
        if key not in key_value:
            return '404 NotFound  '
        # DELETE key-value
        if path == "key":
            # counter value does not exist
            if key not in count:
                body = key_value.pop(key, None)
                return '200 OK content-length ' + len(body) + '  ' + body
            else: 
                return '405 MethodNotAllowed  '
        # DELETE counter
        if path == "counter":
            # counter value does not exist
            if key not in count:
                return '404 NotFound  '
            # counter value exist
            else:
                body = counter.pop(key, None)
                return '200 OK content-length ' + len(body) + '  ' + body