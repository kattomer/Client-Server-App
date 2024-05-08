import time
import msvcrt
from Aclient import Aclient
import json
import random

class Client(Aclient):
    def __init__(self, config_path='config.json', UDP_PORT = 13117):
        self.player_name = self.load_name_from_config(config_path)
        self.UDP_PORT = UDP_PORT
        self.timeout = 10

    def load_name_from_config(self, filepath):
        try:
            with open(filepath, 'r') as file:
                data = json.load(file)
            # Choose a random name from the names list
            return random.choice(data.get('names', ['Default Player']))
        except FileNotFoundError:
            print("Config file not found, using default player name.")
            return "Default Player"
        except json.JSONDecodeError:
            print("Error decoding JSON, using default player name.")
            return "Default Player"

    def answer_from_client(self):
        """
        Get the answer from the client with a timeout.
        """
        start_time = time.time() # Record the start time
        while True:
            try:
                if msvcrt.kbhit():  # Check if a key is pressed
                    key = msvcrt.getch().decode('utf-8')  # Lissten to key pressed without waiting for the client press 
                    # Check if the key is a valid answer
                    if key.lower() in ('t', '1', 'y'): 
                        print("True\n")
                        return "T"
                    elif key.lower() in ('f', '0', 'n'):
                        print("False\n")
                        return "F"
                    print("Invalid answer: optional valid answers: (t/T/1 = True) or (f/F/0 = False)")
                if time.time() - start_time >= self.timeout:        # Check if the timeout has elapsed
                    print("Time is up\n")
                    return "None"
            except Exception as e:
                # Handle exceptions
                print("Typed Hebrew or else invalid Char")
                
if __name__ == "__main__":
    print("Client started, listening for offer requests...")
    client = Client()   # Create an instance of the Client class
    client.play()       # Start playing the trivia game
