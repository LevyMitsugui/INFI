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
import datetime
from datetime import timedelta

class SQLManager():
    def __init__(self, orderQueue, requestQueue, doneRequestQueue, inWHQueue, outWHQueue, machineUpdateQueue, gateUpdateQueue, recipesFile, database):
        # self.db = Database("root", "admin")
        self.db = database
        self.OrderQueue = orderQueue
        self.RequestQueue = requestQueue
        self.DoneRequestQueue = doneRequestQueue

        self.inWHQueue = inWHQueue
        self.outWHQueue = outWHQueue
        self.machineUpdateQueue = machineUpdateQueue
        self.gateUpdateQueue = gateUpdateQueue

        self.initialDate = datetime.datetime.now().strftime("%H:%M:%S")

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
                i = 3
                order = {'clientID' : x[i] , 'Order Number' : x[i+1], 'WorkPiece' : x[i+2], 'Quantity' : x[i+3], 'DueDate' : x[i+4], 'LatePen' : x[i+5], 'EarlyPen' : x[i+6]}
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
                self.machineUpdateQueue.put(machineUpdate)
            print('                 Posted', len(machineTup), 'pieces at machineQueue')
        else:
            print('                 Posted 0 pieces at machineQueue')

        gateTup = self.db.getGateUpdQueue()
        if(gateTup is not None and len(gateTup) > 0):
            for gateReq in gateTup:
                gateUpdate = {'gate': gateReq[0], 'piece': gateReq[1], 'quantity': gateReq[2]}
                self.gateUpdateQueue.put(gateUpdate)
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

    def __init__(self, orderQueue, requestQueue, doneRequestQueue, database, OPCUAClient,recipesFile, transformsFile, thread_lock):
        self.OrderQueue = orderQueue
        self.RequestQueue = requestQueue
        self.DoneRequestQueue = doneRequestQueue
        self.OPCUAClient = OPCUAClient

        self.shutdown = False

        self.recipes = self.__csvReader__(recipesFile)
        self.transforms = self.__csvReader__(transformsFile)
        self.cells = self.__initCells__(thread_lock)

        self.piecesProcessed = []

        # self.db = Database("root", "admin")
        self.db = database
        self.__initPiecesProcessed()
        self.gates = Gates(gateUpdateQueue, OPCUAClient, database)
        self.warehouses = []

        self.beginningTime = time.time()


    def __initCells__(self, thread_lock):
        cells = []
        for i in range(6):
            time.sleep(0.1 + 0.017*i)
            cells.append(Cell(i+1, thread_lock, self.RequestQueue, self.DoneRequestQueue, recipes=self.recipes, transformations=self.transforms))
        return cells
    

    def configMachines(self, machineUpdateQueue): #hardcoded
        print('[Manager] Configuring Machines')
        success = []

        success.append(self.cells[0].addMachine(Machine(0, 'M1', self.OPCUAClient, machineUpdateQueue, self.db)))
        success.append(self.cells[0].addMachine(Machine(1, 'M2', self.OPCUAClient, machineUpdateQueue, self.db)))
        print('[Manager] cell 0 all tools: ', self.cells[0].getAllTools())
        #print('[Manager] Machines Configured')
        success.append(self.cells[1].addMachine(Machine(0, 'M1', self.OPCUAClient, machineUpdateQueue, self.db)))
        success.append(self.cells[1].addMachine(Machine(1, 'M2', self.OPCUAClient, machineUpdateQueue, self.db)))
        print('[Manager] cell 1 all tools: ', self.cells[1].getAllTools())
        #print('[Manager] Machines Configured')
        success.append(self.cells[2].addMachine(Machine(0, 'M1', self.OPCUAClient, machineUpdateQueue, self.db)))
        success.append(self.cells[2].addMachine(Machine(1, 'M2', self.OPCUAClient, machineUpdateQueue, self.db)))
        print('[Manager] cell 2 all tools: ', self.cells[2].getAllTools())
        success.append(self.cells[3].addMachine(Machine(0, 'M3', self.OPCUAClient, machineUpdateQueue, self.db)))
        success.append(self.cells[3].addMachine(Machine(1, 'M4', self.OPCUAClient, machineUpdateQueue, self.db)))
        print('[Manager] cell 3 all tools: ', self.cells[3].getAllTools())
        success.append(self.cells[4].addMachine(Machine(0, 'M3', self.OPCUAClient, machineUpdateQueue, self.db)))
        success.append(self.cells[4].addMachine(Machine(1, 'M4', self.OPCUAClient, machineUpdateQueue, self.db)))
        print('[Manager] cell 4 all tools: ', self.cells[4].getAllTools())
        success.append(self.cells[5].addMachine(Machine(0, 'M3', self.OPCUAClient, machineUpdateQueue, self.db)))
        success.append(self.cells[5].addMachine(Machine(1, 'M4', self.OPCUAClient, machineUpdateQueue, self.db)))
        print('[Manager] cell 5 all tools: ', self.cells[5].getAllTools())
        
        if all(success):
            print('[Manager] Machines Configured')
            return True
        else:
            print('[Manager] Machines not Configured')
            return False

    def configWareHouse(self, inwhQueue, outwhQueue):
        success = []
        Warehouse0 = Warehouse(0, self.OPCUAClient, inwhQueue, outwhQueue, self.db)
        self.warehouses.append(Warehouse0)
        Warehouse1 = Warehouse(1, self.OPCUAClient, inwhQueue, outwhQueue, self.db)
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
                    print('bruh')
                self.RequestQueue.put(request)
                self.db.insertRequestOrder(request, "requests")
        
            print('[Manager, postRequests] Posted ', quantity, ' requests for ', currOrder['WorkPiece'])
            
    def __wareHouse__(self):
        while True:
            time.sleep(0.2)
            if self.DoneRequestQueue.qsize() > 0:
                doneRequest = self.DoneRequestQueue.get()
                self.piecesProcessed.append(doneRequest)
                self.db.setRequestReady(doneRequest, "requests")

                self.db.updateColumn("orders", "end", "CURRENT_TIME()", "requests", None, "start = (SELECT MIN(start) FROM requests_orders WHERE workpiece = '{}' AND end IS NULL)".format(doneRequest))
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

    def startRestockWareHouse(self):
        try:
            threading.Thread(target=self.__restockWareHouse__, daemon=True).start()
            print('[Manager] StartRestockWareHouse thread started')
        except:
            print('[Manager] Could not start StartRestockWareHouse thread')

    def __restockWareHouse__(self):
        time4min = 240
        time2min = 120
        time1min = 10 #ARRUMAR!!!!!!!!!!!!!!
        time30sec = 30
        waitTime = time30sec

        restockThreshold = 40
        setOrderP1 = False
        startTimeP1 = 0
        setOrderP2 = False
        startTimeP2 = 0
        priceP1 = 0
        priceP2 = 0

        missing1 = 0
        missing2 = 0

        firstRun = 2

        print('time to restock supplier C: ', time1min, 'min')
        print('time to restock supplier A: ', time4min, 'min')
        while True:
            time.sleep(2)
            print('WHAREHOUSE 0', self.warehouses[0].getStock())
            print('WHAREHOUSE 1', self.warehouses[1].getStock())
            p1count = self.warehouses[0].getStock()[0]
            p2count = self.warehouses[0].getStock()[1]

            if firstRun != 0:
                print('Running first run')
                if gateUpdateQueue.qsize() == 0 and p2count < restockThreshold and setOrderP2 == False and firstRun == 2:
                    print('Order P2?')
                    missing2 = restockThreshold - p2count
                    if missing2 > 16:
                        print('[Manager] Ordering P2 from supplier C')
                        setOrderP2 = True
                        startTimeP2 = time.time() + self.__solveRestockColision__(setOrderP1, startTimeP1, missing1+16, time1min)
                    firstRun = 1
                    
                        
                elif gateUpdateQueue.qsize() == 0 and p1count < restockThreshold and setOrderP1 == False and firstRun == 1:
                    print('Order P1?')
                    missing1 = restockThreshold - p1count
                    if missing1 > 16:
                        print('[Manager] Ordering P1 from supplier C')
                        setOrderP1 = True
                        startTimeP1 = time.time() + self.__solveRestockColision__(setOrderP2, startTimeP2, missing2+16, time1min)
                    

                if setOrderP2:
                    print('Time since order P2: ', time.time() - startTimeP2)
                if setOrderP1:
                    print('Time since order P1: ', time.time() - startTimeP1)

                if setOrderP2 and time.time() - startTimeP2 > time1min:
                    priceP2 = 18 #Price by piece
                    self.gates.spawnPieces('P2', missing2 + 16)       #SPAWN de Facto
                    # for i in range(missing2+16):
                    #     self.db.insertInTable("supplier", "workpiece, arrival, raw_cost", "{}, {}, {}".format("P2", "CURRENT_TIME()", priceP2))
                    
                    self.warehouses[0].setStock('P2', p2count + missing2 + 16)
                    time.sleep(1.03*(missing2+16))
                    setOrderP2 = False
                    
                
                elif setOrderP1 and time.time() - startTimeP1 > time1min:
                    priceP1 = 55 #Price by piece
                    # for i in range(missing1+16):
                    #     self.db.insertInTable("supplier", "workpiece, arrival, raw_cost", "{}, {}, {}".format("P1", "CURRENT_TIME()", priceP1))
                    
                    self.gates.spawnPieces('P1', missing1 + 16)       #SPAWN de Facto
                    self.warehouses[0].setStock('P1', p1count + missing1 + 16)
                    time.sleep(1.03*(missing1+16))
                    setOrderP1 = False
                    firstRun = 0

            elif firstRun == 0:
                print('Running second run')
                if gateUpdateQueue.qsize() == 0 and p2count < restockThreshold and setOrderP2 == False:
                    missing2 = restockThreshold - p2count
                    if missing2 > 16:
                        print('[Manager] Ordering P2 from supplier A')
                        setOrderP2 = True
                        startTimeP2 = time.time() + self.__solveRestockColision__(setOrderP1, startTimeP1, missing1+16, waitTime)
                        
                elif gateUpdateQueue.qsize() == 0 and p1count < restockThreshold and setOrderP1 == False:
                    missing1 = restockThreshold - p1count
                    if missing1 > 16:
                        print('[Manager] Ordering P1 from supplier A')
                        setOrderP1 = True
                        startTimeP1 = time.time() + self.__solveRestockColision__(setOrderP2, startTimeP2, missing2+16, waitTime)

                if setOrderP2:
                    print('Time since order P2: ', time.time() - startTimeP2)
                if setOrderP1:
                    print('Time since order P1: ', time.time() - startTimeP1)

                if setOrderP2 and time.time() - startTimeP2 > waitTime:
                    if waitTime == time4min:
                        priceP2 = 10 #Price by piece
                    
                    # for i in range(missing2+16):
                    #     self.db.insertInTable("supplier", "workpiece, arrival, raw_cost", "{}, {}, {}".format("P2", "CURRENT_TIME()", priceP2))
                    self.gates.spawnPieces('P2', missing2 + 16)       #SPAWN de Facto
                    self.warehouses[0].setStock('P2', p2count + missing2 + 16)
                    time.sleep(1.03*(missing2+16))
                    setOrderP2 = False
                
                elif setOrderP1 and time.time() - startTimeP1 > waitTime:
                    if waitTime == time4min:
                        priceP1 = 30 #Price by piece
                    
                    # for i in range(missing1+16):
                    #     self.db.insertInTable("supplier", "workpiece, arrival, raw_cost", "{}, {}, {}".format("P1", "CURRENT_TIME()", priceP1))
                    self.gates.spawnPieces('P1', missing1 + 16)       #SPAWN de Facto
                    self.warehouses[0].setStock('P1', p1count + missing1 + 16)
                    time.sleep(1.03*(missing1+16))
                    setOrderP1 = False

    def __solveRestockColision__(self, setOther, startTimeOther, missingOther, waitTime):
        now = time.time()
        dif =startTimeOther + waitTime + missingOther*1.03 - (now+ waitTime+(now-startTimeOther))
        if dif > 0 and setOther == True:
            return dif
        else:
            return 0

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

    def postOrdersReady(self):
        try:
            threading.Thread(target=self.__postOrdersReady, daemon=True).start()
            print('[Manager] PostDoneOrders thread started')
        except:
            print('[Manager] Could not start PostDoneOrders thread')

    def __postOrdersReady(self):
        lastOutput = 7
        while True:
            time.sleep(0.2)
            ordersReady = self.db.getMostUrgentOrder("mes")
            if ordersReady is None:
                continue
            
            i = 2
            request_delivered   = ordersReady[0][i]
            request_start       = ordersReady[0][i+1]     #We can try to use this variable to calculate the production cost
            request_end         = ordersReady[0][i+2]     #It should be the time since production of this order started until enough pieces in stock to delivery
            request_client      = ordersReady[0][i+3]
            request_number      = ordersReady[0][i+4]
            request_workpiece   = ordersReady[0][i+5]
            request_quantity    = ordersReady[0][i+6]
            request_duedate     = ordersReady[0][i+7]
            orderToDeliver = self.db.getOrderByNum(request_client, request_number, "erp")
            delivery_admission  = orderToDeliver[0][i]


            stock_quantity = self.piecesProcessed.count(request_workpiece)
            database_quantity = self.db.countWare(2, "mes", request_workpiece)
            database_quantity = int(database_quantity[0][1]) if database_quantity else 0
            if stock_quantity == database_quantity and stock_quantity >= (request_quantity - request_delivered):
                scheduled_delivery, delivery_limit = self.__scheduleDelivery__(delivery_admission, request_duedate, request_quantity)
                print("scheduled_delivery: ", scheduled_delivery) #TODO SET THE ADMISSION TIME HERE IN ORDER TO BE ABLE TO SCHEDULE DELIVERY
                print("delivery_limit: ", delivery_limit)
                print('[Manager, postDoneOrders] Order found: ', ordersReady[0])
                self.db.setOrderDone(request_client, request_number, "mes")
            else:
                print("[Manager, postDoneOrders] !!Disparity between number of pieces", request_workpiece, "in database and Manager!! database:", database_quantity, "Manager:", stock_quantity)
            ordersReady = None

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
            ordersReady = self.db.getMostUrgentOrder("erp")
            if ordersReady is None:
                continue
            for order in ordersReady:
                i = 2
                delivery_id          = order[i-2]
                delivery_admission   = order[i]
                delivery_client      = order[i+2]
                delivery_number      = order[i+3]
                delivery_workpiece   = order[i+4]
                delivery_quantity    = order[i+5]
                delivery_duedate     = order[i+6]
                orderToDeliver       = self.db.getOrderByNum(delivery_client, delivery_number, "mes")
                pieces_delivered     = orderToDeliver[0][i]


                stock_quantity = self.piecesProcessed.count(delivery_workpiece)
                database_quantity = self.db.countWare(2, "mes", delivery_workpiece)
                database_quantity = int(database_quantity[0][1]) if database_quantity else 0
                if stock_quantity == database_quantity:

                    scheduled_delivery, delivery_limit = self.__scheduleDelivery__(delivery_admission, delivery_duedate, delivery_quantity)

                    if self.__isPast__(scheduled_delivery):
                        if pieces_delivered < delivery_quantity and stock_quantity > 0:
                            self.piecesProcessed.remove(delivery_workpiece)
                                
                            self.warehouses[1].outputPiece(delivery_workpiece, lastOutput)
                            if lastOutput == 10:
                                lastOutput = 7
                            else:
                                lastOutput += 1
                            self.db.updateDeliveredPieces(delivery_client, delivery_number, 1, "mes")

                            requests = self.db.getWaitingRequests(delivery_workpiece)

                            request_id      = requests[0][0]
                            request_arrival = requests[0][3]
                            request_start   = requests[0][4]
                            request_end     = requests[0][5]
                            request_dispatch= requests[0][6]
                            request_raw_cost= requests[0][7]
                            # if(self.__timeDiff__(delivery_admission, request_arrival) > 0):
                            #     delivery_admission = self.db.updateColumn("orders", "start", request_arrival, "mes", delivery_id)
                            request_dispatch = self.db.updateColumn("orders", "dispatch", "CURRENT_TIME()", "requests", request_id)
                            if(request_raw_cost != None):
                                print("!![Manager, postDoneOrders] Raw cost unavailable!!")
                                request_depreciation_cost = request_raw_cost*self.__timeDiff__(request_arrival, request_dispatch)*0.01
                            else:
                                request_depreciation_cost = self.__timeDiff__(request_arrival, request_dispatch)*0.01
                            request_production_cost = self.__timeDiff__(request_start, request_end)
                            request_cost = request_depreciation_cost+request_production_cost+request_raw_cost
                            print("[Manager, postDoneOrders] Piece cost {}€ -> Rc = {}€ | Dc = {}€ | Pc = {}€").__format__(request_cost, request_depreciation_cost, request_production_cost)
                            self.db.__fetchWare__(2)
                            
                            break
                        elif pieces_delivered == delivery_quantity:
                            diff = self.db.setOrderDone(delivery_client, delivery_number, "erp")
                            self.db.__fetchWare__(2)
                            delay = diff - delivery_duedate*60
                            str = 'late' if delay > 0 else 'early'
                            print('[Manager, postDoneOrders] Order done:', order, 'in', diff, 'seconds, expected in', float(delivery_duedate*60), 'seconds =>', delay, 'seconds', str)
                            break
                            
                else:
                    print("[Manager, postDoneOrders] !!Disparity between number of pieces", delivery_workpiece, "in database and Manager!! database:", database_quantity, "Manager:", stock_quantity)
                order = None

    def __printRequestQueue__(self):        
        while True:
            time.sleep(5) 
            print('[Manager]: ', self.RequestQueue.qsize(), "requests pendent in requestQueue")
    
    def printRequestQueue(self):
        try:
            threading.Thread(target=self.__printRequestQueue__, daemon=True).start()
            print('[Manager] PrintRequestQueue thread started')
        except:
            print('[Manager] Could not start PrintRequestQueue thread')
    
    def __timeSum__(self, timeStr1, timeStr2):
        time1 = datetime.datetime.strptime(timeStr1, '%H:%M:%S')
        time2 = datetime.datetime.strptime(timeStr2, '%H:%M:%S')
        result = datetime.datetime.strptime(time1, '%H:%M:%S') + datetime.datetime.strptime(time2, '%H:%M:%S')
        return result
    
    def __timeDiff__(self, timeStr1, timeStr2):
        if(timeStr1 == None):
            return 1
        time1 = datetime.datetime.strptime(timeStr1, '%H:%M:%S')
        time2 = datetime.datetime.strptime(timeStr2, '%H:%M:%S')
        result = datetime.datetime.strptime(time1, '%H:%M:%S') - datetime.datetime.strptime(time2, '%H:%M:%S')
        return result
    
    def __scheduleDelivery__(self, request_admission, request_duedate, request_quantity):
        dueTime = timedelta(minutes = request_duedate)          #timedelta
        delivery_limit = request_admission + dueTime            #datetime
        # datetime.datetime.strftime(delivery_limit, '%H:%M:%S')

        deliver_duration = timedelta(seconds = 2*request_quantity)   #in seconds
        scheduled_delivery = delivery_limit - deliver_duration
        # datetime.datetime.strftime(scheduled_delivery, '%H:%M:%S')
        
        return scheduled_delivery, delivery_limit
    
    def __isPast__(self, time):
        timeNow = datetime.datetime.now().strftime("%H:%M:%S")
        # timeDiff = timeNow - time
        timeDiff = datetime.datetime.strptime(timeNow, '%H:%M:%S') - datetime.datetime.strptime(str(time), '%H:%M:%S')

        if timeDiff.total_seconds() > 0:
            return True
        else:
            return False
        
    def __transferPiece__(self): #TODO implement the piece go back
        while True:
            time.sleep(1)
            if self.warehouses[0].getStock()[7] < 3 and self.warehouses[1].getStock()[7] > 0: #To produce P9 from P8
                self.warehouses[1].outputPiece('P8', 0)
                
                self.db.insertInQueue("outWH", {'conveyor' : 0, 'piece' : 8}, "mes")
                self.db.updateWare('P'+str(8), -1, "mes", 2)
                
                while OPCUAClient.getTransferCellStatusEdge() in ['None', 'Fall']:
                    time.sleep(1)
                self.warehouses[0].inputPiece('P8', 0)
                self.db.insertInQueue("inWH", {'conveyor' : 0, 'piece' : 8}, "mes")
                self.db.updateWare('P'+str(8), 1, "mes", 1)
            
            
            elif self.warehouses[0].getStock()[3] < 3 and self.warehouses[1].getStock()[3] > 0: #To produce P5 from P4              
                self.warehouses[1].outputPiece('P4', 0)
                
                self.db.insertInQueue("outWH", {'conveyor' : 0, 'piece' : 4}, "mes")
                self.db.updateWare('P'+str(4), -1, "mes", 2)

                while OPCUAClient.getTransferCellStatusEdge() in ['None', 'Fall']:
                    time.sleep(1)
                self.warehouses[0].inputPiece('P4', 0)
                self.db.insertInQueue("inWH", {'conveyor' : 0, 'piece' : 4}, "mes")
                self.db.updateWare('P'+str(4), 1, "mes", 1)
    def trasnferPiece(self):
        try:
            threading.Thread(target=self.__transferPiece__, daemon=True).start()
            print('[Manager] TransferPiece thread started')
        except:
            print('[Manager] Could not start TransferPiece thread')

