from Plantfloor import *
from Recipe.Recipe import *
import threading
import time
#import queue
import customQueue
#import mysql.connector

""" class newQueue(queue.Queue):
    def peek(self):
        return self.queue[0]

    def orderedPut(self, item):
        #place item in queue ordered by due date
        for i in range(len(self.queue)):
            if item['DueDate'] < self.queue[i]['DueDate']:
                self.queue.insert(i, item)
                break
        else:
            self.queue.append(item) """

class SQLManager():
    def __init__(self):
        pass

class Manager():

    def __init__(self, orderQueue, requestQueue, doneRequestQueue,recipesFile):
        self.OrderQueue = orderQueue
        self.RequestQueue = requestQueue
        self.DoneRequestQueue = doneRequestQueue
        self.cells = self.__initCells() #hardcoded
        self.__configMachines() #hardcoded

        self.piecesProcessed = []

        self.recipes = self.__reader(recipesFile) #recipes is a reader

    def __initCells(self,): #hardcoded
        cells = []
        for i in range(1):
            cells.append(Cell(i, self.RequestQueue, self.DoneRequestQueue))
        return cells
    

    def __configMachines(self): #hardcoded
        print('[Manager] Configuring Machines')
        self.cells[0].addMachine(Machine(0, 'M1'))
        self.cells[0].addMachine(Machine(1, 'M2'))
        print('[Manager] Machines Configured')
        #self.cells[1].addMachine(Machine(0, 'M1'))
        #self.cells[1].addMachine(Machine(1, 'M2'))
        #print('[Manager] Machines Configured')
        #self.cells[2].addMachine(Machine(0, 'M1'))
        #self.cells[2].addMachine(Machine(1, 'M2'))

        #self.cells[3].addMachine(Machine(0, 'M3'))
        #self.cells[3].addMachine(Machine(1, 'M4'))
        #self.cells[4].addMachine(Machine(0, 'M3'))
        #self.cells[4].addMachine(Machine(1, 'M4'))
        #self.cells[5].addMachine(Machine(0, 'M3'))
        #self.cells[5].addMachine(Machine(1, 'M4'))

    def __reader(self, filename):
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            return [row for row in reader]


    def __postRequests(self):
        while True:
            time.sleep(0.5)
            currOrder = self.OrderQueue.get()

            if currOrder['WorkPiece'] == 'P1' or currOrder['WorkPiece'] == 'P2':
                print('[Manager, postRequests] P1 & P2 are not processable, order will not be posted and will be removed from queue')
                continue

            for row in self.recipes:
                if row['Piece'] == currOrder['WorkPiece']:
                    request = row
                    break
            print('[Manager, postRequests] Posting request: ',request)
            
            quantity = int(currOrder['Quantity'])

            for counter in range(quantity):
                self.RequestQueue.put(request)
            print('[Manager, postRequests] Posted ', quantity, ' requests for ', currOrder['WorkPiece'])
            
    def __wareHouse(self):
        while True:
            time.sleep(2)
            while self.DoneRequestQueue.qsize() > 0:
                self.piecesProcessed.append(self.DoneRequestQueue.get())
                print('[Manager, __wareHouse] WareHouse: ', self.piecesProcessed)

    def postRequests(self):
        #tries to run thread
        try:
            threading.Thread(target=self.__postRequests, daemon=True).start()
            print('[Manager] PostRequests thread started')
        except:
            print('[Manager] Could not start postRequests thread')

    def startWareHouse(self):
        try:
            threading.Thread(target=self.__wareHouse, daemon=True).start()
            print('[Manager] StartWareHouse thread started')
        except:
            print('[Manager] Could not start StartWareHouse thread')

    def addProcessedPiece(self, piece):
        self.piecesProcessed.append(piece)



order = {'clientID' : 'Client AA', 'Order Number' : 18, 'WorkPiece' : 'P4', 'Quantity' : 8, 'DueDate' : 7, 'LatePen' : 10, 'EarlyPen' : 5}

orderQueue = customQueue.customQueue()
requestQueue = customQueue.customQueue()
doneRequestQueue = customQueue.customQueue()

manager = Manager(orderQueue, requestQueue, doneRequestQueue, './Recipe/Recipes.csv')
manager.postRequests()
manager.startWareHouse()
orderQueue.put(order)
input()