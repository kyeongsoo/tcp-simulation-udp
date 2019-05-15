import socket
import time


# define constants
bufferSize = 1024
serverAddress = ("127.0.0.1", 5100)


def server(n_channels, pkt_loss_rate, svr_base_port, ch_base_port, cl_base_port,
           n_pkts):
    ch_addr = [None]*n_channels
    svr_addr = [None]*n_channels
    svr_skt = [None]*n_channels
    for i in range(n_channels):
        # create a list of pairs of channel address and port
        ch_addr[i] = ("127.0.0.1", ch_base_port+i)
        
        # create and bind server sockets
        svr_addr[i] = ("127.0.0.1", svr_base_port+i)
        svr_skt[i] = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        svr_skt[i].bind(svr_addr[i])
        print("SVR{0:d}: The server is up and listening.".format(i))

    # process 'Request' message
    while True:
        isRequestRecived = False
        for i in range(n_channels):
            rx_data, rx_addr = svr_skt[i].recvfrom(bufferSize)
            rx_msg = rx_data.decode("utf-8")
            print("SVR{0:d}: Received {1} from {2}".format(i, rx_msg, rx_addr))
            if "Request" in rx_msg:
                isRequestRecived = True

        if isRequestRecived:
            break

    # send data to the client over multiple channels
    n_rtxs = 0                  # number of retransmissions
    for sn in range(n_pkts):
        tx_msg = "Data: SN={0:d}".format(sn)
        tx_data = tx_msg.encode()
        for i in range(n_channels):
            svr_skt[i].sendto(tx_data, ch_addr[i])
            print("SVR{0:d}: Sent {1} to {2}".format(i, tx_msg, ch_addr[i]))

        ack_sn = -1
        while True:
            for i in range(n_channels):
                ack_data, ack_addr = svr_skt[i].recvfrom(bufferSize)
                ack_msg = ack_data.decode("utf-8")
                print("SVR{0:d}: Received {1} from {2}".format(i, ack_msg, ack_addr))

                # if there's at least one "ACK" from the channles, ACK SN is
                # updated
                if "ACK" in ack_msg:
                    # update the ACK sequence number
                    tmp = int((ack_msg.split(' ')[1]).split('=')[1])  # 'tmp' is an integer
                    if tmp > ack_sn:
                        ack_sn = tmp
                        print("SVR{0:d}: ACK SN={1:d}".format(i, ack_sn))

            if ack_sn == sn:    # acked
                break         # exit from the while loop
            else:             # retransmission
                n_rtxs += 1
                for i in range(n_channels):
                    svr_skt[i].sendto(tx_data, ch_addr[i])
                    print("SVR{0:d}: Sent {1} to {2}".format(i, tx_msg, ch_addr[i]))

    # save the results to a file
    fname = "./output/mptcp_plr-{0:.1f}_ch-{1:d}.out".format(pkt_loss_rate, n_channels)
    with open(fname, 'w') as file:
        file.write("plt={0:.1f},ch={1:d},n_rtxs={2:d}".format(pkt_loss_rate, n_channels, n_rtxs))


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
        "-L",
        "--pkt_loss_rate",
        help="packet loss rate; default is 0.3",
        default=0.3,
        type=float)
    parser.add_argument(
        "--svr_base_port",
        help="base port number for server; default is 31000",
        default=31000,
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
        help="number of packets to transmit to the client; default is 10",
        default=10,
        type=int)
    args = parser.parse_args()
    n_channels = args.n_channels
    pkt_loss_rate = args.pkt_loss_rate  # used for output file name
    svr_base_port = args.svr_base_port
    ch_base_port = args.ch_base_port
    cl_base_port = args.cl_base_port
    n_pkts = args.n_pkts

    # run the server
    server(n_channels, pkt_loss_rate, svr_base_port, ch_base_port, cl_base_port, n_pkts)