class Order:
    def __init__(self, number, workpiece, quantity, due_date, late_pen, early_pen):
        self.number = number
        self.workpiece = workpiece
        self.quantity = quantity
        self.due_date = due_date
        self.late_pen = late_pen
        self.early_pen = early_pen

thread_lock = threading.Lock()


orderQueue = customQueue.customQueue()
requestQueue = customQueue.customQueue()
doneRequestQueue = customQueue.customQueue()

inWHQueue = customQueue.customQueue()
outWHQueue = customQueue.customQueue()
machineUpdateQueue = customQueue.customQueue()
gateUpdateQueue = customQueue.customQueue()

database = Database("root", "admin")

SQLManager = SQLManager(orderQueue, requestQueue, doneRequestQueue, inWHQueue, outWHQueue, machineUpdateQueue, gateUpdateQueue, './Recipe/Recipes.csv', database)
SQLManager.getData()

SQLManager.getOrder()

OPCUAClient = OPCUAClient(inWHQueue, outWHQueue, machineUpdateQueue, gateUpdateQueue, database)
OPCUAClient.opcManager()

manager = Manager(orderQueue, requestQueue, doneRequestQueue, database, OPCUAClient, './Recipe/Recipes.csv', './Recipe/WorkPieceTransform.csv', thread_lock)
manager.configMachines(machineUpdateQueue)

manager.configWareHouse(inWHQueue, outWHQueue)

print('### ORDERING###')
#manager.gates.spawnPieces('P2', 100)
manager.startRestockWareHouse()

manager.postRequests()
manager.startWareHouse()
manager.postDoneOrders()
manager.postOrdersReady()
manager.printRequestQueue()
manager.trasnferPiece()

request = {'Piece': 'P8'}
request2 = {'Piece': 'P4'}
for i in range(3): 
    requestQueue.put(request2)
    manager.db.insertRequestOrder(request2, "requests")

for i in range(3):
    requestQueue.put(request)
    manager.db.insertRequestOrder(request, "requests")

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