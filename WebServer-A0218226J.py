from socket import *
import sys

# server setup
serverPort = int(sys.argv[1])
serverSocket = socket(AF_INET,SOCK_STREAM) 
serverSocket.bind(('',serverPort))
serverSocket.listen(1) 
connectionSocket, clientAddr = serverSocket.accept()

# key-value store
key_value = {}
# counter store
counter = {} 

FIVE_MB = 5242880

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
            # decrement counter if exists
            if key in counter:
                counter[key] -= 1
                # remove key-value if zero
                if counter[key] <= 0:
                    counter.pop(key, None)
                    key_value.pop(key, None)

        # get counter
        if path == "counter":
            body = str(counter.get(key, 'Infinity'))
        
        return '200 OK Content-Length '.encode() + str(len(body)).encode() + '  ' + body.encode()

    if method == "POST":
        length = parsedMessage[3]
        # POST key-value
        if path == "key":
            if key in counter:
                return '405 MethodNotAllowed  '
            value = b'' # value is a binary string
            while (len(value) < max(length, FIVE_MB)):
                value += connectionSocket.recv(1) # handle intermittent connection
            key_value.update({key: value})
        # POST counter
        if path == "counter":
            # key does not exist in key-value
            if key not in key_value:
                return '405 MethodNotAllowed  '
            # key does not exist in key-value
            else:
                count = b''
                while (len(count) < max(length, FIVE_MB)):
                    count += connectionSocket.recv(1) # handle intermittent connection
                count = int(value)
                # insertion
                if counter.get(key) == None:
                    counter.update({key: count})
                # update
                else:
                    counter[key] += count
                return '200 OK  '

    if method == "DELETE":
        # non-existent key
        if key not in key_value:
            return '404 NotFound  '
        # DELETE key-value
        if path == "key":
            # counter value does not exist
            if key not in count:
                body = str(key_value.pop(key, None))
                return '200 OK Content-Length '.encode() + str(len(body)).encode() + '  ' + body.encode()
            else: 
                return '405 MethodNotAllowed  '
        # DELETE counter
        if path == "counter":
            # counter value does not exist
            if key not in count:
                return '404 NotFound  '
            # counter value exist
            else:
                body = str(counter.pop(key, None))
                return '200 OK Content-Length ' + str(len(body)).encode() + '  ' + body.encode()

while True:
    message = connectionSocket.recv(1)

    if len(message) == 0:
        break

    while (message.find(b'  ') == -1):
        message += connectionSocket.recv(1)
    
    output = execute(parse(message.decode()))
    connectionSocket.send(output)

connectionSocket.close()

