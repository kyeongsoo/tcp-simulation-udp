from socket import socket, AF_INET, SOCK_STREAM

sock = socket(AF_INET, SOCK_STREAM)
sock.bind(("localhost", 5505))
sock.listen(1)
while True:
    try:
        while self.running:
            try:
                c, addr = socket.accept()
                print("Connection accepted from " + repr(addr[1]))
                # do special stuff here...
                print("sending...")
                continue
            except (SystemExit, KeyboardInterrupt):
                print("Exiting....")
                service.stop_service()
                break
            except Exception as ex:
                print("======> Fatal Error....\n" + str(ex))
                print(traceback.format_exc())
                self.running = False
                service.stop_service()
                raise
    except (SystemExit, KeyboardInterrupt):
        print("Force Exiting....")
        service.stop_service()
        raise

def stop_service(self):
    """
    properly kills the process: https://stackoverflow.com/a/16736227/4225229
    """
    self.running = False
    socket.socket(socket.AF_INET,
                  socket.SOCK_STREAM).connect((self.hostname, self.port))
    self.socket.close()
