import socket
import time

class Aclient():
    """A class representing a client for a trivia game."""

    def discover_server(self):
        """
        Discover the game server by listening for broadcast messages.
        Returns:
            tuple: A tuple containing server name, server IP address, and TCP port.
            None if no server is discovered.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)    # Set socket option to allow reuse of the port on the same computer
            udp_socket.bind(('', self.UDP_PORT))  # Bind the socket to the UDP port
            data, server = udp_socket.recvfrom(1024)  # Receive broadcast message from the server
            if len(data) >= 13:
                # Check if data length is at least 13 bytes
                magic_cookie = data[:4]
                message_type = data[4]
                if magic_cookie == b'\xab\xcd\xdc\xba' and message_type == 0x02:
                    server_name = data[5:37].decode('utf-8').rstrip('\x00')  # Decode Unicode string and strip null characters
                    server_port = int.from_bytes(data[37:39], 'big')
                    server_address = server[0]
                    return server_name, server_address, server_port

    def start_game(self,ip, port):
        """
        Connect to the game server and start playing.
        Args:
            ip (str): The IP address of the server.
            port (int): The TCP port of the server.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
            try:
                tcp_socket.connect((ip, port))    # Connect to the server
                tcp_socket.send((self.player_name+"\n").encode())     # Send player name to the server          
                print(tcp_socket.recv(1024).decode(), end='')   # Receive initial message from the server
                # Get questions every round and answer
                loos_msg = self.player_name + " is incorrect!"
                while True:
                    msg = tcp_socket.recv(1024).decode()   # Receive question message from the server
                    print(msg)
                    if (msg.startswith("\nGame over!")):
                        # If game is over, print message and break
                        print("Server disconnected, listening for offer requests...")
                        break
                    # Get answer from the client and send
                    answer = self.answer_from_client()               # wait for answer
                    tcp_socket.send(answer.encode())
                    msg = tcp_socket.recv(1024).decode()             # Receive response from the server
                    print(msg)  
                    # If player lost this round, print message and break
                    if (loos_msg in msg  and "Wins" not in msg and "is correct" in msg):
                        print("You lost this round.\nTry Next Time =)\n")
                        while True:
                            msg = tcp_socket.recv(1024).decode()      # question message
                            print(msg)
                            if (msg.startswith("\nGame over!")):
                                # If game is over, print message and break
                                print("Server disconnected, listening for offer requests...")
                                break
                        break

            except Exception:
                # Handle server disconnection
                print("\nServer disconnected, listening for offer requests...\n======================\n")

    def answer_from_client(self):
        """Get the answer from the client with timeout."""
        pass
    
    def play(self):
        """Start playing the trivia game."""
        while True:
            try:
                # Discover the game server
                server_name, server_address, TCP_Port = self.discover_server()
                print(f"Received offer from server \"{server_name}\" at address {server_address}, attempting to connect...")
                # Connect to the servre and start playing
                self.start_game(server_address, TCP_Port)
                time.sleep(1)
            except Exception as e:
                # Handle exceptions
                print(e)
                continue
