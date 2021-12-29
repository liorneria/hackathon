import socket
import time
import struct
import msvcrt
import string
import random
import _thread as thread

FORMAT = "32s 1s 40s 1s 256s 256s"
buffer_size = 1024

# Create a UDP socket
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM , socket.IPPROTO_UDP)
client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    time.sleep(2)
    client.bind(("", 13117))
except:
    pass

print(u"\u001B[33mClient started, listening for offer requests...\u001B[33m")
time_left = time.time() + 10  

# run for 10 second
while time_left > time.time(): 
    try:
        FirstMassage = client.recvfrom(buffer_size)
        FullMassage = struct.unpack('<3Q', FirstMassage[0]) + FirstMassage[1]
         # The message is rejected if it doesn’t start with this cookie 0xfeedbeef.
        if FullMassage[1] == 2 and FullMassage[0] == 2882395322:  
            # The port on the server that the client is supposed to connect to over TCP
            TCP_port = FullMassage[4]  
            print(FullMassage)
            print("“Received offer from " + FullMassage[3] + ", attempting to connect...")
            try:
                team = 'WillyWonka' +"\n" 
                _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
                _socket.connect(('localhost', TCP_port))
                # print(team)
                # send the team name to the server
                _socket.send(team.encode()) 
            except:
                break
            try:
                # print("waiting for start message")
                # receive start massage
                StartMessage = _socket.recv(buffer_size).decode()  
                if StartMessage != "":
                    print(StartMessage)
                    one_key = msvcrt.getch()
                    char = one_key.decode('ASCII')
                    # every key the client press on the keyboard we send to the server
                    _socket.send(char.encode())  
                    ResultMessage = _socket.recv(buffer_size).decode()  
                    if ResultMessage != "":
                        print(ResultMessage)
            except:
                break
    except:
        break

print("Server disconnected, listening for offer requests...")
while True:
    # the client is waiting for offer massage
    massage = client.recvfrom(buffer_size) 

