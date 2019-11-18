from socket import *
import datetime
import time


def main():
    serverName = 'localhost'
    port = 2014
    Csocket = socket(AF_INET, SOCK_DGRAM)
    data = 'ping'
    # data = input("Enter a message in lowercase")

    LastPing = 10
    count = 0
    Csocket.settimeout(1)
    print("Attempting to send ", count, "messages")

    while count < LastPing:
        count = count + 1
        startTime = time.time()
        print("The current time is: ", startTime, " and this is message number: ", count)
        Csocket.sendto(data.encode('utf-8'), (serverName, port))

        try:
            newData, clientAddress = Csocket.recvfrom(1024)
            RTT = ((time.time()) - startTime)
            print(newData)
            print(RTT)
        except timeout:
            print(" Request timed out ")
        except Exception as e:
            print(e)
    print("the program is done")


main()
