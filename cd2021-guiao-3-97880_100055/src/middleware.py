"""Middleware to communicate with PubSub Message Broker."""
from collections.abc import Callable
from enum import Enum
from queue import LifoQueue, Empty
import socket
import json
import pickle
import xml
from typing import Any

class MiddlewareType(Enum):
    """Middleware Type"""

    CONSUMER = 1
    PRODUCER = 2

def listlist(listlistlist):
    for listlistlistlist in listlistlist:
        print(*listlistlistlist)


class Queue:
    """Representation of Queue interface for both Consumers and Producers."""
    def __init__(self, topic, _type=MiddlewareType.CONSUMER):
        """Open socket to broker"""
        HOST = "localhost"
        PORT = 5000
        self.type = _type
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((HOST, PORT))
        self.topic = topic

    def push(self, value):
        """Sends data to broker."""
           
        encoded_msg=str(value).encode("utf-8")                   
        size=len(encoded_msg).to_bytes(2,'big')                

        to_send = size+encoded_msg
        self.s.send(to_send)

    def pull(self):
        """Receives (topic, data) from broker.
        Should BLOCK the consumer!"""
        #implemented in each specific queue
    
    def list_topics(self, callback: Callable): # callable é uma função chamada ao receber a lista
        """Lists all topics available in the broker."""
         #implemented in each specific queue

    def cancel(self):
        """Cancel subscription."""
         #implemented in each specific queue


class JSONQueue(Queue):
    """Queue implementation with JSON based serialization."""
    def __init__(self,topic, _type=MiddlewareType.CONSUMER):
        super().__init__(topic, _type)

    def __init__(self, topic, _type=MiddlewareType.CONSUMER):
        super().__init__(topic, _type=_type)
        #Initial message to let the broker know which type we use to communicate
        register_msg = 0
        super().push(register_msg) 
        if _type == MiddlewareType.CONSUMER: 
            self.sub(topic)

    def sub(self,topic):
        """Send a subscribe message for the specified topic in JSON"""
        msg = {
            'command':'sub',
            'topic':str(topic)
        }
        msg=json.dumps(msg) 
        super().push(msg) # turns JSON into bytestring

    def push(self, value):
        """Push a publish message in JSON"""
        msg = {
            'command':'pub',
            'topic':str(self.topic),
            'content':str(value)        
        }
        msg=json.dumps(msg)
        super().push(msg) # turns JSON into bytestring
        
    def cancel(self):
        msg = {
            'command':'cancel',
            'topic':str(self.topic)
        }
        msg=json.dumps(msg)
        super().push(msg) # turns JSON into bytestring
   
    def pull(self):
        """Get the messages from the topics we're subscribed to, in JSON"""
        # Doing this will block until a messagr is received

        msg_size = int.from_bytes(self.s.recv(2),byteorder="big")
        unparsed_msg = self.s.recv(msg_size)

        msg = json.loads(unparsed_msg)
        if msg['command']=='pub':
            print("received pub :",msg)
            return  (msg['topic'], int(msg['content']))
        elif msg['command']=='list_rep':
            print("AAAAAAA",msg['list'],type(msg['list']))
            self.callable(msg['list'])
            return (msg['list'])

    def list_topics(self,callable):
        """Get a list of the existing topics from the Broker"""
        msg = {'command':'list'}
        msg=json.dumps(msg)
        super().push(msg)
        self.callable = callable 

