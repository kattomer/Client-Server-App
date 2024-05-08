import random
import string
from Aclient import Aclient
import threading

class Bot(Aclient):
    def __init__(self, UDP_PORT = 13117):
        """
        Initialize the Bot client.
        Args:
            UDP_PORT (int): The UDP port for the client. Default is 13117.
        """
        self.player_name = self.generate_bot_name()
        self.UDP_PORT = UDP_PORT

    def generate_bot_name(self):
        """
        Generate a random name for the bot client.
        """
        suffix_length = 6
        suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=suffix_length))
        return "BOT_" + suffix+"\n"   
    
    def answer_from_client(self):
        """
        Generate a random True or False answer.
        """
        choise = random.choice(["T", "F"])
        if choise == "T":
            print("True\n")
            return "T"
        else:
            print("False\n")
            return "F"
        
    def create_and_run_bots(self):
        """
        This method prompts the user to specify the number of bot clients to create,
        then creates and runs the specified number of bot clients concurrently.
        """
        number_of_bots = None
        while True:
            number_of_bots = input("How many bots would you like? ")
            try:
                number_of_bots = int(number_of_bots)
                if number_of_bots > 0:
                    break  
                else:
                    print("Please enter a number larger than 0.")
            except ValueError:
                print("Please enter a valid number of bots.")
        threads = []
        for _ in range(number_of_bots):
            bot = Bot()
            thread = threading.Thread(target=bot.play)      # Create a new thread for each bot client
            thread.start()                                  # Start the thread, which will execute the bot's play method
            threads.append(thread)                          # Store the thread object in a list
        for thread in threads:
            thread.join()                                   # Wait for all threads to complete before proceeding  


            
if __name__ == "__main__":
    bot = Bot()
    bot.create_and_run_bots()
   
