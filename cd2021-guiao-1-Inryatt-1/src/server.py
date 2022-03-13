"""CD Chat server program."""
import logging
import socket
import json
import selectors
from .protocol import CDProto, CDProtoBadFormat
logging.basicConfig(filename="server.log", level=logging.DEBUG)

class Server:
    """Chat Server process."""

    def __init__(self):
        HOST = ""
        PORT = 50005
        self.sel = selectors.DefaultSelector()
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((HOST, PORT))
        self.s.listen(100)  
        self.sel.register(self.s, selectors.EVENT_READ, self.accept)# Listens for activity on the socket to receive new connections
        self.conns = {}                                             # Here'll be stored the user's usernames and joined channels -- is our "database" (no sql involved)
        logging.debug("===========Server initialized==========")

    def accept(self, sock, mask):                                   # Receive and treat a RegisterMessage
        conn, addr = self.s.accept()                                # Get the info for who's connecting
        msg = CDProto.recv_msg(conn)                                # Receive the message as defined on protocol
        name = msg.get()                                            # Gets the username 
        if conn not in self.conns:                                  # If this is a new connection
            self.conns[conn] = [                                    # Conn serves as key, values are username and a list with joined channels
                name,
                ["None"],
            ]                                                       # Registers the new connection in the default channel
        self.sel.register(                                          # And listens for messages coming from that connection (socket)
            conn, selectors.EVENT_READ, self.read
        )  
        logging.debug("Connected %s as %s", conn, self.conns[conn][0])

    def read(self, conn, mask):
        try:
            msg = CDProto.recv_msg(conn)                            # Receive incoming message
            logging.debug("received %s from %s", msg, self.conns[conn][0])
            if msg.type() == "join":                                # If the message is a JoinMessage
                toJoin = msg.get().strip()                          # Get the channel to join
                if toJoin[0]!="#": toJoin="#"+toJoin                # Regardless if user types #chan or chan, result shall be the same
                if toJoin in self.conns[conn][1]:                   # If user is already in channel
                    toSwap=self.conns[conn][1].index(toJoin)
                    self.conns[conn][1].pop(toSwap)
                    self.conns[conn][1].append(toJoin)              # Guarantees the last joined channel will be last in list (active channel)
                else:
                    self.conns[conn][1].append(toJoin)              # Simply adds the channel to the user's channel list
                logging.debug("client %s joined %s", self.conns[conn][0], toJoin)
            else:                                                   # If it isn't a joinMessage, it'll be a TextMessage
                for user in self.conns:    
                    sender_ch=self.conns[conn][1][-1]               # Get the sender's last (active) channel in their list
                    for receiver_ch in self.conns[user][1]:         # Iterate over all channels the other users are in
                        if (sender_ch == receiver_ch): #& (
                                #self.conns[user][0] != self.conns[conn][0])    #Older code which didn't send the message back to sender 
                                # user[1] is channel, user[0] is username
                                # check if is in same channel 
                            CDProto.send_msg(user, msg)             # Sends the message 
                            logging.debug("sent %s to %s", msg, self.conns[user][0])
                            break                                   # Move onto next user
        except (CDProtoBadFormat , ConnectionResetError)as ex:      # Either a wrongly formatted message 
                                                                    #  (in which case something went wrong clientside 
                                                                    #   and we don't want the server to crash as well) 
                                                                    # or the user left the server
            logging.debug("client %s exit", self.conns[conn][0])
            self.sel.unregister(conn)                               # Unregister the selector listening for user's messages
            self.conns.pop(conn)                                    # Remove user from user list
            conn.close()                                            # Close the connection with user        

    def loop(self):
        """Loop indefinetely."""
        while True:
            try:
                for event, mask in self.sel.select():
                    callback = event.data
                    msg = callback(event.fileobj, mask)
                #for c in self.conns:                              For debugging purposes
                #    print("Currently online: ", self.conns[c])
            except KeyboardInterrupt:                              # In case I stop the server via Ctrl-C, close server properly
                if self.s:                                         # which enables me to restart it immediately 
                    self.s.close()                                 # and not have to jiggle the port numbers around
                    print()                                        # So the shell prompt appears prettier
                break                                              # End While cycle
