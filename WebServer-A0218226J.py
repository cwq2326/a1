from socket import *
import sys

# server setup
serverPort = int(sys.argv[1])
serverSocket = socket(AF_INET,SOCK_STREAM) 
serverSocket.bind(('',serverPort))
serverSocket.listen(1) 

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
    length = -1

    if (not (path == "key" or path == "counter")): # path here is case-sensitive
        path = ""
    
    if (method.upper() == "GET" or method.upper() == "DELETE"):
        return [method, path, key]

    if ("content-length" in header.lower()):
        startIdx = header.lower().find("content-length") + 15
        print (startIdx)
        other = header[startIdx:]
        endIdx = other.find(" ") + startIdx
        print(endIdx)
        length = int(header[startIdx:endIdx])

    return [method, path, key, length]

# Read header request 1 byte at a time to account for intermittent transmission
def execute(parsedMessage):
    method = parsedMessage[0]
    path = parsedMessage[1]
    key = parsedMessage[2]
    
    if method == "GET":
        if key not in key_value:
            return '404 NotFound  '.encode()
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
            return '200 OK Content-Length '.encode() + str(len(body)).encode() + b'  ' + body

        # get counter
        if path == "counter":
            body = str(counter.get(key, 'Infinity'))
            return '200 OK Content-Length '.encode() + str(len(body)).encode() + b'  ' + body.encode()

    if method == "POST":
        length = parsedMessage[3]

        # POST key-value
        if path == "key":
            value = b'' # value is a binary string
            for i in range (min(length, FIVE_MB)):
                value += connectionSocket.recv(1) # handle intermittent connection
            if key in counter:
                return '405 MethodNotAllowed  '.encode()
            key_value.update({key: value})
            return '200 OK  '.encode()

        # POST counter
        if path == "counter":
            # key does not exist in key-value
            if key not in key_value:
                return '405 MethodNotAllowed  '.encode()
            # key does not exist in key-value
            else:
                count = b''
                for i in range (min(length, FIVE_MB)):
                    count += connectionSocket.recv(1) # handle intermittent connection
                # count is an int
                count = int(count)
                # insertion 
                if counter.get(key) == None:
                    counter.update({key: count})
                # update
                else:
                    counter[key] += count
                return '200 OK  '.encode()

    if method == "DELETE":
        # non-existent key
        if key not in key_value:
            return '404 NotFound  '.encode()
        # DELETE key-value
        if path == "key":
            # counter value does not exist
            if key not in counter:
                body = key_value.pop(key, None)
                return '200 OK Content-Length '.encode() + str(len(body)).encode() + b'  ' + body
            else: 
                return '405 MethodNotAllowed  '.encode()
        # DELETE counter
        if path == "counter":
            # counter value does not exist
            if key not in counter:
                return '404 NotFound  '.encode()
            # counter value exist
            else:
                body = str(counter.pop(key, None))
                return '200 OK Content-Length '.encode() + str(len(body)).encode() + b'  ' + body.encode()

while True:
    connectionSocket, clientAddr = serverSocket.accept()
    while True:
        message = connectionSocket.recv(1)

        if len(message) == 0:
            break

        while (message.find(b'  ') == -1):
            message += connectionSocket.recv(1)

        output = execute(parse(message.decode()))
        connectionSocket.send(output)

connectionSocket.close()

