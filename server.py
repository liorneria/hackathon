import socket
import _thread
import threading
import time
import struct
import random

buffer_size = 1024
numClients = 0
teamsFlag = False
players = {}
ClientsNames = []
addresses = []
sockets = []
answer1 = []
answer2 = []
# randomize the math question
x1 = random.randrange(1,4)
x2 = random.randrange(1,5)
answer = x1 + x2
# time for the end
FinishTime = time.time() + 100 

def SearchClients():
    global numClients
    try:
        # creating tcp socket 
        TCP_socket = socket.socket(family = socket.AF_INET, type = socket.SOCK_STREAM)
        TCP_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # conneect to our port address - 2094
        TCP_socket.bind(("", 2094))
        TCP_socket.listen(1)
        # searching until we got 2 cliens
        while  numClients < 2:  
            _socket, address = TCP_socket.accept()
            team = threading.Thread(target = AddNewClient, args = (_socket, address))
            team.start()
        return
    except:
        print("Wrong type of message received")

# The server keep the clients name
# and assigns each of the clients randomly to team 1 or team 2
def AddNewClient(_socket, address):
    global ClientsNames
    global numClients
    global players
    global sockets
    global teamsFlag
    global addresses
    global buffer_size
    
    lock1 = threading.RLock()
    lock2 = threading.RLock()
    sockets.append(_socket)
    addresses.append(address)
    try:
        name = _socket.recv(buffer_size).decode()
        if name:
            # add the name to the clients array
            with lock1:
                ClientsNames.append(name)
            while len(ClientsNames) < 2:  # while there are less than 2 clients
                time.sleep(1)
            
            # assign to player
            with lock2:
                # print(name)
                if teamsFlag:
                    players[name] = (_socket, 1)
                    teamsFlag = True
                else:
                    players[name] = (_socket, 2)

        numClients += 1
        return
    except:
        print("error occurred")


def Player1(client, address):
    global answer1
    lock = threading.RLock()
    time_after_10_sec = 10 + time.time()
    while time.time() < time_after_10_sec:  # 10 seconds after the server was started
        try:
            key = client.recv(buffer_size)
            playerAnswer = key.decode()
            if playerAnswer:
                with lock:
                    answer1 = [time.time(), playerAnswer, 1]
                    return
        except:
            continue
    return 

def Player2(client, address):
    global answer2
    lock = threading.RLock()
    time_after_10_sec = 10 + time.time()
    while time.time() < time_after_10_sec:  # 10 seconds after the server was started
        try:
            key = client.recv(buffer_size)
            playerAnswer = key.decode()
            if playerAnswer:
               with lock:
                    answer2 = [time.time(), playerAnswer, 2]
                    return
        except:
            continue
    return 


def StartGame():
    # create welcoming message
    welcome_message = "Welcome to Quick Maths.\n" \
                       "Player 1:\n==\n" + list(players.keys())[0]\
                       +"Player 2:\n==\n" + list(players.keys())[1] +\
                       "\nPlease answer the following question as fast as you can:\n How much is " +str(x1) + " + " +str(x2)
    # print("created welcoming message")
    # for each socket connection we call to ther relevant function
    options = [Player1, Player2]
    for s in range(len(sockets)):
        sockets[s].send(welcome_message.encode())
        _thread.start_new_thread(options[s], (sockets[s], addresses[s]))

def ValidateResults():
    # print(answer1)
    # print(answer2)

    # no one answer - its a draw
    if answer1 == [] and answer2 == []:
        end_message = "\nGame over! \nThe correct answer was " + str(answer) + "!\n Its a draw!\n\n" \
    
    # if player 2 didnt answer or player 1 answer first
    elif answer2 == [] or (answer1!=[] and answer1[0] < answer2[0]):
        # player 1 is correct
        if int(answer1[1]) == answer:
            end_message = "\nGame over!\nThe correct answer was " + str(answer) + "!\n\n" \
                        + "Congratulations to the winners:\n==\n" + "" + list(players.keys())[0]
        else:
            end_message =  "\nGame over!\nThe correct answer was " + str(answer) + "!\n\n" \
                        + "Congratulations to the winners:\n==\n" + "" + list(players.keys())[1]
    
    # if player 1 didnt answer or player 2 answer first
    elif answer1 == [] or (answer2!=[] and answer1[0] > answer2[0]) :
        # player 2 is correct
        if int(answer2[1]) == answer:
            end_message = "\nGame over!\nThe correct answer was " + str(answer) + "!\n\n" \
                        + "Congratulations to the winners:\n==\n" + "" + list(players.keys())[1]
        else:
            end_message = "\nGame over!\nThe correct answer was " + str(answer) + "!\n\n" \
                        + "Congratulations to the winners:\n==\n" + "" + list(players.keys())[0]
    # print(end_message)
    end_message = u"\u001B[35m" + end_message
    # sending to the clients the game results
    for s in range(len(sockets)):
        sockets[s].send(end_message.encode())

# TODO @@ ### @@@# ###
def close_connections():
    global sockets
    for i in range(len(sockets)):
        sockets[i].close()
    sockets = []
    addresses = []


# starting the server
# UDP sockets creation
UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
UDP_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
UDP_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
UDP_socket.bind(('', 2054))
print(u"\u001B[32mServer started' listening on IP address 172.1.0.22\u001B[32m")
thread = threading.Thread(target = SearchClients, args=())
thread.start()

while time.time() < FinishTime and numClients < 2:

    try:
        # send
        MSG = struct.pack('<3Q', 0xabcddcba, 0x2, 0xA)
        print("sending")
        UDP_socket.sendto(MSG, ('<broadcast>', 13117))
        time.sleep(1)

    except:
        time.sleep(1)

# if we have 2 clients we can start the game
if numClients == 2:
    StartGame()
    time.sleep(10)
    ValidateResults()

while time.time() < FinishTime:
    time.sleep(1)

time.sleep(100)

# closing the server
print("Game over, sending out offer requests...")
while True:
    # send
    MSG = struct.pack('<3Q', 0xfeedbeef, 0x2, 0xA)
    UDP_socket.sendto(MSG, ('<broadcast>', 13117))
    time.sleep(1)
