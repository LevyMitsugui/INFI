import time
import csv
import threading

class Cell:
    def __init__(self, ID, requestQueue, doneRequestQueue):
        """
        Initializes an instance of the class with the given ID.

        The Cell class is the interface between the machines and the
        request queue. It is responsible for assigning requests to
        available machines and keeping track of the status of the
        machines. When a request is received, it is added to a request
        queue and the Cell class will assign it to an available machine.

        :param ID: An integer representing the ID of the instance.
        :param requestQueue: The request queue where requests are stored.
        :return: None
        """
        self.ID = ID
        self.busy = False
        self.requestQueue = requestQueue
        self.doneRequestQueue = doneRequestQueue
        self.machines = []
        self.processedRequests = 0

        #self.__allTools = self.__availableTools() 

        self.run()
        #self.printStatus()#TODO remove all functions related to printStatus ([]function, []thread)

    def addMachine(self, machine):
        print('[Cell ', self.ID,' Cycle] Adding machine', machine.getID(), 'to cell', self.ID)
        self.machines.append(machine)
        self.updateCellTools()

    
    def setBusy(self):
        self.busy = True

    def setFree(self):
        self.busy = False

    def isBusy(self):
        
        return self.busy

    def getID(self):
        return self.ID
    
    def getMachines(self):
        return self.machines
    
    def run(self):
        threading.Thread(target=self.__cycle, daemon=True).start()

    def __cycle(self):
        #TODO implement this: while ocpcua Connected, because, for now, the code will run even if there is no connection
        
        while True:
            time.sleep(1)

            if len(self.machines) < 2 or len(self.machines) > 2:
                print('[Cell ', self.ID,' Cycle] Machines improperly allocated to cell (machines:', len(self.machines), ')')
                continue
            #request = self.requestQueue.get()  

            """ if self.machines[0].getType() == 'M1' and self.machines[1].getType() == 'M2':
                if request['Piece'] == 'P3' or\
                request['Piece'] == 'P4' or\
                request['Piece'] == 'P6' or\
                request['Piece'] == 'P7' or\
                request['Piece'] == 'P8':
                    print('[Cell ', self.ID,' Cycle] Can process')
                    self.setBusy()
                else:
                    print('[Cell ', self.ID,' Cycle] Can not process')
                    self.requestQueue.put(request)
            elif self.machines[0].getType() == 'M3' and self.machines[1].getType() == 'M4':
                if request['Piece'] == 'P3' or\
                request['Piece'] == 'P8' or\
                request['Piece'] == 'P5' or\
                request['Piece'] == 'P7' or\
                request['Piece'] == 'P9':
                    print('[Cell ', self.ID,' Cycle] Can process')
                    self.setBusy()
                else:
                    print('[Cell ', self.ID,' Cycle] Can not process')
                    self.requestQueue.orderedPut(request)
            else:
                print('[Cell ', self.ID,' Cycle] Indetermined piece, request will not be put back in queue')
                request = None """
            
            request = self.getRequest()
            if request is None:
                continue
            self.setBusy()

            if self.isBusy():
                toolsOrder = request['Tools'] #exp: 'T1;T2;T3'
                toolsOrder = toolsOrder.split(';') #exp: ['T1', 'T2', 'T3']
                times = request['Time'].split(';')

                for t in toolsOrder:
                    if t not in self.__allTools:
                        print('[Cell ', self.ID,' Cycle] Invalid tool: ', t)
                        break
                
                if len(toolsOrder) == 1:
                    print('[Cell ', self.ID,' Cycle] One step process')
                    self.machines[1].setBusy()
                    self.machines[1].setToolSelect(toolsOrder[0])
                    self.machines[1].setTime(times[0])

                    time.sleep(float(times[0]))
                    while not self.machines[1].machineDone(): #wait until piece is processed #TODO mock function just to simulate the piece processing
                        time.sleep(0.5)
                    
                    self.machines[1].setFree()
                    self.setFree()
                    self.processedRequests += 1
                    print('[Cell ', self.ID,' Cycle] Done one step process. Cell processed ', self.processedRequests, ' requests so far')
                        
                elif len(toolsOrder) == 2:
                    print('[Cell ', self.ID,' Cycle] Two step process')
                    self.machines[0].setBusy()
                    self.machines[0].setToolSelect(toolsOrder[0])
                    self.machines[0].setTime(times[0])
                    self.machines[1].setToolSelect(toolsOrder[1])
                    self.machines[1].setTime(times[1])
                    
                    while not self.machines[0].machineDone(): #wait until piece is processed #TODO mock function
                        time.sleep(0.5)
                    self.machines[0].setFree()

                    self.machines[1].setBusy()
                    while not self.machines[1].machineDone(): #wait until piece is processed #TODO mock
                        time.sleep(0.5)   
                    self.machines[1].setFree()
                    self.setFree()
                    self.processedRequests += 1
                    print('[Cell ', self.ID,' Cycle] Done two step process. Cell', self.ID, ' processed ', self.processedRequests, ' requests so far')

                elif len(toolsOrder) == 3:
                    print('[Cell ', self.ID,' Cycle] Three step process')
                    self.machines[0].setBusy()
                    self.machines[0].setToolSelect(toolsOrder[0])
                    self.machines[0].setTime(times[0])
                    self.machines[1].setToolSelect(toolsOrder[1])
                    self.machines[1].setTime(times[1])
                    
                    while not self.machines[0].machineDone(): #wait until piece is processed #TODO mock function just to simulate the piece processing
                        time.sleep(0.5)
                    self.machines[0].setFree()    

                    self.machines[1].setBusy()
                    while not self.machines[1].machineDone(): #wait until piece is processed #TODO mock function
                        time.sleep(0.5)

                    self.machines[1].setToolSelect(toolsOrder[2])
                    self.machines[1].setTime(times[2])
                    
                    while not self.machines[1].machineDone(): #wait until piece is processed #TODO mock function
                        time.sleep(0.5)
                    self.machines[1].setFree()
                    self.setFree()
                    self.processedRequests += 1
                    print('[Cell ', self.ID,' Cycle] Done three step process. Cell processed ', self.processedRequests, ' requests so far')

                else:
                    print('[Cell ', self.ID,' Cycle] Invalid number of tools in request: ', len(toolsOrder))
                    break

                self.doneRequestQueue.put(request['Piece'])

    def getRequest(self):
        #print('[Cell ', self.ID, ' getRequest] Request queue size: ', self.requestQueue.qsize())
        for iterator in range(self.requestQueue.qsize()):
            #print("[Cell ", self.ID, " getRequest] Request index: ", iterator)
            request = self.requestQueue.peek(block = False, index = iterator)
            
            if self.machines[0].getType() == 'M1' and self.machines[1].getType() == 'M2':
                if request['Piece'] == 'P3' or\
                request['Piece'] == 'P4' or\
                request['Piece'] == 'P6' or\
                request['Piece'] == 'P7' or\
                request['Piece'] == 'P8':
                    requestTaken = self.requestQueue.get(iterator)
                    print('[cell ', self.ID, ' getRequest] Request Peeked ', request)
                    print('[Cell ', self.ID, ' getRequest] Request taken: ', requestTaken)
                    if request != requestTaken:
                        self.requestQueue.put(requestTaken)
                        return None
                    return requestTaken

            elif self.machines[0].getType() == 'M3' and self.machines[1].getType() == 'M4':
                if request['Piece'] == 'P3' or\
                request['Piece'] == 'P8' :
                    requestTaken = self.requestQueue.get(iterator)
                    print('[cell ', self.ID, ' getRequest] Request Peeked ', request)
                    print('[Cell ', self.ID, ' getRequest] Request taken: ', requestTaken)
                    if request != requestTaken:
                        self.requestQueue.put(requestTaken)
                        return None
                    return requestTaken

            else:
                request = None
        
        return None


    def printStatus(self):
        threading.Thread(target=self.__printStatus, daemon=True).start()
    
    def __printStatus(self):
        pastStatus = []
        pastStatus.append(self.isBusy())
        for m in self.machines:
            pastStatus.append(m.getStatus())
    
        while True:
            currStatus = []
            currStatus.append(self.isBusy())
            for m in self.machines:
                currStatus.append(m.isBusy())

            if currStatus[0] != pastStatus[0] or currStatus[1] != pastStatus[1] or currStatus[2] != pastStatus[2]:
                pastStatus = currStatus
                print('[Cell ', self.ID,' Cycle] Is cell', self.ID, 'busy?:', currStatus, 'machines:', [m.getID() for m in self.machines])
            time.sleep(0.5)

            

 
    def __availableTools(self):
        tools = []
        for m in self.machines:
            for t in m.getAvailableTools():
                if t not in tools:
                    tools.append(t)
        return tools
    
    def updateCellTools(self):
        self.__allTools = self.__availableTools()
    
    def __reader(self, filename):
        with open(filename, newline='') as csvfile:
            return csv.DictReader(csvfile)
        
    def __getToolOrder(self, Piece):
        return self.recipes.getRecipeData(Piece).get('Tools')