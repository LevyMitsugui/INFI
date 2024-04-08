import socket
import threading
import queue
import time
from xml.dom import minidom

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
    

def UDPServer(OutputQueue):
    threading.Thread(target=__UDPServer, daemon=True, args=(OutputQueue,)).start()

def printQueue(outputQueue):
    while True:
        time.sleep(5)
        while not outputQueue.empty():
            print('\n\n -- -- From Queue -- -- \n', minidom.parseString(outputQueue.get()).toprettyxml())


class OrderXML:
    def __init__(self, xmlData):
        self.data = minidom.parseString(xmlData)

    def parse(self):
        order = {}
        order['client'] = self.data.getElementsByTagName('Client')[0].getAttribute('NameId')
        orders = self.data.getElementsByTagName('Order')
        for o in orders:
            order[o.getAttribute('Number')] = {
                'workpiece': o.getAttribute('WorkPiece'),
                'quantity': int(o.getAttribute('Quantity')),
                'due_date': int(o.getAttribute('DueDate')),
                'late_pen': int(o.getAttribute('LatePen')),
                'early_pen': int(o.getAttribute('EarlyPen'))
            }
        return order

    def print(self):
        print(self.data.toprettyxml())



fromUDP = queue.Queue()
UDPServer(fromUDP)

threading.Thread(target=printQueue, daemon=True, args=(fromUDP,)).start()
input()
