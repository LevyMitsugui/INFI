from Plantfloor import *
from Recipe.Recipe import *
import threading
import time
import queue
# import sys
# sys.path.append("..")

# from ..Database.DB import *         # TO RUN THE CODE YOU MUST GO TO THE PREVIOUS FOLDER OF INFI AND RUN "python -m INFI.4-MES.Main"

class newQueue(queue.Queue):
    def peek(self):
        return self.queue[0]

    def orderedPut(self, item):
        #place item in queue ordered by due date
        for i in range(len(self.queue)):
            if item['DueDate'] < self.queue[i]['DueDate']:
                self.queue.insert(i, item)
                break
        else:
            self.queue.append(item)

class SQLManager():
    def __init__(self):
        pass
    #     self.db = Database()

    # def getOrder(self):
    #     orderTup = self.db.processMostUrgentOrder()
    #     if(not orderTup):
    #         return None
    #     order = {'clientID' : orderTup[0][0] , 'Order Number' : orderTup[0][1], 'WorkPiece' : orderTup[0][2], 'Quantity' : orderTup[0][3], 'DueDate' : orderTup[0][4], 'LatePen' : orderTup[0][5], 'EarlyPen' : orderTup[0][6]}
    #     return order

class Manager():
    def __init__(self, orderQueue, requestQueue):
        self.OrderQueue = orderQueue
        self.RequestQueue = requestQueue
        self.cells = self.__initCells() #hardcoded
        self.__configMachines() #hardcoded

    def __initCells(self,): #hardcoded
        cells = []
        for i in range(6):
            cells.append(Cell(i))
        return cells
    
    def __configMachines(self): #hardcoded
        self.cells[0].addMachine(Machine(0, 'M1'))
        self.cells[0].addMachine(Machine(1, 'M2'))
        self.cells[1].addMachine(Machine(0, 'M1'))
        self.cells[1].addMachine(Machine(1, 'M2'))
        self.cells[2].addMachine(Machine(0, 'M1'))
        self.cells[2].addMachine(Machine(1, 'M2'))

        self.cells[3].addMachine(Machine(0, 'M3'))
        self.cells[3].addMachine(Machine(1, 'M4'))
        self.cells[4].addMachine(Machine(0, 'M3'))
        self.cells[4].addMachine(Machine(1, 'M4'))
        self.cells[5].addMachine(Machine(0, 'M3'))
        self.cells[5].addMachine(Machine(1, 'M4'))

    #def makeRequest(self, )

    def __processOrders(self):
        while True:
            currOrder = self.OrderQueue.get()



order = {'clientID' : 'Client AA', 'Order Number' : 18, 'WorkPiece' : 'P5', 'Quantity' : 8, 'DueDate' : 7, 'LatePen' : 10, 'EarlyPen' : 5}

myQueue = newQueue()
# mySQL = SQLManager()
# myQueue.orderedPut(mySQL.getOrder())
myQueue.orderedPut(order)
print(myQueue.peek())