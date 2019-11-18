from socket import *
import random


def main():
    ssocket = socket(AF_INET, SOCK_DGRAM)
    ssocket.bind(('', 2014))
    print("I will be waiting on port", 2014)

    while True:
        data, clientAddress = ssocket.recvfrom(1024)
        newData = data.upper()
        ssocket.sendto(newData, clientAddress)


main()
