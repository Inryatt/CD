"""CD Chat client program"""
import logging
import socket
import sys
import selectors
import fcntl
import os

from .protocol import CDProto, CDProtoBadFormat

# set sys.stdin non-blocking
orig_fl = fcntl.fcntl(sys.stdin, fcntl.F_GETFL)
fcntl.fcntl(sys.stdin, fcntl.F_SETFL, orig_fl | os.O_NONBLOCK)
sel = selectors.DefaultSelector()  # selector

logging.basicConfig(filename=f"{sys.argv[0]}.log", level=logging.DEBUG)


class Client:
    """Chat Client process."""

    def __init__(self, name: str = "Foo"):
        """Initializes chat client."""
        #Connects via ipv4 using tcp
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.name = name
        self.HOST = "localhost"
        self.PORT = 50005

    #This is called via the selector that's listening for input activity 
    def got_keyboard_data(self, stdin):
        input = stdin.read().rstrip("\n")   #Get user's input
        if input == "exit":                 #Ends Client Session
            self.s.close()
            exit()
        elif input[0:5] == "/join":         #For user to join other channels
            toJoin = input[5:]              #Get what comes after '/input ', which will be the channel to join
            if toJoin.rstrip() == "":       #If the command is empty, join default
                toJoin = "None"
            msg = CDProto.join(toJoin)      #Write the message 
            CDProto.send_msg(self.s, msg)   # Send the message to let the server know you're joining a channel
            logging.debug(f"joined channel {toJoin}")
        else:
            if input != "":                                      #Ignore empty messages
                #The line below is to avoid having repeated messages
                #in the terminal, since you can see what you type plus the server's echo
                sys.stdout.write('\x1b[1A')                      #Moves cursor to above line and deletes what was there before 
                CDProto.send_msg(self.s, CDProto.message(input)) #Send message  
                logging.debug("Sent %s", CDProto.message(input)) #Log message
                #sys.stdout.write('\x1b[1A')
                #sys.stdout.write('\b \b>')
                #sys.stdout.flush()
                #tried to delete the received < and replace with > but doesnt work :( 
 
    def connect(self):
        """Connect to chat server and setup stdin flags."""
        logging.debug("Connection to server established")                       # For log readability purposes
        self.s.connect((self.HOST, self.PORT))                                  # Connect to the server 
        sel.register(sys.stdin, selectors.EVENT_READ, self.got_keyboard_data)   # Listen for input activity
        sel.register(self.s, selectors.EVENT_READ, self.read)                   # Listen for socket activity
        self.s.setblocking(False)                                               # So it doesn't block
        CDProto.send_msg(self.s, CDProto.register(self.name))                   # Send the message to let server know we're here (RegisterMessage)
        sys.stdout.write("> ")                                                  # For that old-school IRC feel
        sys.stdout.flush()                                                      

    def read(self, sock):
        """Receive Messages via socket"""
        #This is called via the selector that's listening for activity on the socket
        msg = CDProto.recv_msg(sock)                                            # Receive the message as defined on the protocol
        logging.debug("Received: %s", msg)
        if msg:                                                                 # Now redundant, but might as well have some security 
            sys.stdout.write("\b\b< {}\n".format(str(msg.get())))               # Print message to terminal

    def loop(self):
        """Loop indefinetely."""
        while True:
            toSend = sel.select()                                               # The usual method for event treatment
            for event, data in toSend:
                callback = event.data
                msg = callback(event.fileobj)
            sys.stdout.write("> ")                                              # For that old-school IRC feel
            sys.stdout.flush()
