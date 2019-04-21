import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 50005
N = 10                          # number of messages

print("UDP target IP: {}".format(UDP_IP))
print("UDP target port: {}".format(UDP_PORT))

for i in range(N):
    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
    message = "packet-{:d}".format(i)
    sock.sendto(message.encode(), (UDP_IP, UDP_PORT))
    print("Sent {}".format(message))
