import socket


# define constants
serverAddressPort = ("127.0.0.1", 5100)
channelAddressPort = ("127.0.0.1", 5101)
bufferSize = 1024
    

def main():
    # create and bind a server socket
    serverSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    serverSocket.bind(serverAddressPort)
    print("The server is up and listening.")

    while True:
        # check if the received message is a client request message
        rx_data, rx_addr = serverSocket.recvfrom(bufferSize)
        rx_msg = rx_data.decode("utf-8")

        # DEBUG
        print("Received {0}:{1}".format(rx_msg, rx_addr))
        
        if "Request" not in rx_msg:
            continue

        # send data to the client over the channel
        N=10
        for i in range(N):
            tx_msg = "Data: SN={:d}".format(i)
            tx_data = tx_msg.encode()
            serverSocket.sendto(tx_data, channelAddressPort)
            print("Transmitted {0}:{1}".format(tx_msg, channelAddressPort))
                
            # process ACK
            while True:
                ack_data, ack_addr = serverSocket.recvfrom(bufferSize)
                ack_msg = ack_data.decode("utf-8")
                if "ACK" not in ack_msg:
                    continue
                
                ack_sn = int((ack_msg.split(' ')[1]).split('=')[1])
                if ack_sn == i: # ok
                    break       # exit from the inner while loop
                else:           # retransmission
                    serverSocket.sendto(tx_data, channelAddressPort)
                    print("Retransmitted " + tx_msg)


if __name__ == '__main__':
    main()
