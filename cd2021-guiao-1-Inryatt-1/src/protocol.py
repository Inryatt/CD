"""Protocol for chat server - Computação Distribuida Assignment 1."""
import json
from datetime import datetime
from socket import socket


class Message:
    """Message Type."""

    def __init__(self,command):                         # All types of message have this attribute
        self.command=command

    def __str__(self):
        return json.dumps(self.__dict__)                

    def type(self):                                     # Getter for the message type
        return self.command
    
class JoinMessage(Message):                             # When user joins a channel this is sent
    """Message to join a chat channel."""
    #channel
    def __init__(self,channel):
        super().__init__("join")
        self.channel=channel

    def get(self):                                      # Getter for the channel attr
        return self.channel
    
class RegisterMessage(Message):                         # When user joins server this is sent 
    """Message to register username in the server."""
    #user
    def __init__(self,user):
        super().__init__("register")
        self.user=user

    def get(self):                                      # Getter for username
        return self.user                                
    
class TextMessage(Message):                             # Transports the user's messages
    """Message to chat with other clients."""

    def __init__(self,message,timestamp:int):
        super().__init__("message")
        self.message=message
        self.ts=timestamp 

    def get(self):                                      # Getter for message contents
        return self.message    


class CDProto:
    """Computação Distribuida Protocol."""

    @classmethod
    def register(cls, username: str) -> RegisterMessage:
        """Creates a RegisterMessage object."""
        msg=RegisterMessage(username)
        return msg

    @classmethod
    def join(cls, channel: str) -> JoinMessage:
        """Creates a JoinMessage object."""
        msg=JoinMessage(channel)
        return msg

    @classmethod
    def message(cls, message: str, channel: str = None) -> TextMessage:
        """Creates a TextMessage object."""
        msg=TextMessage(message, int(datetime.timestamp(datetime.now())))
        return msg

    @classmethod
    def send_msg(cls, connection: socket, msg: Message):       
        """Sends through a connection a Message object."""
        better_msg=str(msg).encode("utf-8")                    # Encode the message so it can be sent via socket
        size=len(better_msg).to_bytes(2,'big')                 # Gets the size of the *encoded* message into a 2-byte format

        connection.sendall(size)
        connection.sendall(better_msg)
        return

    @classmethod
    def recv_msg(cls, connection: socket) -> Message:
        """Receives through a connection a Message object."""
        size=int.from_bytes(connection.recv(2),byteorder="big") # Receive the first two bytes, which contain the size of the msg
        msg=connection.recv(size)                               # Receive the rest of the message
        try:
            msg=json.loads(msg)                                 # Try to load the message into json format
        except:
            raise CDProtoBadFormat                              # If it doesn't work (Incomplete or malformed message)
            return
        key=msg.get("command")                                  # Gets the message type and returns correct message with the contents
       
        if key =="register":
            return RegisterMessage(msg.get("user"))
        elif key=="join":
            return JoinMessage(msg.get("channel"))
        elif key=="message":
            return TextMessage(msg.get("message"),msg.get("ts"))
        else:
            print("Wrong Format")                              # Should never even get here
            return
       

class CDProtoBadFormat(Exception):
    """Exception when source message is not CDProto.""" 
    def __init__(self, original_msg: bytes=None) :
        """Store original message that triggered exception."""
        self._original = original_msg

    @property
    def original_msg(self) -> str:
        """Retrieve original message as a string."""
        return self._original.decode("utf-8")

