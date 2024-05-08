
# Champions League Trivia Server
Welcome to the Champions League Trivia Server, where the excitement never ends! This application allows you to immerse yourself in thrilling rounds of trivia about the UEFA Champions League. Players can connect and engage in a battle of wits, while automated bots add an extra layer of competition 

## Key Features
# <ins>Broadcasting Capability:</ins> 
The server employs UDP broadcasting to efficiently disseminate its IP address and TCP port, facilitating seamless client discovery.

# <ins>Comprehensive Game Management:</ins> 
It orchestrates player connections, coordinates trivia rounds, and announces victors with precision, ensuring a smooth and enjoyable gaming experience.

# <ins>Continuous Operation:</ins> 
Both server and client applications run indefinitely until manually stopped, ensuring uninterrupted gameplay.

# <ins>Dynamic Question Handling: </ins> 
The server dynamically selects questions from a meticulously curated set, providing an engaging and diverse range of challenges for participants.

# <ins>Interactive Client Interaction:</ins> 
Through TCP communication, clients receive questions and submit answers, fostering a dynamic and responsive interaction between players and the game server.

# <ins>Robust Bot Support:</ins>
The inclusion of bot functionality allows for the seamless integration of automated players, enhancing the overall competitiveness and engagement of the trivia experience.

## Utilization Guidelines
# <ins>Server Deployment:</ins> 
Ready to get the party started? Just fire up server.py to kick off your trivia game server. It's all set to handle connections and dish out some seriously fun rounds of questions.

# <ins>Client Engagement:</ins> 
As for the players, they can jump right into the action by hooking up with the server using the Client class from client.py. It's like diving into a pool of trivia goodness, where they can flex their knowledge muscles and battle it out with other enthusiasts.

# <ins>Bot Integration:</ins> 
Add some zest to your game with bots! Use the Bot class in bot.py to spice things up. These automated players dive right into the trivia game, adding an extra kick to the competition.

They're here to make the gaming experience livelier and more thrilling.

## Component Breakdown
# <ins>server.py:</ins> 
Houses the server logic, meticulously engineered to handle connections, orchestrate game rounds, and broadcast server details efficiently.

# <ins>client.py:</ins> 
Offers a robust client class, empowering users to effortlessly connect to the server, participate in trivia rounds, and submit responses to questions.

# <ins>bot.py:</ins> 
Defines a sophisticated bot class, facilitating the creation and deployment of automated players, thereby enriching the gaming ecosystem with dynamic and engaging adversaries.

# <ins>Aclient.py:</ins> 
Serves as a foundational base class shared by both the client and bot classes, encapsulating common UDP communication functionalities for seamless integration and extensibility.

## Guidelines
# <ins>Error Handling:</ins> 
Implement robust error handling mechanisms to address network-related issues, ensuring smooth operation even in challenging scenarios.

# <ins>Code Quality:</ins> 
Strive for excellence in code quality, with proper layout, meaningful variable names, and comprehensive documentation.

# <ins>Source Control:</ins> 
Maintain your codebase in a dedicated GitHub repository, with regular commits from all team members and clear commit messages.

## How to Play
# <ins>Server Deployment:</ins> 
Launch the server.py script to initiate the trivia game server.

# <ins>Client Engagement:</ins> 
Connect to the server using client.py and dive into the trivia action with your creative player name.

# <ins>Bot Integration:</ins> 
Spice up the competition by deploying bots using bot.py, adding an extra layer of challenge and excitement to the game.

Additional Notes
The server diligently persists question statistics to a JSON file (config.json) post each game session, ensuring the preservation and accessibility of invaluable gaming data.
Clients benefit from a predefined timeout mechanism for answering questions, guaranteeing fairness and integrity throughout the gaming process.
Bots contribute to the gaming ecosystem by furnishing random names and responses, imbuing the gameplay with an additional layer of unpredictability and excitement.
Embark on an exhilarating journey of Champions League Trivia, where knowledge reigns supreme, and victory awaits the most astute and discerning participants!
