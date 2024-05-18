import time
import csv
import threading

class Cell:
    def __init__(self, ID, requestQueue, doneRequestQueue, recipes):
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
        self.recipes = recipes

        

        self.__allTools = []#self.__availableTools() 

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

            request, recipe = self.getRequest()
            if request is None or recipe is None:
                continue
            self.setBusy()

            print('[Cell ', self.ID,' Cycle] Request: ', request)
            print('[Cell ', self.ID,' Cycle] Recipe: ', recipe)
            
            self.setFree()
            self.doneRequestQueue.put(request['Piece'])

    def getRequest(self):
        for iterator in range(self.requestQueue.qsize()):
            request = self.requestQueue.peek(block = False, index = iterator)
            recipe = self.getRecipe(request)

            if(recipe != None and self.requestQueue.qsize() > 0):
                requestGotten = self.requestQueue.get(iterator)
                
                if requestGotten['Piece'] != request['Piece']:
                    self.requestQueue.put(requestGotten)
                    print('!![Cell ', self.ID, ' getRequest]!! Failded to get right request')
                    return (None, None)
                
                print('**[Cell ', self.ID, ' getRequest]** verified request gave recipe: ', recipe)
                return (request, recipe)
                
            else: #There is no recipe for this request
                request = None
        
        return (None, None)

    def getRecipe(self, request):#TODO restructure this
        valid = []

        for recipe in self.recipes:
            if recipe['Piece'] == request['Piece']:
                tools = recipe['Tools'].split(';')
                for tool in tools:
                    if len(valid) == len(tools):
                        break
                    # print('[Cell ', self.ID,' Cycle] Checking tool: ', tool, ' in recipe: ', tools, 'is valid: ', tool in self.__allTools)
                    valid.append(tool in self.__allTools)
                # print('[Cell ', self.ID,' Cycle] Valid: ', valid)
                if all(valid):
                    return recipe                

        return None
    
    def __arrangeSteps(self, recipe):
        steps = []
        timeIndex = 0
        times = recipe['Time'].split(';')
        
        for it in range(len(self.machines)):
            for tool in recipe['Tools']:
                print('[Cell ', self.ID,' Cycle] Checking machine ', it, ' for tool ', tool)
                if tool in self.machines[it].availableTools:
                    steps.append({'Machine': it, 'Tool': tool, 'Time': times[timeIndex]})
                    timeIndex += 1
                else:
                    break
        
        """ if len(steps) != len(recipe['Tools']):
            print('[Cell ', self.ID,' Cycle] Invalid number of tools in request: ', len(steps))
        if len(steps) != len(times):
            print('[Cell ', self.ID,' Cycle] Invalid number of times in request: ', len(steps))
        if len(steps) != timeIndex+1:
            print('[Cell ', self.ID,' Cycle] Invalid number of steps in request or invelid number of times: ', len(steps))
 """
        if len(steps) == len(recipe['Tools']) and len(steps) == len(times) and len(steps) == timeIndex+1:
            return steps

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

            
    def getAllTools(self):
        return self.__allTools
 
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