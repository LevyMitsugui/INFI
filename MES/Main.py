from Plantfloor import *
from Recipe.Recipe import *
import threading
import time
import customQueue
import sys
sys.path.append("..")
from Database import Database         # TO RUN THE CODE YOU MUST GO TO THE PREVIOUS FOLDER OF INFI AND RUN "python -m INFI.4-MES.Main"
#from ..Database import *

class SQLManager():
    def __init__(self, orderQueue):
        self.erpDB = Database("root", "admin", "erp")
        self.mesDB = Database("root", "admin", "mes")
        self.OrderQueue = orderQueue

    def __getOrder(self):
        while True:
            time.sleep(1)
            orderTup = self.erpDB.processMostUrgentOrder("erp")
            if(not orderTup):
                continue
            structOrder = Order(orderTup[0][1], orderTup[0][2], orderTup[0][3], orderTup[0][4], orderTup[0][5], orderTup[0][6])
            self.mesDB.insertOrder(orderTup[0][0], structOrder, "mes")
            order = {'clientID' : orderTup[0][0] , 'Order Number' : orderTup[0][1], 'WorkPiece' : orderTup[0][2], 'Quantity' : orderTup[0][3], 'DueDate' : orderTup[0][4], 'LatePen' : orderTup[0][5], 'EarlyPen' : orderTup[0][6]}
            self.OrderQueue.put(order)

    def getOrder(self):
        try:
            threading.Thread(target=self.__getOrder, daemon=True).start()
            print('[Manager] getOrder thread started')
        except:
            print('[Manager] getOrder thread failed')

class Manager():

    def __init__(self, orderQueue, requestQueue, doneRequestQueue, recipesFile, transformFile):
        self.OrderQueue = orderQueue
        self.RequestQueue = requestQueue
        self.DoneRequestQueue = doneRequestQueue
        self.piecesProcessed = []
        self.recipes = self.__csvReader__(recipesFile)
        self.transformations = self.__csvReader__(transformFile)
        self.cells = self.__initCells__() #hardcoded
        self.__configMachines__() #hardcoded

        self.piecesProcessed = []

        self.db = Database("root", "admin", "mes")

    def __initCells__(self,): #hardcoded
        cells = []
        for i in range(6):
            cells.append(Cell(i, self.RequestQueue, self.DoneRequestQueue, recipes=self.recipes, transformations=self.transformations))
        return cells
    

    def __configMachines__(self): #hardcoded
        print('[Manager] Configuring Machines')
        self.cells[0].addMachine(Machine(0, 'M1'))
        self.cells[0].addMachine(Machine(1, 'M2'))
        print('[Manager] cell 0 all tools: ', self.cells[0].getAllTools())
        #print('[Manager] Machines Configured')
        self.cells[1].addMachine(Machine(0, 'M1'))
        self.cells[1].addMachine(Machine(1, 'M2'))
        print('[Manager] cell 1 all tools: ', self.cells[1].getAllTools())
        #print('[Manager] Machines Configured')
        self.cells[2].addMachine(Machine(0, 'M1'))
        self.cells[2].addMachine(Machine(1, 'M2'))
        print('[Manager] cell 2 all tools: ', self.cells[2].getAllTools())
        self.cells[3].addMachine(Machine(0, 'M3'))
        self.cells[3].addMachine(Machine(1, 'M4'))
        print('[Manager] cell 3 all tools: ', self.cells[3].getAllTools())
        self.cells[4].addMachine(Machine(0, 'M3'))
        self.cells[4].addMachine(Machine(1, 'M4'))
        print('[Manager] cell 4 all tools: ', self.cells[4].getAllTools())
        self.cells[5].addMachine(Machine(0, 'M3'))
        self.cells[5].addMachine(Machine(1, 'M4'))
        print('[Manager] cell 5 all tools: ', self.cells[5].getAllTools())
        print('[Manager] Machines Configured')

    def __csvReader__(self, filename):
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            return [row for row in reader]
        
    def __postRequests__(self):
        while True:
            time.sleep(0.5)
            currOrder = self.OrderQueue.get()
            mesOrder = self.db.processMostUrgentOrder("mes")
            if(not mesOrder):
                continue
            self.db.updateWare(mesOrder[0][2], mesOrder[0][3], "mes", 2)

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
            
    def __wareHouse__(self):
        while True:
            time.sleep(2.73)
            if self.DoneRequestQueue.qsize() > 0:
                while self.DoneRequestQueue.qsize() > 0:
                    self.piecesProcessed.append(self.DoneRequestQueue.get())
                print('[Manager, __wareHouse] WareHouse: ', self.piecesProcessed)

    def postRequests(self):
        #tries to run thread
        try:
            threading.Thread(target=self.__postRequests__, daemon=True).start()
            print('[Manager] PostRequests thread started')
        except:
            print('[Manager] Could not start postRequests thread')

    def startWareHouse(self):
        try:
            threading.Thread(target=self.__wareHouse__, daemon=True).start()
            print('[Manager] StartWareHouse thread started')
        except:
            print('[Manager] Could not start StartWareHouse thread')

    def addProcessedPiece(self, piece):
        self.piecesProcessed.append(piece)
 
            



class Order:
    def __init__(self, number, workpiece, quantity, due_date, late_pen, early_pen):
        self.number = number
        self.workpiece = workpiece
        self.quantity = quantity
        self.due_date = due_date
        self.late_pen = late_pen
        self.early_pen = early_pen


order = {'clientID' : 'Client AA', 'Order Number' : 18, 'WorkPiece' : 'P6', 'Quantity' : 8, 'DueDate' : 7, 'LatePen' : 10, 'EarlyPen' : 5}
order1 = {'clientID' : 'Client AA', 'Order Number' : 19, 'WorkPiece' : 'P7', 'Quantity' : 12, 'DueDate' : 7, 'LatePen' : 10, 'EarlyPen' : 5}

orderQueue = customQueue.customQueue()
requestQueue = customQueue.customQueue()
doneRequestQueue = customQueue.customQueue()

SQLManager = SQLManager(orderQueue)
SQLManager.getOrder()
manager = Manager(orderQueue, requestQueue, doneRequestQueue, './Recipe/Recipes.csv', './Recipe/WorkPieceTransform.csv')
manager.postRequests()
manager.startWareHouse()

input()