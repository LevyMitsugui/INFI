from Plantfloor import *
#from Recipe.Recipe import *
from collections import OrderedDict
import csv
import threading
import time
import customQueue
import sys
from math import floor
import random
sys.path.append("..")
from Database import Database         # TO RUN THE CODE YOU MUST GO TO THE PREVIOUS FOLDER OF INFI AND RUN "python -m INFI.4-MES.Main"
from OPCUAClient import OPCUAClient

class SQLManager():
    def __init__(self, orderQueue, requestQueue, doneRequestQueue, recipesFile):
        # self.erpDB = Database("root", "admin", "erp")                           # Creates a connector to access the database
        # self.mesDB = Database("root", "admin", "mes")
        self.db = Database("root", "admin")
        self.OrderQueue = orderQueue
        self.RequestQueue = requestQueue
        self.DoneRequestQueue = doneRequestQueue

        self.recipes = self.__reader(recipesFile)

    def __getOrder(self):
        while True:
            time.sleep(0.5)
            orderTup = self.db.processMostUrgentOrder("erp")
            if(not orderTup):
                continue
            structOrder = Order(orderTup[0][1], orderTup[0][2], orderTup[0][3], orderTup[0][4], orderTup[0][5], orderTup[0][6])
            self.db.insertOrder(orderTup[0][0], structOrder, "mes")
            order = {'clientID' : orderTup[0][0] , 'Order Number' : orderTup[0][1], 'WorkPiece' : orderTup[0][2], 'Quantity' : orderTup[0][3], 'DueDate' : orderTup[0][4], 'LatePen' : orderTup[0][5], 'EarlyPen' : orderTup[0][6]}
            self.OrderQueue.put(order)
            print('[Manager, postOrder] Posting order: ',order)

            
    def __reader(self, filename):
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            return [row for row in reader]

    def getOrder(self):
        try:
            threading.Thread(target=self.__getOrder, daemon = True).start()
            print('[Manager] getOrder thread started')
        except:
            print('[Manager] getOrder thread failed')


    def getData(self):
        print('[Database] Initialing MES Queues')
        ordersTup = self.db.getMostUrgentOrder("erp")
        if(ordersTup is not None and len(ordersTup) > 0):
            for x in ordersTup:
                order = {'clientID' : x[0] , 'Order Number' : x[1], 'WorkPiece' : x[2], 'Quantity' : x[3], 'DueDate' : x[4], 'LatePen' : x[5], 'EarlyPen' : x[6]}
                self.OrderQueue.put(order)
            print('                 Posted', len(ordersTup), 'orders at RequestQueue')
        else:
            print('                 Posted 0 orders at RequestQueue')

        ordersTup = self.db.getOpenOrders("requests")
        if(ordersTup is not None and len(ordersTup) > 0):                                  #Calculate open requests and lost requests
            pieces_req = []
            quantities_req = []
            for order in ordersTup:
                piece = order[0]
                if(piece not in pieces_req):        
                    pieces_req.append(piece)
                    quantities_req.append(1)
                else:
                    quantities_req[pieces_req.index(piece)] += 1
                    
                for row in self.recipes:
                    if row['Piece'] == piece:
                        request = row
                        break
                self.RequestQueue.put(request)
            for c in pieces_req:
                print('                 Posted', quantities_req[pieces_req.index(c)], 'requests for', c, 'at RequestQueue')
            mesProcessingTup = self.db.countAllPieces("processing", "mes", done = True)
            mesRequestsTup = self.db.countAllPieces("", "requests")
            pieces_requests, quantities_requests = self.__countPieces(mesRequestsTup)
            pieces_processing, quantities_processing = self.__countPieces(mesProcessingTup)
            if(pieces_processing is not None and quantities_processing is not None and pieces_requests is not None and quantities_requests is not None):
                for piece in pieces_processing:
                    request = self.__getRequest(piece)
                    lost_requests = quantities_processing[pieces_processing.index(piece)] - quantities_requests[pieces_requests.index(piece)]
                    if(lost_requests > 0):
                        for i in range(lost_requests):
                            self.db.insertRequestOrder(request, "requests")
                            self.RequestQueue.put(request)
                        print('                 Posted', lost_requests, 'lost requests for', piece, 'at RequestQueue')

        else:
            print('                 Posted 0 lost requests at RequestQueue')

        ordersTup = self.db.getProcessingOrders("requests")
        if(ordersTup is not None and len(ordersTup) > 0):
            quantities = []
            pieces = []
            print('[Database] Exist requests in process at MES database, requests added to MES doneRequestQueue')
            for order in ordersTup:
                piece = order[0]
                if(piece not in pieces):        
                    pieces.append(piece)
                    quantities.append(1)
                else:
                    quantities[pieces.index(piece)] += 1
                self.DoneRequestQueue.put(piece)
            for c in pieces:
                print('                 Posted', quantities[pieces.index(c)], 'requests for', c, 'at doneRequestQueue')
        else:
            print('                 Posted 0 requests at doneRequestQueue')

        print('[Database] Initializing OPC-UA Queues')
        inTup = self.db.getWareQueue("in")
        if(inTup is not None):
            if len(inTup) > 0:
                for inReq in inTup:
                    inPiece = {'conveyor': inReq[0], 'piece': inReq[1]}
                    self.inWHQueue.put(inPiece)
                print('                 Posted', len(inTup), 'pieces at inWHQueue')
            else:
                print('                 Posted 0 pieces at inWHQueue')
        outTup = self.db.getWareQueue("out")
        if(outTup is not None and len(outTup) > 0):
            for inReq in outTup:
                inPiece = {'conveyor': inReq[0], 'piece': inReq[1]}
                self.outWHQueue.put(inPiece)
            print('                 Posted', len(outTup), 'pieces at outWHQueue')
        else:
            print('                 Posted 0 pieces at outWHQueue')

        machineTup = self.db.getMachineUpdQueue()
        if(machineTup is not None and len(machineTup) > 0):
            for machineReq in machineTup:
                machineUpdate = {'machine': machineReq[0], 'tool': machineReq[1], 'time': machineReq[2]}
                self.machineQueue.put(machineUpdate)
            print('                 Posted', len(machineTup), 'pieces at machineQueue')
        else:
            print('                 Posted 0 pieces at machineQueue')

        gateTup = self.db.getGateUpdQueue()
        if(gateTup is not None and len(gateTup) > 0):
            for gateReq in gateTup:
                gateUpdate = {'gate': gateReq[0], 'piece': gateReq[1], 'quantity': gateReq[2]}
                self.gateQueue.put(gateUpdate)
            print('                 Posted', len(gateTup), 'pieces at gateQueue')
        else:
            print('                 Posted 0 pieces at gateQueue')
        

    def __countPieces(self, taple, unitary = False):
        if(taple is not None):
            if len(taple) > 0:
                quantities = []
                pieces = []
                for order in taple:
                    piece = order[0]
                    if(unitary):
                        quantity = 1
                    else:
                        quantity = int(order[1])
                    if(piece not in pieces):        
                        pieces.append(piece)
                        quantities.append(quantity)
                    else:
                        quantities[pieces.index(piece)] += quantity
                return pieces, quantities
        return None, None

    def __getRequest(self, piece):
        for row in self.recipes:
            if row['Piece'] == piece:
                return row

