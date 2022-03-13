"""Message Broker"""
import enum
from typing import Dict, List, Any, Tuple
import socket
import selectors
import json
import xml
import pickle
class Serializer(enum.Enum):
    """Possible message serializers."""

    JSON = 0
    XML = 1
    PICKLE = 2


class Broker:
    """Implementation of a PubSub Message Broker."""

    def __init__(self):
        """Initialize broker."""
        self.canceled = False
        self._host = "localhost"
        self._port = 5000

        self.sel = selectors.DefaultSelector()

        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.s.bind((self._host,self._port))
        self.s.listen(100)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.sel.register(self.s,selectors.EVENT_READ,self.accept) # regista a socket do broker no selector, sp que alguém se tentar
                                                                   # connectar é processado na função accept

        self.topics = {
            #str key: topic
            #str value: last message in that topic
        } 

        self.subscriptions = {
            #str key: topic
            #list value: conns
        } 

        self.clients = { 
            #key:conn                      
            #values: msgtype                           
        }

    def accept(self, sock, mask):
        conn, addr = sock.accept()
        # The broker, after accepting a connection, always expects a message with the serialization type
        size = int.from_bytes(conn.recv(2),byteorder="big")
        type = int(conn.recv(size))
        self.clients[conn] = type # Register client type in clients dict
        self.sel.register(conn,selectors.EVENT_READ,self.read) # regista a socket conectada ao broker no selector, sp que recebemos 
                                                               # informação da sock, esta é processada na função read!  

    def read(self, sock, mask):
        try:
            msg_type = -1 
            size = int.from_bytes(sock.recv(2),byteorder="big")
            if size == 0: # Empty message! Close this socket.
                self.sel.unregister(sock)
                self.clients.pop(sock)
                sock.close()
                for topic in self.subscriptions.keys(): # Removes socket from topics dictionary in case the socket was subscribed to any topic
                    for conn in self.subscriptions[topic]:
                        if conn == sock:
                            self.subscriptions[topic].remove(conn)
                return
            #===========Recieve the unserialized message=================
            msg = sock.recv(size) #
            if(msg == ''): # Empty message! Close this socket.
                self.sel.unregister(sock)
                self.clients.pop(sock)
                sock.close()
                for topic in self.subscriptions.keys():
                    for conn in self.subscriptions[topic]:
                        if conn == sock:
                            self.subscriptions[topic].pop(conn)
                return
            #===========Check client serialization type=================
            for conn in self.clients.keys():
                if sock == conn:
                    msg_type = self.clients[conn]
                    break
            #===========Load message up according to type===================
            actual_msg = {}
            if msg_type ==- 1:
                self.canceled = True # TODO
                return
            elif msg_type == 0:
                # process json msg
                actual_msg = json.loads(msg)
                command = actual_msg["command"]
            elif msg_type == 1:
                # process xml msg
                my_xml = xml.etree.ElementTree.fromstring(msg)
                actual_msg = my_xml.attrib
                command = actual_msg["command"]
            elif msg_type == 2:
                #process pickle msg
                actual_msg = pickle.loads(msg)
                command =  actual_msg['command'] 
            #================Process Message=================
            #--Depending on the message command pass to the appropriate function
            if command == 'sub':
                # proccess subscription message (dealing with a consumer)
                # args: topic
                topic=actual_msg['topic']
                self.subscribe(topic,sock) # store subscription
            elif command == 'pub':
                # process publication message (dealing with a producer)
                # args: topic, content
                topic = actual_msg['topic']
                content = actual_msg['content']
                self.put_topic(topic,content) # store last topic message
                self.send_to_consumers(topic,actual_msg)
            elif command == 'list': #TODO
                # return consumer topic list
                topic_list=self.list_topics()
                msg={
                    'command':'list_rep',
                    'list' : topic_list
                } 
                if msg_type == 0:
                    value = json.dumps(msg)
                    encoded_msg = str(value).encode("utf-8")                   
                    size = len(encoded_msg).to_bytes(2,'big')                
                    to_send = size+encoded_msg
                    conn.send(to_send)     
                elif msg_type == 1:
                    value = xml.etree.ElementTree.Element("msg",attrib=msg)
                    encoded_msg = xml.etree.ElementTree.tostring(value)
                    size=len(encoded_msg).to_bytes(2,'big')              
                    to_send = size + encoded_msg
                    conn.send(to_send)
                elif msg_type == 2:
                    encoded_msg = pickle.dumps(msg)
                    size = len(encoded_msg).to_bytes(2,'big')    
                    to_send = size + encoded_msg
                    conn.send(to_send)

            elif command == 'cancel': #TODO?
                # cancels consumer subscription to topic
                # args: topic
                topic=actual_msg['topic']
                self.unsubscribe(topic,sock)
                self.sel.unregister(sock)
            else:
                # should never happen
                self.canceled = True
                return
        except ConnectionResetError:
            self.sel.unregister(sock)
            self.clients.pop(sock)
            sock.close()
            for topic in self.subscriptions.keys():
                    for conn in self.subscriptions[topic]:
                        if conn == sock:
                            self.subscriptions[topic].remove(conn)
            return
    
    def send_to_consumers(self,topic,msg):
            """Send a Message to Consumers subscribed to the given Topic"""
            topics = [] # List of topics which should receive the pub message :p
            if topic[0] == "/":
                topics.append(topic)
                for top in self.subscriptions.keys():
                    if top == topic[:len(top)]:
                        topics.append(topic[:len(top)])
            else:
                topics = [topic]
                
            for topic in topics:
                    if topic in self.subscriptions.keys():
                        for conn in self.subscriptions[topic]:
                            if self.clients[conn] == 0: # Consumer is using json 
                                print("Send to consumers:" , msg,"in ",topic)
                                value = json.dumps(msg)
                                encoded_msg = str(value).encode("utf-8")                   
                                size = len(encoded_msg).to_bytes(2,'big')                
                        
                                to_send = size+encoded_msg
                                conn.send(to_send)
                                
                            elif self.clients[conn] == 1: # Consumer is using xml

                                value = xml.etree.ElementTree.Element("msg",attrib=msg)
                                encoded_msg = xml.etree.ElementTree.tostring(value)
                                size=len(encoded_msg).to_bytes(2,'big')                

                                to_send = size + encoded_msg
                                conn.send(to_send)
                                
                            elif self.clients[conn]==2: # Consumer is using pickle

                                encoded_msg = pickle.dumps(msg)
                                size = len(encoded_msg).to_bytes(2,'big')    
                                to_send = size + encoded_msg
                                conn.send(to_send)
                                
                            else:
                                # ERROR:Something didn't go according to plan
                                self.canceled = True           
                                return    
            
          
    def list_topics(self) -> List[str]:
        """Returns a list of strings containing all topics."""
        topic_list = []
        for topic in self.topics.keys():
            topic_list.append(topic)
        return sorted(topic_list) #alphabetically sorted so topics can be grouped together (hopefully)

    def get_topic(self, topic):
        """Returns the currently stored value in topic."""
        #this will be the last received message 
        if topic in self.topics.keys():
            return self.topics[topic]
        else:
            return None
         

    def put_topic(self, topic, value):
        """Store in topic the value."""
        try:
            self.topics[topic] = int(value) # The value can be parsed as an int
        except:
            self.topics[topic] = value    # The value cannot be parsed as an int

    def list_subscriptions(self, topic: str) :#-> List[socket.socket]:
        """Provide list of subscribers to a given topic."""
        user_list = [] # list of clients (sockets) subscribed to topic
        
        if topic in self.subscriptions.keys():
            user_list = self.subscriptions[topic]
        else:
            self.canceled = True
            return

        to_return = [] # list of clients subscribed to topic, now with serialization type

        for client in user_list:
            if client in self.clients:
                to_return.append((client,self.clients[client]))
            else:
                self.canceled = True
                return

        return to_return

    def subscribe(self, topic: str, address : socket.socket ,_format: Serializer = None): # antes tinha arg Serializer
        """Subscribe to topic by client in address."""
        # This should never happen in normal operation but a test does it >:(
        if address not in self.clients:
            self.clients[address] = _format

        if topic in self.subscriptions:
            # Topic already exist
            self.subscriptions[topic].append(address)
        else:
            # Topic is new
            self.subscriptions[topic] = [address]      


    def unsubscribe(self, topic, address):
        """Unsubscribe to topic by client in address."""
        self.subscriptions[topic].remove(address)


    def run(self):
        """Run until canceled."""
        
        while not self.canceled:
                events = self.sel.select()
                for key, mask in events:
                    callback = key.data
                    callback(key.fileobj, mask)
