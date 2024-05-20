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
    def __init__(self, orderQueue, requestQueue, doneRequestQueue, recipesFile):
        self.erpDB = Database("root", "admin", "erp")                           # Creates a connector to access the database
        self.mesDB = Database("root", "admin", "mes")
        self.OrderQueue = orderQueue
        self.RequestQueue = requestQueue
        self.DoneRequestQueue = doneRequestQueue

        self.recipes = self.__reader(recipesFile)

    def __getOrder(self):
        while True:
            time.sleep(1)
            orderTup = self.erpDB.processMostUrgentOrder("erp")
            if(not orderTup):
                continue
            structOrder = Order(orderTup[0][1], orderTup[0][2], orderTup[0][3], orderTup[0][4], orderTup[0][5], orderTup[0][6])
            self.erpDB.setOrderDone(orderTup[0][0], orderTup[0][1], "erp")
            self.mesDB.insertOrder(orderTup[0][0], structOrder, "mes")
            order = {'clientID' : orderTup[0][0] , 'Order Number' : orderTup[0][1], 'WorkPiece' : orderTup[0][2], 'Quantity' : orderTup[0][3], 'DueDate' : orderTup[0][4], 'LatePen' : orderTup[0][5], 'EarlyPen' : orderTup[0][6]}
            self.OrderQueue.put(order)
            print('[Manager, postOrder] Posting order: ',order)

            
    def __reader(self, filename):
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            return [row for row in reader]

    def getOrder(self):
        try:
            threading.Thread(target=self.__getOrder, daemon=True).start()
            print('[Manager] getOrder thread started')
        except:
            print('[Manager] getOrder thread failed')


    def getData(self):
        ordersTup = self.erpDB.getProcessingOrders("erp")
        if len(ordersTup) > 0:
            print('[Database] Exist orders in process at ERP database, orders added to MES orderQueue')
            for x in ordersTup:
                order = {'clientID' : x[0] , 'Order Number' : x[1], 'WorkPiece' : x[2], 'Quantity' : x[3], 'DueDate' : x[4], 'LatePen' : x[5], 'EarlyPen' : x[6]}
                self.OrderQueue.put(order)
                print(order)
        else:
            print('[Database] No orders to add to MES orderQueue')

        ordersTup = self.mesDB.getProcessingOrders("mes")
        if len(ordersTup) > 0:
            print('[Database] Exist orders in process at MES database, orders added to MES orderQueue')
            pieces = []
            quantities = []
            for order in ordersTup:
                piece = order[2]
                requiredNum = order[3]
                alreadyDone = self.mesDB.countPiece(piece, "mes_ware2")[0][0]
                if(piece not in pieces):        
                    pieces.append(piece)
                    quantities.append(requiredNum)
                else:
                    quantities[pieces.index(piece)] += requiredNum
                    
                for row in self.recipes:
                    if row['Piece'] == piece:
                        request = row
                        break
                print('[Database, postRequests] Posted   ', requiredNum, 'requests for', request['Piece'], "at RequestQueue")
                for count in range(requiredNum):
                    self.RequestQueue.put(request)
            if(len(pieces) > 0):
                for piece in pieces:
                    alreadyDone = self.mesDB.countPiece(piece, "mes_ware2")[0][0]
                    if(alreadyDone < quantities[pieces.index(piece)]):
                        for count in range(alreadyDone):
                            for iterator in range(self.RequestQueue.qsize()):
                                requestGotten = self.RequestQueue.get(iterator)
                                
                                if requestGotten['Piece'] != piece:
                                    self.RequestQueue.put(requestGotten)
                                else:
                                    break
                        print('[Database, postDoneRequest] Posted', alreadyDone, 'already done requests for', piece, "at doneRequestQueue")
                        print('[Database, postRequests] Removed  ', alreadyDone, 'requests for', piece, "from RequestQueue") 
                        print('[Database, postRequests] Remaining', self.RequestQueue.qsize(), 'requests for', piece, 'at RequestQueue', 'of total:', quantities[pieces.index(piece)] , piece)

            else:
                print('[Database] No orders to add to MES doneRequestQueue')
        else:
            print('[Database] No orders to add to MES RequestQueue')


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
            wareTup = self.db.countWare(2)
            if len(wareTup) > 0:
                for x in wareTup:
                    piece = x[0]
                    quantity = x[1]
                    for count in range(quantity):
                        self.piecesProcessed.append(piece)
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
            
            print('[Manager, postDoneOrders] Order found: ', DoneOrders[0])
            request_client = DoneOrders[0][0]
            request_number = DoneOrders[0][1]
            request_workpiece = DoneOrders[0][2]
            request_quantity = DoneOrders[0][3]
            database_quantity = self.db.countPiece(request_workpiece, "mes_ware2")
            manager_quantity = self.piecesProcessed.count(request_workpiece)
            delivery_count = 0
            if(database_quantity):
                database_quantity = int(database_quantity[0][0])
                print("                                 Manager:", manager_quantity, "pieces of", request_workpiece, "   Database:", database_quantity, "pieces of", request_workpiece, "   Request:", request_quantity)
            if manager_quantity == database_quantity:
                if self.piecesProcessed.count(request_workpiece) >= request_quantity:
                    while delivery_count < request_quantity:
                        for x in self.piecesProcessed:
                            if x == request_workpiece:
                                delivery_count += 1
                                self.piecesProcessed.remove(x)
                                self.db.updateWare(request_workpiece, -1, "mes", 2)
                                print(      "                                             Number of pieces delivered: ", delivery_count)
                                break
                    print('[Manager, postDoneOrders] Order done: ', DoneOrders[0])
                    self.db.setOrderDone(request_client, request_number, "mes")
                    self.db.__fetchWare__(2)
                    DoneOrders = None
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

SQLManager = SQLManager(orderQueue, requestQueue, doneRequestQueue, './Recipe/Recipes.csv')
SQLManager.getData()

SQLManager.getOrder()
manager = Manager(orderQueue, requestQueue, doneRequestQueue, './Recipe/Recipes.csv')
manager.postRequests()
manager.startWareHouse()
manager.postDoneOrders()

#orderQueue.put(order)
#orderQueue.put(order1)
input()
print("Order queue:", orderQueue.queue)
print("Request queue:", requestQueue.queue)
print("Done queue:", doneRequestQueue.queue)