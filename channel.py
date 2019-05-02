import socket


# define constants
serverAddressPort = ("127.0.0.1", 5100)
channelAddressPort = ("127.0.0.1", 5101)
clientAddressPort = ("127.0.0.1", 5102)
bufferSize  = 1024


def main():
    # create and bind a channel socket
    channelSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    channelSocket.bind(channelAddressPort)
    print("The channel is up and listening.")

    while True:
        rx_data, rx_addr = channelSocket.recvfrom(bufferSize)
        rx_msg = rx_data.decode("utf-8")
        print("Received from {0}->{1}".format(rx_addr, rx_msg))

        if "Data" in rx_msg:    # from the server
            channelSocket.sendto(rx_data, clientAddressPort)
            print("Sent to {0}->{1}".format(clientAddressPort, rx_data))
        else:
            channelSocket.sendto(rx_data, serverAddressPort)
            print("Sent to {0}->{1}".format(serverAddressPort, rx_data))


if __name__ == '__main__':
    main()
