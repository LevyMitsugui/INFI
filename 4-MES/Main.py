from Plantfloor import *
from Recipe.Recipe import *
import threading
import time
import queue
import mysql.connector

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
myQueue.orderedPutput(order)