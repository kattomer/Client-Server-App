import random
import socket
import threading
import time
import concurrent.futures
from Bot import Bot 
import json

# Define server settings
UDP_PORT = 13117
TCP_PORT = None
BROADCAST_INTERVAL = 1  # send every 1 second
GAME_DURATION = 10      # seconds
clients = []
players = []
player_stats = {}
game_started = False
charachter = 0
players_daily_record = []

# Unique and predefined value or sequence of bytes 
# Help identify and distinguish different types of messages
MAGIC_COOKIE = b'\xab\xcd\xdc\xba'  

SERVER_NAME = "_Champions_League_Trivia_Server_"
MESSAGE_TYPE_OFFER = 0x02

# ANSI color escape codes
COLOR_GREEN = "\033[92m"    # Green
COLOR_RED = "\033[91m"      # Red
COLOR_BLUE = "\033[94m"     # Blue
COLOR_YELLOW = "\033[93m"   # Yellow
COLOR_BOLD = "\033[1m"      # Bold
COLOR_UNDERLINE = "\033[4m" # Underline
COLOR_RESET = "\033[0m"     # Reset color to default

# Upload the data
data = load_config()
champions_league_questions, stats = data["questions"], data["stats"]


# Send brodcast massege with the server IP and TCP port in UDP every second  
def broadcast_udp(tcp_port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as udp_socket: # Create a UDP socket for broadcasting
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        # Prepare server details for the UDP message
        server_name_bytes = SERVER_NAME.encode('utf-8')
        message = MAGIC_COOKIE + bytes([MESSAGE_TYPE_OFFER]) + server_name_bytes + tcp_port.to_bytes(2, 'big') 

        # Send broadcast messages until the game starts
        while not game_started:
            udp_socket.sendto(message, ('<broadcast>', UDP_PORT))
            # Send every second
            time.sleep(BROADCAST_INTERVAL)


   
# Seve client details and add him to the game    
def handle_client(conn, addr):
    global clients, charachter, player_stats, players_daily_record
    try:
        name = conn.recv(1024).decode().strip()  # Receive player's name
        print(f"Accepted connection from {addr}, {COLOR_UNDERLINE}Player Name: {name}{COLOR_RESET}")
        clients.append((conn, name))  # Store connection and name
        if name not in players_daily_record: # Create new stats report for the new players
            player_stats[name] = {"wins": 0, "games_played": 0, "consecutive_wins": 0, "max_consecutive_wins": 0}
            players_daily_record.append(name)

    except Exception as e:
        print(f"Error handling client {addr}: {e}")



# Function to send a message to all clients concurrently
def send_all(message, conections):
    print(message)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        [executor.submit(send_message, conn, message) for conn, _ in conections]


# Function to send a message to a single client
def send_message(conn, message):
    try:
        conn.send(message.encode())
    except Exception as e:
        remove_client(conn)



# Start and manege new game
def start_game():
    global game_started, clients, players, champions_league_questions
    game_started = True
    winner_name = ""
    players = clients  #Pleyers left in courent round
    msg_participants = ""  # players massage
    # send welcome message to all prticipents
    for i, client in enumerate(clients):
        msg_participants += f'Player {i+1}: {client[1]}\n' 
    welcome_m = f"Welcome to the {SERVER_NAME}, where we are answering trivia questions about the Champions Leage.\n=== \n{msg_participants}\n===\n"    
    send_all(welcome_m, clients)  
    with concurrent.futures.ThreadPoolExecutor() as executor:
        num_players_left = len(clients)
        idx = 0
        round = 1
        # Play untill one pleyer left
        while(num_players_left > 1):
            num_players_left = 0 # Number of winers in this courrent round
            responseWin = ""  # nemes of the winners
            responseLose = "" # nemes of the loosers
            temp = []
            # Choose randon question every round
            question, answer = champions_league_questions[idx]['text'], champions_league_questions[idx]['correct_answer']
            if (idx >= 19):
                idx = 0
                random.shuffle(champions_league_questions)
            else:
                idx+=1
            # Send the question info (success rate, question, the players...)
            if champions_league_questions[idx]['times_asked'] > 0:  # Avoid division by zero
                success_rate = 100 * champions_league_questions[idx]['correct_responses'] / champions_league_questions[idx]['times_asked']
                stat = f"{COLOR_BLUE}Question: {champions_league_questions[idx]['text']}{COLOR_RESET}\n{success_rate:.2f}% have manage to answer this question correctly"
            else:
                stat = question
            question_message = f"{COLOR_BLUE}Round {round}, played by:{COLOR_RESET}\n" + "\n".join(p[1] for p in players) + "\n\n" + stat
            send_all(question_message, players)

            futures = [executor.submit(get_answer, conn, answer, idx) for conn, _ in players]
            # Retrieve results from completed tasks
            done, _ = concurrent.futures.wait(futures)
            for future in done:
                result = future.result()
                index = futures.index(future)
                # handel winners
                if result:
                    temp.append(players[index])
                    responseWin += f'{COLOR_GREEN}{players[index][1]} is correct!{COLOR_RESET}\n'
                    num_players_left += 1 
                #handel loosers    
                else:
                    responseLose += f'{COLOR_RED}{players[index][1]} is incorrect!{COLOR_RESET}\n' 
            # only one winner
            if num_players_left == 1:
                winner_name = temp[0][1]
                responseWin = f'{COLOR_GREEN}{temp[0][1]} is correct! {temp[0][1]} Wins!{COLOR_RESET}\n'
            # massege to all clients left
            response = responseLose + responseWin +"\n======================\n"   
            send_all(response, clients)
            # Eliminate loosers
            if(len(temp) != 0):
                players = temp
            round += 1
            num_players_left = len(players) 
               
        end_game(winner_name)
        save_questions(champions_league_questions)  # Save updated stats at the end of each game
 



#One round of The game, send question to each client and check his answer
def get_answer(conn, answer, question_idx):        
    global clients, players
    try:
        received_answer = conn.recv(1024).decode().strip().upper()
        correct = received_answer == answer
        # Update question statistics
        champions_league_questions[question_idx]['times_asked'] += 1
        if correct:
            champions_league_questions[question_idx]['correct_responses'] += 1
        return correct
    except Exception as e:
        print(f"Client disconnected")
        return False


# Send End game massege and close connections
def end_game(winner_name):
    global clients, game_started, player_stats
    game_started = False
    if winner_name == "":
        final_message = f"{COLOR_BOLD}\nGame over!\nAll other players disconnected{COLOR_RESET}"
    else:
        record_broken = update_stats(winner_name)
        record_message = f"\n{winner_name} has set a new record of consecutive wins: {player_stats[winner_name]['max_consecutive_wins']}!" if record_broken else ""
        stats_message = format_stats()
        final_message = f"\nGame over!\nCongratulations to the winner: {COLOR_YELLOW}{winner_name}{COLOR_RESET}{record_message}\n{stats_message}"

    send_all(final_message, clients)
    for tup in clients:
        tup[0].close()
        
    send_all(final_message, clients)
    clients = []  # Reset clients for the next game
    print(f"Game over, sending out offer requests...\n======================\n")

# Listen to clients connections 
def collect_players(tcp_port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(('0.0.0.0', tcp_port))  # Bind the socket to listen on all available network
        server_socket.listen()
        client_threads = []
        players = 0
        while True:
            try:
                conn, addr = server_socket.accept()  # Accept a new connection from a player
                players += 1
                if(players >1):   #  Set a 10 seconds timeout if more than 2 player is connected
                    server_socket.settimeout(10.0)
                client_thread = threading.Thread(target=handle_client, args=(conn, addr))
                client_thread.start()
                client_threads.append(client_thread)
            # 10 seconds after last player connect    
            except socket.timeout:
                break
        for thread in client_threads:
            thread.join()    
        start_game()

#Serch avilable TCP port
def get_free_tcp_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:  # Creates a TCP socket 
        s.bind(('', 0))  # Operating system selects an available port automatically by passing an empty string '' as the IP address and 0 as the port number
        return s.getsockname()[1]
    
def get_local_ip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  #  Creates a UDP socket
    try:
        # Connect to a known address to get the local IP
        # Establish a connection to the address '8.8.8.8' on port 80
        sock.connect(('8.8.8.8', 80)) #  Port 80 is the default port for HTTP traffic
        # Get the local IP address
        local_ip = sock.getsockname()[0] # The first element contains the local IP and port

    except socket.error as e:
        print(f"Socket error: {e}")
        local_ip = None  # Assign None to local_ip in case of an exception

    finally:
        sock.close()
    return local_ip


def remove_client(conn):
    global clients, players
    # Remove the client connection from the list
    clients = [client for client in clients if client[0] != conn]
    players = [player for player in players if player[0] != conn]

    try:
        conn.close()  # Attempt to close the connection gracefully
    except Exception as e:
        print(f"Failed to close connection: {e}")




def load_config(filepath='config.json'):
    try:
        with open(filepath, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # Return a default structure if there's an error loading the file
        return {'questions': [], 'stats': {}}


def save_questions(questions):
    data = load_config()
    data['questions'] = questions

    with open('config.json', 'w') as file:
        json.dump(data, file, indent=4)  # Use indent=4 for better readability in the file
 


# Sending formatted player statistics
def format_stats():
    title = "\033[1;34mPlayer Statistics - Top 5 Performers\033[0m\n"
    header = "\033[1;33m| {0:<10} | {1:<5} | {2:<14} | {3:<16} |\033[0m".format(
        "Player", "Wins", "Games Played", "Max Win Streak")
    lines = [title, header, "\033[1;32m" + "-" * len(header) + "\033[0m"]

    # Sort players based on 'max_consecutive_wins' in descending order and select the top five
    sorted_players = sorted(player_stats.items(), key=lambda item: item[1]['max_consecutive_wins'], reverse=True)[:5]

    for name, stats in sorted_players:
        line = "| {0:<10} | {1:<5} | {2:<14} | {3:<16} |".format(
            name, stats['wins'], stats['games_played'], stats['max_consecutive_wins'])
        lines.append(line)

    lines.append("\033[1;32m" + "-" * len(header) + "\033[0m")
    return "\n".join(lines)


# Update the config.json file 
def update_stats_file(new_score, filepath='config.json'):
    global champions_league_questions
    data = load_config(filepath)
    json_obj = json.dumps({"questions": champions_league_questions, "stats": new_score, "names": data['names']})
    try:
        with open("config.json", 'w') as file:
            file.write(json_obj)
    except IOError as e:
        print(f"Error writing to file: {e}")


 # Update stats after a game ends and notify about any new records    
def update_stats(winner):
    global clients, player_stats, stats
    record_broken = False
    for player_name in player_stats:  
        player_stats[player_name]["games_played"] += 1
        if player_name == winner:
            player_stats[player_name]["wins"] += 1
            player_stats[player_name]["consecutive_wins"] += 1

            # Check and update maximum consecutive wins
            if player_stats[player_name]["consecutive_wins"] > player_stats[player_name]["max_consecutive_wins"]:
                player_stats[player_name]["max_consecutive_wins"] = player_stats[player_name]["consecutive_wins"]
                # The world record was broken
                if player_stats[player_name]["consecutive_wins"] > stats:
                    num = player_stats[player_name]["max_consecutive_wins"]
                    update_stats_file(num)  # Save the new global record 
                    record_broken = True
        else:
            player_stats[player_name]["consecutive_wins"] = 0  # Reset on loss

    return record_broken


def run():
    ip = get_local_ip() # For sending UDP broadcast to the clients
    print(f"Server started, listening on IP address {ip}")
    while(True):
        try:
            tcp_port = get_free_tcp_port()
            # send brodcast with the server details every second
            threading.Thread(target=broadcast_udp, args=(tcp_port,), daemon=True).start()
            # Collect players and start the game
            collect_players(tcp_port)
        except Exception as e:
            print(e)
            # time.sleep(5)  # Wait before retrying


if __name__ == "__main__":
    run()