class Manager():

    def __init__(self, orderQueue, requestQueue, doneRequestQueue, OPCUAClient,recipesFile, transformsFile):
        self.OrderQueue = orderQueue
        self.RequestQueue = requestQueue
        self.DoneRequestQueue = doneRequestQueue
        self.OPCUAClient = OPCUAClient

        self.shutdown = False

        self.recipes = self.__csvReader__(recipesFile)
        self.transforms = self.__csvReader__(transformsFile)
        self.cells = self.__initCells__() #hardcoded
        #self.__configMachines__() #hardcoded

        self.piecesProcessed = []

        self.db = Database("root", "admin")
        self.__initPiecesProcessed()
        self.gates = Gates(gateUpdateQueue, OPCUAClient)
        self.warehouses = []

    def __initCells__(self,): #hardcoded
        cells = []
        for i in range(6):
            time.sleep(0.1 + 0.017*i)
            cells.append(Cell(i+1, self.RequestQueue, self.DoneRequestQueue, recipes=self.recipes, transformations=self.transforms))
        return cells
    

    def configMachines(self, machineUpdateQueue): #hardcoded
        print('[Manager] Configuring Machines')
        success = []

        success.append(self.cells[0].addMachine(Machine(0, 'M1', self.OPCUAClient, machineUpdateQueue)))
        success.append(self.cells[0].addMachine(Machine(1, 'M2', self.OPCUAClient, machineUpdateQueue)))
        print('[Manager] cell 0 all tools: ', self.cells[0].getAllTools())
        #print('[Manager] Machines Configured')
        success.append(self.cells[1].addMachine(Machine(0, 'M1', self.OPCUAClient, machineUpdateQueue)))
        success.append(self.cells[1].addMachine(Machine(1, 'M2', self.OPCUAClient, machineUpdateQueue)))
        print('[Manager] cell 1 all tools: ', self.cells[1].getAllTools())
        #print('[Manager] Machines Configured')
        success.append(self.cells[2].addMachine(Machine(0, 'M1', self.OPCUAClient, machineUpdateQueue)))
        success.append(self.cells[2].addMachine(Machine(1, 'M2', self.OPCUAClient, machineUpdateQueue)))
        print('[Manager] cell 2 all tools: ', self.cells[2].getAllTools())
        success.append(self.cells[3].addMachine(Machine(0, 'M3', self.OPCUAClient, machineUpdateQueue)))
        success.append(self.cells[3].addMachine(Machine(1, 'M4', self.OPCUAClient, machineUpdateQueue)))
        print('[Manager] cell 3 all tools: ', self.cells[3].getAllTools())
        success.append(self.cells[4].addMachine(Machine(0, 'M3', self.OPCUAClient, machineUpdateQueue)))
        success.append(self.cells[4].addMachine(Machine(1, 'M4', self.OPCUAClient, machineUpdateQueue)))
        print('[Manager] cell 4 all tools: ', self.cells[4].getAllTools())
        success.append(self.cells[5].addMachine(Machine(0, 'M3', self.OPCUAClient, machineUpdateQueue)))
        success.append(self.cells[5].addMachine(Machine(1, 'M4', self.OPCUAClient, machineUpdateQueue)))
        print('[Manager] cell 5 all tools: ', self.cells[5].getAllTools())
        
        if all(success):
            print('[Manager] Machines Configured')
            return True
        else:
            print('[Manager] Machines not Configured')
            return False

    def configWareHouse(self, inwhQueue, outwhQueue):
        success = []
        Warehouse0 = Warehouse(0, self.OPCUAClient, inwhQueue, outwhQueue)
        self.warehouses.append(Warehouse0)
        Warehouse1 = Warehouse(1, self.OPCUAClient, inwhQueue, outwhQueue)
        self.warehouses.append(Warehouse1)
        for cell in self.cells:
            success.append(cell.addWarehouse(Warehouse0))#, self.db)))
            success.append(cell.addWarehouse(Warehouse1))#, self.db)))
        if all(success):
            print('[Manager] Warehouse Configured')
            return True
        else:
            print('[Manager] Warehouse not Configured')
            return False
        
        
    def __csvReader__(self, filename):
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            return [row for row in reader]
        
    def __postRequests__(self):
        while True:
            time.sleep(0.2)
            currOrder = self.OrderQueue.get()
            # self.db.setOrderDone(currOrder['clientID'], currOrder['Order Number'], "erp")

            if currOrder['WorkPiece'] == 'P1' or currOrder['WorkPiece'] == 'P2':
                print('[Manager, postRequests] P1 & P2 are not processable, order will not be posted and will be removed from queue')
                continue

            mesOrder = self.db.processOrderByNum(currOrder['clientID'] , currOrder['Order Number'] , "mes")
            if mesOrder is None:    # Order not found at database open orders
                print('[Manager, postRequests] Order not found at MES database, it will not be posted and will be removed from queue')
                continue

            request = {'Piece':currOrder['WorkPiece']}
            if currOrder['WorkPiece'] == 'P9':
                request['Steps'] = [{'Machine': 1, 'Tool':1, 'Time': 45}, {'Machine': 0, 'Tool':5, 'Time': 45}]
            quantity = int(currOrder['Quantity'])
            print('[Manager, postRequests] Posting', quantity, 'requests for: ',request['Piece'])
            

            for counter in range(quantity):
                if currOrder['WorkPiece'] == 'P9':
                    timeN = time.process_time()
                    request['ID'] = random.randint(1,9999)
                self.RequestQueue.put(request)
                self.db.insertRequestOrder(request, "requests")
        
            print('[Manager, postRequests] Posted ', quantity, ' requests for ', currOrder['WorkPiece'])
            
    def __wareHouse__(self):
        while True:
            time.sleep(0.2)
            if self.DoneRequestQueue.qsize() > 0:
                doneRequest = self.DoneRequestQueue.get()
                self.piecesProcessed.append(doneRequest)
                self.db.updateWare(doneRequest, 1, "mes", 2)
                self.db.setRequestDone(doneRequest, "requests")
                print('[Manager, __wareHouse] WareHouse: ', self.piecesProcessed)
                self.db.__fetchWare__(2)

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

    def __initPiecesProcessed(self):            # On starting the code, get data of piecesProcessed with all pieces from warehouse2 at database
        wareTup = self.db.countWare(2, "mes")
        if len(wareTup) > 0:
            for x in wareTup:
                piece = x[0]
                quantity = x[1]
                for count in range(quantity):
                    self.piecesProcessed.append(piece)

    def postDoneOrders(self):
        try:
            threading.Thread(target=self.__postDoneOrders, daemon=True).start()
            print('[Manager] PostDoneOrders thread started')
        except:
            print('[Manager] Could not start PostDoneOrders thread')

    def __postDoneOrders(self):
        lastOutput = 7
        while True:
            time.sleep(0.2)
            DoneOrders = self.db.getMostUrgentOrder("mes")
            if DoneOrders is None:
                continue
            
            request_delivered = DoneOrders[0][0]
            request_client = DoneOrders[0][1]
            request_number = DoneOrders[0][2]
            request_workpiece = DoneOrders[0][3]
            request_quantity = DoneOrders[0][4]
            if request_delivered == 0:
                print('[Manager, postDoneOrders] Order found: ', DoneOrders[0])
            manager_quantity = self.piecesProcessed.count(request_workpiece)
            database_quantity = self.db.countWare(2, "mes", request_workpiece)
            if(database_quantity):
                database_quantity = int(database_quantity[0][1])
            else:
                database_quantity = 0
            if manager_quantity == database_quantity:
                if request_delivered < request_quantity and manager_quantity > 0:
                    self.piecesProcessed.remove(request_workpiece)
                    if self.db.updateWare(request_workpiece, -1, "mes", 2):
                        self.warehouses[1].outputPiece(request_workpiece, lastOutput)
                        if lastOutput == 10:
                            lastOutput = 7
                        else:
                            lastOutput += 1
                        self.db.updateDeliveredPieces(request_client, request_number, 1, "mes")
                        self.db.__fetchWare__(2)
                    else:
                        print('                                             [Manager, postDoneOrders] Could not update warehouse')
                        DoneOrders = None
                        continue
                elif request_delivered == request_quantity:
                    self.db.setOrderDone(request_client, request_number, "mes")
                    self.db.setOrderDone(request_client, request_number, "erp")
                    self.db.__fetchWare__(2)
                    print('[Manager, postDoneOrders] Order done: ', DoneOrders[0])
            else:
                print("[Manager, postDoneOrders] !!Disparity between number of pieces", request_workpiece, "in database and Manager!! database:", database_quantity, "Manager:", manager_quantity)
            DoneOrders = None

    def __printRequestQueue__(self):
        while True:
            count = {}
            time.sleep(4)
            print(len(requestQueue.queue), "requests pendent in requestQueue")
            for x in requestQueue.queue:
                if x['Piece'] in count:
                    count[x['Piece']] += 1
                else:
                    count[x['Piece']] = 1
            print(OrderedDict(sorted(count.items())))
    
    def printRequestQueue(self):
        try:
            threading.Thread(target=self.__printRequestQueue__, daemon=True).start()
            print('[Manager] PrintRequestQueue thread started')
        except:
            print('[Manager] Could not start PrintRequestQueue thread')


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

