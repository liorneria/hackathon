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
        TcpSocket = socket.socket(family = socket.AF_INET, type = socket.SOCK_STREAM)
        TcpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # conneect to our port address - 2160
        TcpSocket.bind(("", 2160))
        TcpSocket.listen(1)
        # searching until we got 2 cliens
        while  numClients < 2:  
            _socket, address = TcpSocket.accept()
            team = threading.Thread(target = AddNewClient, args = (_socket, address))
            team.start()
        return
    except:
        print("Wrong message type")

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
        ClientName = _socket.recv(buffer_size).decode()
        if ClientName:
            # add the ClientName to the clients array
            with lock1:
                ClientsNames.append(ClientName)
            # while there are less than 2 clients we need to wait
            while len(ClientsNames) < 2:  
                time.sleep(1)
            
            with lock2:
                # if there is assign client already
                if teamsFlag:
                    players[ClientName] = (_socket, 1)
                    teamsFlag = True
                else:
                    players[ClientName] = (_socket, 2)

        numClients += 1
        return
    except:
        print("there is an error")


def Player1(client, address):
    global answer1
    lock = threading.RLock()
    TimeLeft = time.time() + 10 
    # 10 seconds after the server was started we wait to answer
    while time.time() < TimeLeft: 
        try:
            key = client.recv(buffer_size)
            playerAnswer = key.decode()
            if playerAnswer:
                with lock:
                    # create the answer data structure 
                    # include the time the client answer
                    # and the answer
                    answer1 = [time.time(), playerAnswer, 1]
                    return
        except:
            continue
    return 

def Player2(client, address):
    global answer2
    lock = threading.RLock()
    TimeLeft = 10 + time.time()
    # 10 seconds after the server was started we wait to answer
    while time.time() < TimeLeft: 
        try:
            key = client.recv(buffer_size)
            playerAnswer = key.decode()
            if playerAnswer:
               with lock:
                    # create the answer data structure 
                    # include the time the client answer
                    # and the answer
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
    # for each socket connection we call to ther relevant function
    connections = [Player1, Player2]
    for i, s in enumerate(sockets):
        s.send(welcome_message.encode())
        _thread.start_new_thread(connections[s], (sockets[s], addresses[s]))

def ValidateResults():
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
    for i, s in enumerate(sockets):
        s.send(end_message.encode())

def CloseSockets():
    global sockets
    for i, s in enumerate(sockets):
       s.close()
    addresses = []
    sockets = []
    
def main():
    # starting the server by creating UDP sockets connections
    UdpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    UdpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    UdpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    # connetct to our port 2160 
    UdpSocket.bind(('', 2160))
    print(u"\u001B[32mServer started' listening on IP address 172.1.0.22\u001B[32m")
    # now we wait unlill we have two clients
    thread = threading.Thread(target = SearchClients, args=())
    thread.start()

    while time.time() < FinishTime and numClients < 2:
        try:
            # sending broadcast
            BroadcastMassege = struct.pack('<3Q', 0xabcddcba, 0x2, 0xA)
            UdpSocket.sendto(BroadcastMassege, ('<broadcast>', 13117))
            time.sleep(1)
        except:
            time.sleep(1)

    # if we have 2 clients we can start the game
    if numClients == 2:
        StartGame()
        time.sleep(10)
        ValidateResults()
        CloseSockets()

    while time.time() < FinishTime:
        time.sleep(1)

    time.sleep(100)

    # closing the server
    print("Game over, sending out offer requests...")
    while True:
        # send
        BroadcastMassege = struct.pack('<3Q', 0xfeedbeef, 0x2, 0xA)
        UdpSocket.sendto(BroadcastMassege, ('<broadcast>', 13117))
        time.sleep(1)

if __name__ == '__main__':
    main()   