import socket
import threading
import queue
import time
from xml.dom import minidom

class parser(object):
    def __init__(self, xml):
        self.info = minidom.parseString(xml)

    def __insertOrder(self, clientList):
        #if client does not exist in list:
        if self.info.getElementsByTagName('Client')[0].getAttribute('NameId') not in clientList:
            client = Client()
            clientList[self.info.getElementsByTagName('Client')[0].getAttribute('NameId')] = client
        else:
            client = clientList[self.info.getElementsByTagName('Client')[0].getAttribute('NameId')]
        
        order = Order(self.info.getElementsByTagName('Order')[0].getAttribute('Number'),
                      self.info.getElementsByTagName('Order')[0].getAttribute('WorkPiece'),
                      self.info.getElementsByTagName('Order')[0].getAttribute('Quantity'),
                      self.info.getElementsByTagName('Order')[0].getAttribute('DueDate'),
                      self.info.getElementsByTagName('Order')[0].getAttribute('LatePen'),
                      self.info.getElementsByTagName('Order')[0].getAttribute('EarlyPen'))
        client.addOrder(order)

class Client:
    def __init__(self):
        orderList = []

    def addOrder(self, order):
        #insert order into list keeping number order
        i = 0
        while i < len(self.orderList) and self.orderList[i].number < order.number:
            i += 1
        self.orderList.insert(i, order)

class Order:
    def __init__(self, number, workpiece, quantity, due_date, late_pen, early_pen):
        self.number = number
        self.workpiece = workpiece
        self.quantity = quantity
        self.due_date = due_date
        self.late_pen = late_pen
        self.early_pen = early_pen

def __UDPServer(OutputQueue):
    HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
    PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((HOST, PORT))
        while True:
            print('Waiting for data...')
            data, addr = s.recvfrom(1024)
            print('\nReceived\n', repr(data), 'from', addr)
            OutputQueue.put(data)
            s.sendto(data, addr)

def __printQueue(outputQueue):
    while True:
        time.sleep(5)
        while not outputQueue.empty():
            print('\n\n -- -- From Queue -- -- \n', minidom.parseString(outputQueue.get()).toprettyxml())    

def UDPServer(OutputQueue):
    threading.Thread(target=__UDPServer, daemon=True, args=(OutputQueue,)).start()

def printQueue(OutputQueue):
    threading.Thread(target=__printQueue, daemon=True, args=(OutputQueue,)).start()


queueFromUDP = queue.Queue()# create queue for UDP

UDPServer(queueFromUDP) # start UDP server thread
printQueue(queueFromUDP)# start print queue thread

parser = parser(queueFromUDP.get())

while input() != 'q':
    time.sleep(1)
    print('bruh')