inWHQueue = customQueue.customQueue()
outWHQueue = customQueue.customQueue()
machineUpdateQueue = customQueue.customQueue()
gateUpdateQueue = customQueue.customQueue()


inWHQueue = customQueue.customQueue()
outWHQueue = customQueue.customQueue()
machineUpdateQueue = customQueue.customQueue()
gateUpdateQueue = customQueue.customQueue()


SQLManager = SQLManager(orderQueue, requestQueue, doneRequestQueue, './Recipe/Recipes.csv')
SQLManager.getData()

SQLManager.getOrder()

OPCUAClient = OPCUAClient(inWHQueue, outWHQueue, machineUpdateQueue, gateUpdateQueue)
OPCUAClient.opcManager()

manager = Manager(orderQueue, requestQueue, doneRequestQueue, OPCUAClient, './Recipe/Recipes.csv', './Recipe/WorkPieceTransform.csv')
manager.configMachines(machineUpdateQueue)
print ('hello')
manager.configWareHouse(inWHQueue, outWHQueue)

print('hello hello')
manager.gates.spawnPieces('P2', 8)

manager.postRequests()
manager.startWareHouse()
manager.postDoneOrders()
manager.printRequestQueue()

input()
count = {}
print(len(orderQueue.queue), "orders pendent in orderQueue")
for x in orderQueue.queue:
    if x['clientID'] in count:
        count[x['clientID']] += 1
    else:
        count[x['clientID']] = 1
print(OrderedDict(sorted(count.items())))

count = {}
print(len(requestQueue.queue), "requests pendent in requestQueue")
for x in requestQueue.queue:
    if x['Piece'] in count:
        count[x['Piece']] += 1
    else:
        count[x['Piece']] = 1
print(OrderedDict(sorted(count.items())))

count = {}
print(len(doneRequestQueue.queue), "requests pendent in doneRequestQueue")
for x in doneRequestQueue.queue:
    if x in count:
        count[x] += 1
    else:
        count[x] = 1
print(OrderedDict(sorted(count.items())))
OPCUAClient.kill()