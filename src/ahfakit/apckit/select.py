import select
import socket


class Poll(object):

    def __init__(self, poller=None):
        self.fd_map = {}
        self.poller = poller if poller else select.epoll()
        self.timeout = None

    def poll(self):
        result = ([], [], [])
        for fd, event in self.poller.poll(self.timeout):
            if event & select.POLLIN:
                result[0].append(self.fd_map[fd])
            elif event & select.POLLOUT:
                result[1].append(self.fd_map[fd])
            elif event & select.POLLERR or event & select.POLLHUP:
                result[2].append(self.fd_map[fd])
        return result

    def register(self, sock, event):
        fd = sock.fileno()
        self.poller.register(fd, event)
        self.fd_map[fd] = sock

    def unregister(self, sock):
        fd = sock.fileno()
        self.poller.unregister(fd)
        del self.fd_map[fd]


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("localhost", 8000))
    sock.setblocking(False)
    sock.listen(5)
    poll = Poll()
    poll.register(sock, select.POLLIN)
    while True:
        readable, writable, exceptional = poll.poll()
        for i in readable:
            if i is sock:
                conn, addr = sock.accept()
                poll.register(conn, select.POLLIN)
                print("新连接", addr)
            else:
                data = i.recv(1024)
                if data == b"":
                    print("连接已断开")
                    poll.unregister(i)
                else:
                    print(data)


if __name__ == "__main__":
    main()
