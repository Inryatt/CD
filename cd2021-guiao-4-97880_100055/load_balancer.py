# coding: utf-8

import socket
import selectors
import signal
import logging
import argparse
import time


# configure logger output format
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
    datefmt="%m-%d %H:%M:%S",
)
logger = logging.getLogger("Load Balancer")


# used to stop the infinity loop
done = False

sel = selectors.DefaultSelector()

policy = None
mapper = None

# implements a graceful shutdown
def graceful_shutdown(signalNumber, frame):
    logger.debug("Graceful Shutdown...")
    global done
    done = True


# n to 1 policy
class N2One:
    def __init__(self, servers):
        self.servers = servers

    def select_server(self):
        return self.servers[0]

    def update(self, *arg):
        pass


# round robin policy
class RoundRobin:
    def __init__(self, servers):
        self.servers = servers
        self.rr_count = -1
        print("Started RoundRobin")

    def select_server(self):
        print("count=", self.rr_count)
        if self.rr_count == len(self.servers) - 1:
            print("reached last server")
            self.rr_count = 0
        else:
            print("Next Server: ", self.rr_count)
            self.rr_count = self.rr_count + 1

        print("going to:", self.rr_count)
        return self.servers[self.rr_count]

    def update(self, *arg):
        pass


# least connections policy
class LeastConnections:
    def __init__(self, servers):
        self.servers = servers
        self.connections = {}
        for serv in servers:
            self.connections[serv[1]] = 0

    def select_server(self):
        print("Connections:", self.connections)
        minCons = 1000
        selectedServer = None
        # All this is quite wrong, delete :)
        for s in servers:
            if self.connections[s[1]] < minCons:
                minCons = self.connections[s[1]]
                selectedServer = s
        if selectedServer == None:
            print("Something went terribly wrong!")
            return None
        else:
            print("Sending to", selectedServer)
            self.connections[selectedServer[1]] = (
                self.connections[selectedServer[1]] + 1
            )
            return selectedServer

    def update(self, *arg):
        print(arg[0], "AAAAAAAAA")
        if arg[0] != None:
            s = arg[0][1]
            self.connections[s] = self.connections[s] - 1


# least response time
class LeastResponseTime:
    def __init__(self, servers):
        self.servers = servers
        self.connections = {}
        for serv in servers:
            self.connections[serv[1]] = 0

    def select_server(self):
        print("DEBUG: We have: ",self.connections,"\n")

        selectedServer = min(self.connections, key=self.connections.get)
        print("DEBUG: And you're getting:",selectedServer)
        self.connections[selectedServer] = time.time()

        for serv in servers:
            if serv[1] == selectedServer:
                selectedServer = serv
                break
        return selectedServer

    def update(self, *arg):
        # print("DEBUG: ",arg[0] ,"finished, taking time now")

        self.connections[arg[0][1]] = time.time() - self.connections[arg[0][1]]


POLICIES = {
    "N2One": N2One,
    "RoundRobin": RoundRobin,
    "LeastConnections": LeastConnections,
    "LeastResponseTime": LeastResponseTime,
}


class SocketMapper:
    def __init__(self, policy):
        self.policy = policy
        self.map = {}

    def add(self, client_sock, upstream_server):
        client_sock.setblocking(False)
        sel.register(client_sock, selectors.EVENT_READ, read)
        upstream_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # print("upsv:",upstream_server)
        upstream_sock.connect(upstream_server)
        upstream_sock.setblocking(False)
        sel.register(upstream_sock, selectors.EVENT_READ, read)
        logger.debug("Proxying to %s %s", *upstream_server)
        self.map[client_sock] = (upstream_sock, upstream_server)

    def delete(self, sock):
        sel.unregister(sock)
        sock.close()
        if sock in self.map:
            self.map.pop(sock)

    def get_sock(self, sock):
        for client, upstream in self.map.items():
            if upstream[0] == sock:
                return client
            if client == sock:
                return upstream[0]
        return None

    def get_upstream_sock(self, sock):
        return self.map.get(sock)[0]

    def get_all_socks(self):
        """Flatten all sockets into a list"""
        return list(sum(self.map.items(), ()))


def accept(sock, mask):
    client, addr = sock.accept()
    logger.debug("Accepted connection %s %s", *addr)
    mapper.add(client, policy.select_server())


def read(conn, mask):
    data = conn.recv(4096)
    if len(data) == 0:  # No messages in socket, we can close down the socket
        if mapper.map.get(conn) != None:
            # print("upstream:",mapper.map.get(conn)[1])
            policy.update(mapper.map.get(conn)[1])
        mapper.delete(conn)
    else:
        mapper.get_sock(conn).send(data)


def main(addr, servers, policy_class):
    global policy
    global mapper

    # register handler for interruption
    # it stops the infinite loop gracefully
    signal.signal(signal.SIGINT, graceful_shutdown)

    policy = policy_class(servers)
    mapper = SocketMapper(policy)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(addr)
    sock.listen()
    sock.setblocking(False)

    sel.register(sock, selectors.EVENT_READ, accept)

    try:
        logger.debug("Listening on %s %s", *addr)
        while not done:
            events = sel.select(timeout=1)
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)

    except Exception as err:
        logger.error(err, exc_info=1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pi HTTP server")
    parser.add_argument("-a", dest="policy", choices=POLICIES)
    parser.add_argument(
        "-p", dest="port", type=int, help="load balancer port", default=8080
    )
    parser.add_argument(
        "-s", dest="servers", nargs="+", type=int, help="list of servers ports"
    )
    args = parser.parse_args()

    servers = [("localhost", p) for p in args.servers]

    main(("127.0.0.1", args.port), servers, POLICIES[args.policy])
