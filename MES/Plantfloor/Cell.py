import time
import csv
import threading

class Cell:
    def __init__(self, ID, requestQueue):
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
        self.machines = []

        self.__allTools = self.__availableTools()

        self.run()
        self.printStatus()

    def addMachine(self, machine):
        self.machines.append(machine)

    
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
        while True:
            time.sleep(1)
            request = self.requestQueue.get()
            
            if self.machines[0].getType() == 'M1' and self.machines[1].getType() == 'M2':
                if request['Piece'] == 'P3' or\
                request['Piece'] == 'P4' or\
                request['Piece'] == 'P6' or\
                request['Piece'] == 'P7' or\
                request['Piece'] == 'P8':
                    print('Can process')
                    self.setBusy()
                else:
                    print('Can not process')
                    self.requestQueue.orderedPut(request)
            elif self.machines[0].getType() == 'M3' and self.machines[1].getType() == 'M4':
                if request['Piece'] == 'P3' or\
                request['Piece'] == 'P8' or\
                request['Piece'] == 'P5' or\
                request['Piece'] == 'P7' or\
                request['Piece'] == 'P9':
                    print('Can process')
                    self.setBusy()
                else:
                    print('Can not process')
                    self.requestQueue.orderedPut(request)
            
            if self.isBusy():
                toolsOrder = request['Tools'] #exp: 'T1;T2;T3'
                toolsOrder = toolsOrder.split(';') #exp: ['T1', 'T2', 'T3']
                times = request['Time'].split(';')

                for t in toolsOrder:
                    if t not in self.__allTools:
                        print('Invalid tool: ', t)
                        break
                
                if len(toolsOrder) == 1:
                    self.machines[1].setBusy()
                    self.machines[1].setTool(toolsOrder[0])

                    while not self.machines[1].isPieceInPosition(): #wait until piece is in position
                        time.sleep(0.5)
                    
                    self.machines[1].setActive()
                    time.sleep(times[0])
                    self.machines[1].setInactive()
                    
                    while self.machines[1].isPieceInPosition(): #wait until piece is not in position
                        time.sleep(0.5)
                    self.machines[1].setFree()
                    self.setFree()
                        
                elif len(toolsOrder) == 2:
                    self.machines[0].setBusy()
                    self.machines[0].setTool(toolsOrder[0])
                    self.machines[1].setTool(toolsOrder[1])
                    
                    while not self.machines[0].isPieceInPosition():
                        time.sleep(0.5)
                        
                    self.machines[0].setActive()
                    time.sleep(times[0])
                    self.machines[0].setInactive()

                    while self.machines[0].isPieceInPosition(): #wait until piece is not in position
                        time.sleep(0.5)
                    self.machines[0].setFree()

                    
                    self.machines[1].setBusy()
                    while not self.machines[1].isPieceInPosition():
                        time.sleep(0.5)
                        
                    self.machines[1].setActive()
                    time.sleep(times[1])
                    self.machines[1].setInactive()

                    while self.machines[1].isPieceInPosition(): #wait until piece is not in position
                        time.sleep(0.5)
                    self.machines[1].setFree()
                    self.setFree()

                elif len(toolsOrder) == 3:
                    self.machines[0].setBusy()
                    self.machines[0].setTool(toolsOrder[0])
                    self.machines[1].setTool(toolsOrder[1])
                    
                    while not self.machines[0].isPieceInPosition():
                        time.sleep(0.5)
                        
                    self.machines[0].setActive()
                    time.sleep(times[0])
                    self.machines[0].setInactive()

                    while self.machines[0].isPieceInPosition(): #wait until piece is not in position
                        time.sleep(0.5)
                    self.machines[0].setFree()

                    
                    self.machines[1].setBusy()
                    while not self.machines[1].isPieceInPosition():
                        time.sleep(0.5)
                        
                    self.machines[1].setActive()
                    time.sleep(times[1])
                    self.machines[1].setInactive()

                    self.machines[1].setTool(toolsOrder[2])
                    #tool in position?
                    while not self.machines[1].isToolInPosition(): #wait until tool is in position
                        time.sleep(30) #TEMPORARY SOLUTION                        
                        self.machines[1].setToolInPosition()#TODO fix tool in position
                    
                    self.machines[1].setActive()
                    time.sleep(times[2])
                    self.machines[1].setInactive()
                    
                    while self.machines[1].isPieceInPosition(): #wait until piece is not in position
                        time.sleep(0.5)
                    self.machines[1].setFree()
                    self.setFree()

                else:
                    print('Invalid number of tools: ', len(toolsOrder))
                    break

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
                currStatus.append(m.getStatus())

            if currStatus != pastStatus:
                pastStatus = currStatus
                print('Cell', self.ID, 'is busy:', currStatus, 'machines:', [m.getID() for m in self.machines])
            time.sleep(0.5)

            

 
    def __availableTools(self):
        tools = []
        for m in self.machines:
            for t in m.getAvailableTools():
                if t not in tools:
                    tools.append(t)
        return tools
    
    def __reader(self, filename):
        with open(filename, newline='') as csvfile:
            return csv.DictReader(csvfile)
        
    def __getToolOrder(self, Piece):
        return self.recipes.getRecipeData(Piece).get('Tools')