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
error404 = '404 NotFound  '.encode()
ok200a = '200 OK  '.encode()
ok200b = '200 OK Content-Length '.encode()
error405 = '405 MethodNotAllowed  '.encode()

while True:
    connectionSocket, addr = serverSocket.accept()
    message = connectionSocket.recv(FIVE_MB) 
    
    while len(message) != 0 : 
        headerEnd = message.find(b'  ')
        # full header found
        while headerEnd != -1:
            # header found but could overlap with body 
            # get a full request containing body first
            header = message[:headerEnd].decode()
            split = header.split(" ")
            method = split[0].upper()
            path = (split[1].split("/"))[1]
            key = (split[1].split("/"))[2]

            if method == "GET":
                if key not in key_value:
                    connectionSocket.send(error404)
                    # get key-value
                else:
                    if path == "key":
                        body = key_value.get(key)
                        # decrement counter if exists
                        if key in counter:
                            counter[key] -= 1
                            # remove key-value if zero
                            if counter[key] <= 0:
                                counter.pop(key, None)
                                key_value.pop(key, None)
                        connectionSocket.send(ok200b + str(len(body)).encode() + b'  ' + body)

                    # get counter
                    if path == "counter":
                        body = str(counter.get(key, 'Infinity'))
                        connectionSocket.send(ok200b + str(len(body)).encode() + b'  ' + body.encode())
            
                message = message[len(header) + 2:len(message)]

            if method == "POST":
                length = 0

                for i in range(len(split)):
                    if (split[i].lower() == 'content-length'):
                        if split[i + 1].isdigit():
                            length = int(split[i+1])
                            break

                # get body
                body = message[headerEnd + 2 : headerEnd + 2 + length]
                if (len(body) < length):
                    break
                # POST key-value
                if path == "key":
                    value = body
                    if key in counter:
                        connectionSocket.send(error405)
                    else: 
                        key_value.update({key: value})
                        connectionSocket.send(ok200a)

                # POST counter
                elif path == "counter":
                    # key does not exist in key-value
                    if key not in key_value:
                        connectionSocket.send(error405)
                    # key exist in key-value
                    else:
                        count = body
                        # count is an int
                        count = int(count)
                        # insertion
                        if counter.get(key) == None:
                            counter.update({key: count})
                        # update
                        else:
                            counter[key] += count
                        connectionSocket.send(ok200a)

                else: 
                    connectionSocket.send(error404)

                message = message[len(header) + 2 + length:]

            if method == "DELETE":
                # non-existent key
                if key not in key_value:
                    connectionSocket.send(error404)
                else:
                    # DELETE key-value
                    if path == "key":
                        # counter value does not exist
                        if key not in counter:
                            body = key_value.pop(key, None)
                            connectionSocket.send(ok200b + str(len(body)).encode() + b'  ' + body)
                        else:
                            connectionSocket.send(error405)
                    # DELETE counter
                    if path == "counter":
                        # counter value does not exist
                        if key not in counter:
                            connectionSocket.send(error404)
                        # counter value exist
                        else:
                            body = str(counter.pop(key, None))
                            connectionSocket.send(ok200b + str(len(body)).encode() + b'  ' + body.encode())
                            
                message = message[len(header) + 2:len(message)]
            
            headerEnd = message.find(b'  ')

        nextMessage = connectionSocket.recv(FIVE_MB)
        if len(nextMessage) == 0:
            break
        message += nextMessage

    connectionSocket.close()