class XMLQueue(Queue):
    """Queue implementation with XML based serialization."""
    def __init__(self,topic, _type=MiddlewareType.CONSUMER):
        super().__init__(topic, _type)

    def __init__(self, topic, _type=MiddlewareType.CONSUMER):
        super().__init__(topic, _type=_type)
        #Initial message to let the broker know which type we use to communicate
        register_msg = 1
        super().push(register_msg)
        if _type == MiddlewareType.CONSUMER: 
            self.sub(topic)

    def sub(self, topic):
        """Subscribe to a topic in XML"""
        msg = {
            'command' : 'sub',
            'topic' : str(topic)
        }
        elem = xml.etree.ElementTree.Element("msg", attrib=msg)
        encoded_msg = xml.etree.ElementTree.tostring(elem)

        size = len(encoded_msg).to_bytes(2, 'big')                
        to_send = size+encoded_msg

        self.s.send(to_send)

    def cancel(self): #TODO eventually
        msg = {
            'command':'cancel',
            'topic':str(self.topic)
        }
        elem = xml.etree.ElementTree.Element("msg", attrib=msg)
        encoded_msg = xml.etree.ElementTree.tostring(elem)

        size = len(encoded_msg).to_bytes(2, 'big')                
        to_send = size+encoded_msg

        self.s.send(to_send)

    def push(self, value):
        """Push a message to a topic, in XML"""
        msg = {
            'command':'pub',
            'topic':str(self.topic),
            'content':str(value)
        }
        elem = xml.etree.ElementTree.Element("msg",attrib=msg)
        encoded_msg = xml.etree.ElementTree.tostring(elem)

        size = len(encoded_msg).to_bytes(2,'big')                
        to_send = size + encoded_msg

        self.s.send(to_send)
   
    def pull(self):
        """Get the messages from the subscribed topics, in XML"""
        if(self.type == MiddlewareType.CONSUMER):
            msg_size = int.from_bytes(self.s.recv(2), byteorder="big")
            unparsed_msg = self.s.recv(msg_size)

            my_xml = xml.etree.ElementTree.fromstring(unparsed_msg)
            actual_msg = my_xml.attrib

        if actual_msg['command']=='pub':
            return  (actual_msg['topic'], int(actual_msg['content']))
        elif actual_msg['command']=='list_rep':
            self.callable(actual_msg['list'])
            return (actual_msg['list'])

        return (actual_msg['topic'], int(actual_msg['content']))

    def list_topics(self,callable):
        """Get a list of the existing topics from the broker, in XML"""
        msg = {'command':'list'}

        elem = xml.etree.ElementTree.Element("msg",attrib=msg)
        print("OH LOOK A PROBLEM",elem)
        encoded_msg = xml.etree.ElementTree.tostring(elem)

        size = len(encoded_msg).to_bytes(2,'big')                
        to_send = size + encoded_msg
        self.s.send(to_send)
        self.callable = callable
        
class PickleQueue(Queue):
    """Queue implementation with Pickle based serialization."""

    def __init__(self, topic, _type=MiddlewareType.CONSUMER):
        super().__init__(topic, _type=_type)
        #Initial message to let the broker know which type we use to communicate
        register_msg = 2
        super().push(register_msg)
        if _type == MiddlewareType.CONSUMER: 
            self.sub(topic)

    def sub(self,topic):
        """Subscribe to a topic, in Pickle"""
        msg = {
            'command':'sub',
            'topic':str(topic)
        }
        encoded_msg = pickle.dumps(msg)        
        size = len(encoded_msg).to_bytes(2, 'big')                

        to_send = size + encoded_msg    #  It's a byte stream, we can just send it together
        self.s.send(to_send) 

    def cancel(self): #TODO eventually
        msg = {
            'command':'cancel',
            'topic':str(self.topic)
        }
        encoded_msg = pickle.dumps(msg)        
        size = len(encoded_msg).to_bytes(2, 'big')                

        to_send = size + encoded_msg    #  It's a byte stream, we can just send it together
        self.s.send(to_send)

    def push(self, value):
        """Push a message to a topic, in Pickle"""
        msg = {
            'command' : 'pub',
            'topic' : str(self.topic),
            'content' : str(value)
            }
        encoded_msg = pickle.dumps(msg)
        size = len(encoded_msg).to_bytes(2, 'big')                

        to_send = size + encoded_msg
        self.s.send(to_send)

    def pull(self):
        """Get the messages from topics we're subscribed to, in Pickle"""
        msg_size = int.from_bytes(self.s.recv(2), byteorder="big")
        unparsed_msg = self.s.recv(msg_size)
        try:
            msg = pickle.loads(unparsed_msg)
        except pickle.UnpicklingError:
            msg = {'topic' : "error", 'content' : 2} # Should not happen.

        if msg['command']=='pub':
            return  (msg['topic'], int(msg['content']))
        elif msg['command']=='list_rep':
            self.callable(msg['list'])
            return (msg['list'])
            

    def list_topics(self,callable):
        """Get a list of the existing topics from the broker, in Pickle"""
        msg = {
            'command' : 'list_rep'
        }
        encoded_msg = pickle.dumps(msg)
        size = len(encoded_msg).to_bytes(2, 'big')                
        
        to_send = size + encoded_msg
        self.s.send(to_send)
        self.callable = callable
        
    
    
