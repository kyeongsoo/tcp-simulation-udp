import subprocess
import time
# import socket
# import sys
# sys.path.insert(0, './')
# from channel import channel

# define constants
# serverAddressPort = ("127.0.0.1", 5100)
# clientAddressPort = ("127.0.0.1", 5102)
# bufferSize  = 1024


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
    subprocess.Popen([
        'python', 'server.py',
        '--n_channels', str(n_channels),
        '--pkt_loss_rate', str(pkt_loss_rate),
        '--svr_base_port', str(svr_base_port),
        '--ch_base_port', str(ch_base_port),
        '--cl_base_port', str(cl_base_port),
        '--n_pkts', str(n_pkts)
    ])
    print('server is started')

    # start channels
    time.sleep(3)    # wait until the server is up and running
    for i in range(n_channels):
        subprocess.Popen([
            'python', 'channel.py',
            '--pkt_loss_rate', str(pkt_loss_rate),
            '--svr_base_port', str(svr_base_port),
            '--ch_base_port', str(ch_base_port),
            '--cl_base_port', str(cl_base_port),
            '--ch_number', str(i),
            '--ch_delay', str(ch_delay),
            '--n_pkts', str(n_pkts)
        ])
        print('channel {0:d} is started'.format(i))

    # start a client
    time.sleep(3)    # wait until the channels are up and running
    subprocess.Popen([
        'python', 'client.py',
        '--n_channels', str(n_channels),
        '--ch_base_port', str(ch_base_port),
        '--cl_base_port', str(cl_base_port),
        '--n_pkts', str(n_pkts)
    ])
    print('client is started')
