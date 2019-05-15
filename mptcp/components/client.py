import socket


# define constants
bufferSize  = 1024


def client(n_channels, ch_base_port, cl_base_port, n_pkts):
    ch_addr = [None]*n_channels
    cl_addr = [None]*n_channels
    cl_skt = [None]*n_channels
    for i in range(n_channels):
        # create a list of pairs of channel address and port
        ch_addr[i] = ("127.0.0.1", ch_base_port+i)
        
        # create and bind client sockets
        cl_addr[i] = ("127.0.0.1", cl_base_port+i)
        cl_skt[i] = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        cl_skt[i].bind(cl_addr[i])
        print("CL{0:d}: The client is up and listening.".format(i))
    
    # send a request message to the server through channels
    rqst = "Request"
    for i in range(n_channels):
        cl_skt[i].sendto(rqst.encode(), ch_addr[i])
        print("CL{0:d}: Sent {1} to {2}".format(i, rqst, ch_addr[i]))

    sn = -1
    while True:
        for i in range(n_channels):
            rx_data, rx_addr = cl_skt[i].recvfrom(bufferSize)
            rx_msg = rx_data.decode("utf-8")
            print("CL{0:d}: Received {1} from {2}".format(i, rx_msg, rx_addr))

            # if there is at least one "Data" from the channles, SN is updated
            if "Data" in rx_msg:
                # update the data sequence number
                tmp = int((rx_msg.split(' ')[1]).split('=')[1])  # 'tmp' is an integer
                if tmp > sn:
                    sn = tmp

        ack_msg = "ACK: SN=" + str(sn)
        ack_data = ack_msg.encode()
        for i in range(n_channels):
            cl_skt[i].sendto(ack_data, ch_addr[i])
            print("CL{0:d}: Sent {1} to {2}".format(i, ack_msg, ch_addr[i]))

        if sn == n_pkts-1:
            return 0        # to end the function


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-C",
        "--n_channels",
        help="number of channels; default is 2",
        default=2,
        type=int)
    parser.add_argument(
        "--ch_base_port",
        help="base port number for channels; default is 31100",
        default=31100,
        type=int)
    parser.add_argument(
        "--cl_base_port",
        help="base port number for client; default is 31200",
        default=31200,
        type=int)
    parser.add_argument(
        "-P",
        "--n_pkts",
        help="number of packets to receive from the server; default is 10",
        default=10,
        type=int)
    args = parser.parse_args()
    n_channels = args.n_channels
    ch_base_port = args.ch_base_port
    cl_base_port = args.cl_base_port
    n_pkts = args.n_pkts


    # run the client
    client(n_channels=n_channels,
           ch_base_port=ch_base_port,
           cl_base_port=cl_base_port,
           n_pkts=n_pkts)
