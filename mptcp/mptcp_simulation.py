import random
import socket
import time
import threading


# define constants
bufferSize = 1024


def channel(pkt_loss_rate, svr_base_port, ch_base_port, cl_base_port, ch_number,
            ch_delay, n_pkts, barrier):
    # initialize server and client address and port
    svr_addr = ("127.0.0.1", svr_base_port+ch_number)
    cl_addr = ("127.0.0.1", cl_base_port+ch_number)
    
    # create and bind a channel socket
    ch_addr = ("127.0.0.1", ch_base_port+ch_number)
    ch_skt = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    ch_skt.bind(ch_addr)
    # print("CH{0:d}: The channel is up and listening.".format(ch_number))

    # synchronize with other threads
    barrier.wait()
    print("CH{0:d} is ready.".format(ch_number))
    
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


def client(n_channels, ch_base_port, cl_base_port, n_pkts, barrier):
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
        # print("CL{0:d}: The client is up and listening.".format(i))

    # synchronize with other threads
    barrier.wait()
    print("A client is ready.")

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


def server(n_channels, pkt_loss_rate, svr_base_port, ch_base_port, cl_base_port,
           n_pkts, barrier):
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
        # print("SVR{0:d}: The server is up and listening.".format(i))

    # synchronize with other threads
    barrier.wait()
    print("A server is ready.")

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
                # print("SVR: ACKED!")  # DEBUG
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
    # return n_rtxs               # return number of retransmissions


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
        "-D",
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
    n_channels = args.n_channels
    pkt_loss_rate = args.pkt_loss_rate
    svr_base_port = args.svr_base_port
    ch_base_port = args.ch_base_port
    cl_base_port = args.cl_base_port
    ch_delay = args.ch_delay
    n_pkts = args.n_pkts

    # for synchronization of threads for a server, a client, and channels
    barrier = threading.Barrier(n_channels+2)
    
    # start a server
    t_svr = threading.Thread(target=server,
                             kwargs=dict(
                                 n_channels=n_channels,
                                 pkt_loss_rate=pkt_loss_rate,
                                 svr_base_port=svr_base_port,
                                 ch_base_port=ch_base_port,
                                 cl_base_port=cl_base_port,
                                 n_pkts=n_pkts,
                                 barrier=barrier
                             ))
    t_svr.start()
    
    # start channels
    for i in range(n_channels):
        t_ch = threading.Thread(target=channel,
                                kwargs=dict(
                                    pkt_loss_rate=pkt_loss_rate,
                                    svr_base_port=svr_base_port,
                                    ch_base_port=ch_base_port,
                                    cl_base_port=cl_base_port,
                                    ch_number=i,
                                    ch_delay=ch_delay,
                                    n_pkts=n_pkts,
                                    barrier=barrier
                                ))
        t_ch.start()
        
    # start a client
    t_cl = threading.Thread(target=client,
                            kwargs=dict(
                                n_channels=n_channels,
                                ch_base_port=ch_base_port,
                                cl_base_port=cl_base_port,
                                n_pkts=n_pkts,
                                barrier=barrier
                            ))
    t_cl.start()
