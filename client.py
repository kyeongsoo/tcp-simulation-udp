import socket


# define constants
# serverAddressPort = ("127.0.0.1", 5100)
channelAddressPort = ("127.0.0.1", 5101)
clientAddressPort = ("127.0.0.1", 5102)
bufferSize  = 1024

def main():
    # create and bind a client socket
    clientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    clientSocket.bind(clientAddressPort)
    print("The client is up and listening.")

    # send a request message to the server through the channel
    rqst = "Request"
    clientSocket.sendto(rqst.encode(), channelAddressPort)
    print("Sent to {0}->{1}".format(channelAddressPort, rqst))
    
    while True:
        rx_data, rx_addr = clientSocket.recvfrom(bufferSize)
        rx_msg = rx_data.decode("utf-8")
        print("Received from {0}->{1}".format(rx_addr, rx_msg))
        
        if "Data" not in rx_msg:
            continue
        
        # extract the sequence number of a data packet
        sn = (rx_msg.split(' ')[1]).split('=')[1] # 'sn' is a string

        # acknowledge the received data packet
        ack_msg = "ACK: SN=" + sn
        ack_data = ack_msg.encode()
        clientSocket.sendto(ack_data, channelAddressPort)
        print("Sent to {0}->{1}".format(channelAddressPort, ack_msg))


if __name__ == '__main__':
    main()
