# TCP Chat Server implementation

import select, socket, sys
import query

# Broadcasts message to all clients connected to server
def broadcast(sender_socket, message):
    for socket in CONNECTION_LIST:
        # Excluding the server socket and the client socket that send the message
        if socket != server_socket and socket != sender_socket:
            try:
                socket.send(message.encode())
            except:
                # Client closed the socket. Hence the socket is removed.
                socket.close()
                CONNECTION_LIST.remove(socket)

# main
if __name__ == "__main__":

    # if len(sys.argv) != 2:
    # 	exit("usage: %s <port>" % sys.argv[0])

    # Connection list
    # Contains all the objects from which we intend to read data.
    # The objects in this list falls to 3 categories.
    # (More details further below at the corresponding lines)
    # 1- The server socket
    # 2- stdin (The console input)
    # 3- The client sockets
    CONNECTION_LIST = []
    # # receive buffer length
    RECV_BUFFER = 4096
    # # listen port
    # try:
    # 	PORT = int(sys.argv[1])
    # 	if PORT < 1000 or PORT > 60000:
    # 		raise ValueError
    # except ValueError:
    # 	exit(">> Invalid port.")

    PORT = 5500

    # Creating the socket.
    # AF_INET -> IPv4 address family
    # SOCK_STREAM -> TCP protocol
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Configuring to reuse the same port.
    # If SO_REUSEADDR is not set to 1, once after running and closing the
    # server program, running it a second time on the same port throws
    # "Address already in use" error. So, it is set to 1 in order to reuse the
    # port even after the socket is closed.
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Binds to all the netwrok addresses of the host/server computer.
    server_socket.bind(("0.0.0.0", PORT))

    # Socket listens for incoming connections.
    server_socket.listen(10)

    # Adding server socket to the list.
    # Functionality:
    # The server socket listens for incoming
    # connections and add the newly connected
    # client sockets to the CONNECTION_LIST.
    # (Code pretaining to this comes below, inside the for loop)
    CONNECTION_LIST.append(server_socket)

    # Adding console input to the list.
    # Functionality:
    # Typing "/exit" at the console let's you safely
    # close the sockets and exit the server program.
    # (Code pretaining to this comes below, inside the for loop)
    CONNECTION_LIST.append(sys.stdin)

    print("\r>> Server started on port:", PORT)

    query.server()

    while True:
        # fetching connection list
        # CONNECTION_LIST contains the readable objects and the
        # select function waits and returns the objects that has data
        # to be read. (Only read_sockets is of importance to us. The rest
        # two are just place holders for empty lists.)
        read_sockets,write_sockets,error_sockets = select.select(CONNECTION_LIST,[],[])

        #Iterating through each readable object in read_sockets
        for sock in read_sockets:

            # If the input is from the console, the following
            # lines are executed. Only "/exit" command exits as of now.
            # Commands are defined within the query.py file
            if sock == sys.stdin:
                cmd = sys.stdin.readline()
                query.command(cmd)

            # If the server socket finds a new connection, the corresponding
            # client socket is added to the list.
            elif sock == server_socket:
                sockfd, addr = server_socket.accept()
                CONNECTION_LIST.append(sockfd)
                print("\r>> (%s, %s) connected." % addr)
                broadcast(sockfd, "\r>> [%s:%s] entered chat room.\n" % addr)

            # If a connected client sends a message, the message is
            # broadcasted to all the clients and displayed within the server program.
            else:
                try:
                    data = sock.recv(RECV_BUFFER)
                    data = data.decode()
                    if data == "":
                        raise Exception
                    if data:
                        broadcast(sock, "\r" + str(sock.getpeername()) + ": " + data)
                        print("\r" + str(sock.getpeername()) + ": " + data, end = "")
                # Reading data from a disconnected client throws an error and the
                # following block handles the error by closing the socket and
                # removing it from the list.
                except:
                    broadcast(sock, "\r>> [%s, %s] is now offline.\n" % addr)
                    print("\r>> (%s, %s) is now offline." % addr)
                    if sock in CONNECTION_LIST:
                        sock.close()
                        CONNECTION_LIST.remove(sock)
                    continue

        query.server()

    server_socket.close()
