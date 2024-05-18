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
        self.erpDB = Database("root", "admin", "erp")                           # Creates a connector to access the database
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

    # def getData(self, orderQueue, requestQueue, doneRequestQueue):
    #     ordersTup = self.erpDB.getOpenOrders("mes")
    #     if len(ordersTup) > 0:
    #         print('[Database] Exist open orders at ERP database, orders added to MES orderQueue')
    #         for x in ordersTup:
    #             order = {'clientID' : x[0] , 'Order Number' : x[1], 'WorkPiece' : x[2], 'Quantity' : x[3], 'DueDate' : x[4], 'LatePen' : x[5], 'EarlyPen' : x[6]}
    #             orderQueue.put(order)
    #             print(order)
    #     else:
    #         print('[Database] No orders to add to MES orderQueue')

    #     ordersTup = self.mesDB.getOpenOrders("mes")
    #     if len(ordersTup) > 0:
    #         print('[Database] Exist processing orders at MES database, orders added to MES requestQueue')
    #         for x in ordersTup:
    #             order = {'clientID' : x[0] , 'Order Number' : x[1], 'WorkPiece' : x[2], 'Quantity' : x[3], 'DueDate' : x[4], 'LatePen' : x[5], 'EarlyPen' : x[6]}
    #             requestQueue.put(order)
    #             print(order)
    #     else:
    #         print('[Database] No orders to add to MES requestQueue')

    #     ordersTup = self.mesDB.getOrdersDone("mes")
    #     if len(ordersTup) > 0:
    #         print('[Database] Exist orders done at MES database, orders added to MES doneRequestQueue')
    #         for x in ordersTup:
    #             order = {'clientID' : x[0] , 'Order Number' : x[1], 'WorkPiece' : x[2], 'Quantity' : x[3], 'DueDate' : x[4], 'LatePen' : x[5], 'EarlyPen' : x[6]}
    #             doneRequestQueue.put(order)
    #             print(order)
    #     else:
    #         print('[Database] No orders to add to MES doneRequestQueue')


class Manager():

    def __init__(self, orderQueue, requestQueue, doneRequestQueue, recipesFile):
        self.OrderQueue = orderQueue
        self.RequestQueue = requestQueue
        self.DoneRequestQueue = doneRequestQueue
        self.piecesProcessed = []
        self.recipes = self.__reader(recipesFile)
        self.cells = self.__initCells() #hardcoded
        self.__configMachines() #hardcoded

        self.piecesProcessed = []

        self.recipes = self.__reader(recipesFile) #recipes is a reader

        self.db = Database("root", "admin", "mes")

    def __initCells(self,): #hardcoded
        cells = []
        for i in range(6):
            cells.append(Cell(i, self.RequestQueue, self.DoneRequestQueue, recipes=self.recipes))
        return cells
    

    def __configMachines(self): #hardcoded
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

            # mesOrder = self.db.processMostUrgentOrder("mes")
            mesOrder = self.db.processOrderByNum(currOrder['clientID'] , currOrder['Order Number'] , "mes")
            if mesOrder is None:    # Order not found at database open orders
                print('[Manager, postRequests] Order not found at MES database, it will not be posted and will be removed from queue')
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
            time.sleep(2.73)
            if self.DoneRequestQueue.qsize() > 0:
                while self.DoneRequestQueue.qsize() > 0:
                    doneRequest = self.DoneRequestQueue.get()
                    self.piecesProcessed.append(doneRequest)
                    self.db.updateWare(doneRequest, 1, "mes", 2)
                print('[Manager, __wareHouse] WareHouse: ', self.piecesProcessed)
                self.db.__fetchWare__(2)

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



    def postDoneOrders(self):
        try:
            threading.Thread(target=self.__postDoneOrders, daemon=True).start()
            print('[Manager] PostDoneOrders thread started')
        except:
            print('[Manager] Could not start PostDoneOrders thread')

    def __postDoneOrders(self):
        while True:
            time.sleep(0.41)
            DoneOrders = self.db.getMostUrgentOrder("mes")
            if DoneOrders is None:
                continue
            
            request_client = DoneOrders[0][0]
            request_number = DoneOrders[0][1]
            request_workpiece = DoneOrders[0][2]
            request_quantity = DoneOrders[0][3]
            if self.piecesProcessed.count(request_workpiece) == self.db.countPieces(request_workpiece, 2):
                if self.piecesProcessed.count(request_workpiece) >= request_quantity:
                    for x in self.piecesProcessed:
                        if x == request_workpiece:
                            self.piecesProcessed.remove(x)
                            self.db.updateWare(request_workpiece, -1, "mes", 2)
                    self.db.setOrderDone(request_client, request_number, "mes")
                    self.db.__fetchWare__(2)
                    print('[Manager, postDoneOrders] Order done: ', DoneOrders[0])
                else:
                    continue



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
# SQLManager.getData(orderQueue, requestQueue, doneRequestQueue)

SQLManager.getOrder()
manager = Manager(orderQueue, requestQueue, doneRequestQueue, './Recipe/Recipes.csv')
manager.postRequests()
manager.startWareHouse()
manager.postDoneOrders()

#orderQueue.put(order)
#orderQueue.put(order1)
input()