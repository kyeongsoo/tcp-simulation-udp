import random
import socket
import time


# define constants
bufferSize  = 1024


def channel(pkt_loss_rate, svr_base_port, ch_base_port, cl_base_port, ch_number, ch_delay, n_pkts):
    # initialize server and client address and port
    svr_addr = ("127.0.0.1", svr_base_port+ch_number)
    cl_addr = ("127.0.0.1", cl_base_port+ch_number)
    
    # create and bind a channel socket
    ch_addr = ("127.0.0.1", ch_base_port+ch_number)
    ch_skt = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    ch_skt.bind(ch_addr)
    print("CH{0:d}: The channel is up and listening.".format(ch_number))

    while True:
        rx_data, rx_addr = ch_skt.recvfrom(bufferSize)
        rx_msg = rx_data.decode("utf-8")
        print("CH{0:d}: Received {1} from {2}".format(ch_number, rx_msg, rx_addr))
        
        # random packet losses
        loss = "Loss"
        isLost = random.uniform(0, 1) < pkt_loss_rate
        if "Data" in rx_msg:    # from the server
            time.sleep(ch_delay)
            if isLost:
                ch_skt.sendto(loss.encode(), cl_addr)
                print("CH{0:d}: Sent {1} to {2}".format(ch_number, loss, cl_addr))
            else:
                ch_skt.sendto(rx_data, cl_addr)
                print("CH{0:d}: Sent {1} to {2}".format(ch_number, rx_msg, cl_addr))

        else:                   # from the client
            
            # N.B.: we assume no loss for 'Request' and 'Ack' messages for simplicity
            # otherwise, we need to handle packet losses at the client as well.

            # if isLost:
            #     ch_skt.sendto(loss.encode(), svr_addr)
            #     print("Sent {0} to {1}".format(loss, svr_addr))
            # else:
            
            ch_skt.sendto(rx_data, svr_addr)
            print("CH{0:d}: Sent {1} to {2}".format(ch_number, rx_msg, svr_addr))

            # end the function if SN equals to (n_pkts-1)
            if "ACK" in rx_msg:
                sn = int((rx_msg.split(' ')[1]).split('=')[1])  # 'sn' is an integer
                if sn == n_pkts-1:
                    return 0    # to end the function


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pkt_loss_rate",
        help="packet loss rate; default is 0.3",
        default=0.3,
        type=float)
    parser.add_argument(
        "--svr_base_port",
        help="base port number for server; default is 51000",
        default=51000,
        type=int)
    parser.add_argument(
        "--ch_base_port",
        help="base port number for channels; default is 51100",
        default=51100,
        type=int)
    parser.add_argument(
        "--cl_base_port",
        help="base port number for client; default is 51200",
        default=51200,
        type=int)
    parser.add_argument(
        "--ch_number",
        help="channel number; default is 0",
        default=0,
        type=int)
    parser.add_argument(
        "--ch_delay",
        help="channel delay in second; default is 1",
        default=1,
        type=int)
    parser.add_argument(
        "-P",
        "--n_pkts",
        help="number of packets to transmit to the client; default is 10",
        default=10,
        type=int)
    args = parser.parse_args()
    pkt_loss_rate = args.pkt_loss_rate
    svr_base_port = args.svr_base_port
    ch_base_port = args.ch_base_port
    cl_base_port = args.cl_base_port
    ch_number = args.ch_number
    ch_delay = args.ch_delay
    n_pkts = args.n_pkts

    # run the channel
    channel(pkt_loss_rate, svr_base_port, ch_base_port, cl_base_port, ch_number, ch_delay, n_pkts)
