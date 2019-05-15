import subprocess
import time
import threading
# import socket
import sys
sys.path.insert(0, './')
import channel
import client
import server


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

    # start a server
    t_svr = threading.Thread(target=server.server,
                             kwargs=dict(
                                 n_channels=n_channels,
                                 pkt_loss_rate=pkt_loss_rate,
                                 svr_base_port=svr_base_port,
                                 ch_base_port=ch_base_port,
                                 cl_base_port=cl_base_port,
                                 n_pkts=n_pkts
                             ))
    t_svr.start()
    print('server is started')

    # start channels
    time.sleep(3)    # wait until the server is up and running
    for i in range(n_channels):
        t_ch = threading.Thread(target=channel.channel,
                                kwargs=dict(
                                    pkt_loss_rate=pkt_loss_rate,
                                    svr_base_port=svr_base_port,
                                    ch_base_port=ch_base_port,
                                    cl_base_port=cl_base_port,
                                    ch_number=i,
                                    ch_delay=ch_delay,
                                    n_pkts=n_pkts
                                ))
        t_ch.start()
        print('channel {0:d} is started'.format(i))

    # start a client
    time.sleep(3)    # wait until the channels are up and running
    t_cl = threading.Thread(target=client.client,
                            kwargs=dict(
                                n_channels=n_channels,
                                ch_base_port=ch_base_port,
                                cl_base_port=cl_base_port,
                                n_pkts=n_pkts
                            ))
    t_cl.start()
    print('client is started')
