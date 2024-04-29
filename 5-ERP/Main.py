import socket
import threading
import queue
import time
import sys
sys.path.append("..")

from ..Database.DB import *         # TO RUN THE CODE YOU MUST GO TO THE PREVIOUS FOLDER OF INFI AND RUN "python -m INFI.5-ERP.Main"
from xml.dom import minidom

class Parser(object):
    def __init__(self, clientList):
        self.clientList = clientList
        self.db = Database()                                                                            # initialize database connector

    def insertOrder(self, xml):
        info = minidom.parseString(xml)
        #if client does not exist in list:
        if info.getElementsByTagName('Client')[0].getAttribute('NameId') not in self.clientList:
            client = Client()
            self.clientList[info.getElementsByTagName('Client')[0].getAttribute('NameId')] = client
        else:
            client = self.clientList[info.getElementsByTagName('Client')[0].getAttribute('NameId')]
        
        #according to the number of orders, add all orders to the client
        for i in range(len(info.getElementsByTagName('Order'))):
            order = Order(info.getElementsByTagName('Order')[i].getAttribute('Number'),
                          info.getElementsByTagName('Order')[i].getAttribute('WorkPiece'),
                          info.getElementsByTagName('Order')[i].getAttribute('Quantity'),
                          info.getElementsByTagName('Order')[i].getAttribute('DueDate'),
                          info.getElementsByTagName('Order')[i].getAttribute('LatePen'),
                          info.getElementsByTagName('Order')[i].getAttribute('EarlyPen'))
            client.addOrder(order)
            self.db.insertOrder(info.getElementsByTagName('Client')[0].getAttribute('NameId'), order)   # Insert order in the database
            
class Client:
    def __init__(self):
        self.orderList = []

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
            print('[UDP Thread] Waiting for data...')
            data, addr = s.recvfrom(1024)
            print('\n[UDP Thread] Received\n', repr(data), 'from', addr)
            OutputQueue.put(data)
            s.sendto(data, addr)

def __printQueue(outputQueue):
    while True:
        time.sleep(5)
        while not outputQueue.empty():
            print('[Print Thread] \n\n -- -- From Queue -- -- \n', minidom.parseString(outputQueue.get()).toprettyxml())    

def UDPServer(OutputQueue):
    threading.Thread(target=__UDPServer, daemon=True, args=(OutputQueue,)).start()

def printQueue(OutputQueue):
    threading.Thread(target=__printQueue, daemon=True, args=(OutputQueue,)).start()


queueFromUDP = queue.Queue()# create queue for UDP
clientList = {}

UDPServer(queueFromUDP) # start UDP/IP server thread
printQueue(queueFromUDP)# start print queue thread

parser = Parser(clientList)

while True:
    if not queueFromUDP.empty():
        parser.insertOrder(queueFromUDP.get())
        print('Client List: ', clientList)
        for c in clientList.values():
            for o in c.orderList:
                print(o.number, o.workpiece, o.quantity, o.due_date, o.late_pen, o.early_pen)