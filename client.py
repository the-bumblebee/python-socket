# TCP Chat Client implementation

import select, socket, string, sys
import query

# main
if __name__ == "__main__":

    # if len(sys.argv) < 3:
    #     print("usage: %s <hostname> <port>" % sys.argv[0])
    #     sys.exit()

    # host = sys.argv[1]
    # port = int(sys.argv[2])

    host = "127.0.0.1"
    port = 5500

    # Socket is created
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)

    # Connecting to host
    try:
        s.connect((host, port))
    except:
        print(">> Connection failed.")
        sys.exit()

    print(">> Connected to remote host")

    query.client()

    while True:
        # Listening from stdin (console input) and server socket
        # (Client version of CONNECTION_LIST)
        socket_list = [sys.stdin, s]

        # Fetching readable socket list
        read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])

        for sock in read_sockets:

            # If message incoming from server
            if sock == s:
                data = sock.recv(4096)
                data = data.decode()
                if data:
                    sys.stdout.write(data)
                else:
                    print(">> Connection timed out.")
                    sys.exit()

            # If message is from the console (message to be send)
            # Also "/exit" is a command and exits the program.
            else:
                msg = sys.stdin.readline()
                if not msg.isspace():
                    if msg[0] == '/':
                        query.command(msg)
                    else:
                        s.send(msg.encode())

            query.client()
