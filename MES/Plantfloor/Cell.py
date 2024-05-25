import time
import csv
import threading
import sys
sys.path.append("..")
from Database import Database
import PlantFloor

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
        self.warehouses = []
        self.processedRequests = 0
        self.recipes = recipes

        self.db = Database("root", "admin")

        
        self.setsLists = []

        self.__allTools = []#self.__availableTools() 

        self.run()
        #self.printStatus()#TODO remove all functions related to printStatus ([]function, []thread)
        
    def addMachine(self, machine):
        #print('[Cell ', self.ID,' Cycle] Adding machine', machine.getID(), 'to cell', self.ID)
        try:
            self.machines.append(machine)
            self.updateCellTools()
            return True
        except:
            print('[Cell ', self.ID,' Cycle] Failed to add machine', machine.getID(), 'to cell', self.ID)
            return False
        
    def addWarehouse(self, warehouse):
        try:
            self.warehouses.append(warehouse)
            return True
        except:
            print('[Cell ', self.ID,' Cycle] Failed to add warehouse', warehouse.getID(), 'to cell', self.ID)
            return False

    
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
        

        while len(self.machines) != 2:
            time.sleep(1)
            print('[Cell ', self.ID,' Cycle] Machines improperly allocated to cell (machines:', len(self.machines), ')')
                   
        
        print('[Cell ', self.ID,' Cycle] Machines allocated to cell (machines:', len(self.machines), ')')

        while True:
            self.machines[0].waitForMachineDone(self.ID)
            self.machines[1].waitForMachineDone(self.ID)
            #TODO continue Testing Here

            request, recipe = self.getRequest()
            if request is None or recipe is None:
                time.sleep(3)
                continue
            self.setBusy()

            print('The game has begun!')
            self.setsLists.insert(0, self.__arrangeSteps__(recipe))
            print(self.setsLists)
            print('É aqui oh mano:', self.setsLists[0])
            
            self.warehouses[0].outputPiece(recipe['Material'], self.ID)
            
            print(self.setsLists[0][0])
            step = self.setsLists[0].pop(0)

            self.machines[0].updateToolAndTime(self.ID, step[1],step[2])

            self.__removeDoneSteps__(self.setsLists[0][0][0], self.setsLists)# remove the first step from the first step set of the first list
            print('after removal',self.setsLists)

            # print('[Cell ', self.ID,' Cycle] Request: ', request)
            # print('[Cell ', self.ID,' Cycle] Recipe: ', recipe)
            
            # self.setFree()
            # self.doneRequestQueue.put(request['Piece'])

            

    def getRequest(self):
        for iterator in range(self.requestQueue.qsize()):
            request = {}
            request = self.requestQueue.peek(block = False, index = iterator)
            recipe = self.getRecipe(request)

            if(recipe != None and self.requestQueue.qsize() > 0):
                requestGotten = self.requestQueue.get(iterator)
                
                if requestGotten['Piece'] != request['Piece']:
                    self.requestQueue.put(requestGotten)
                    print('!![Cell ', self.ID, ' getRequest]!! Failded to get right request')
                    return (None, None)
                
                reqGotTup = self.db.processRequestByPiece(requestGotten['Piece'], "requests")
                if(reqGotTup != None):
                    reqGot = {'Piece': reqGotTup[0][0], 'Material': reqGotTup[0][1], 'Time': reqGotTup[0][2], 'Tools': reqGotTup[0][3]}
                    if requestGotten['Piece'] != reqGot['Piece']:
                        print('!![Cell ', self.ID, ' DATABASE getRequest]!! Failded to get right request')
                print('**[Cell ', self.ID, ' getRequest]** verified request gave recipe: ', recipe)
                return (request, recipe)
                
            else: #There is no recipe for this request
                request = None
        return (None, None)
    

    def getRecipe(self, request):#TODO restructure this

        for recipe in self.recipes:
            valid = []
            if recipe['Piece'] == request['Piece']:
                if ';' in recipe['Tools']:
                    tools = recipe['Tools'].split(';')
                else:
                    tools = [recipe['Tools']]
                for tool in tools:
                    if len(valid) == len(tools):
                        break
                    # print('[Cell ', self.ID,' Cycle] Checking tool: ', tool, ' in recipe: ', tools, 'is valid: ', tool in self.__allTools)
                    valid.append(tool in self.__allTools__)
                # print('[Cell ', self.ID,' Cycle] Valid: ', valid)
                if all(valid):
                    return recipe                

        return None
    
    
    def __removeDoneSteps__(self, machine, setList):
        """
        A function that removes steps that are marked as done for a specific machine
        
        Parameters:
            machine (str): The machine name to filter the steps for.
            steps (list): A list of steps to filter.
        
        Returns:
            None
        """
        for stepsSet in setList:
            for step in stepsSet:
                if step[0] == machine:
                    stepsSet.remove(step)
                
            
        return stepsSet
    
    def __arrangeSteps__(self, recipe, maxToolChange = 2):
        steps = []

        if ';' in recipe['Tools']:
            tools = [int(tool.strip('T')) for tool in recipe['Tools'].split(';')]
        else:
            tools = [int(recipe['Tools'].strip('T'))]
        
        if ';' in recipe['Time']:
            times = [eval(x) for x in recipe['Time'].split(';')]
        else:
            times = [eval(recipe['Time'])]
        
        
        #set steps of second machine first
        changes = 0
        for iterator in range(len(tools)-1, 0, -1):
            steps.insert(0, (1,tools[iterator], times[iterator]))
            changes += 1
            if changes == maxToolChange:
                break

        if len(tools) >= 2:
            steps.insert(0, (0,tools[0], times[0]))

        
        return steps
 

    def printStatus(self):
        threading.Thread(target=self.__printStatus__, daemon=True).start()
    
    def __printStatus__(self):
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
        return self.__allTools__
 
    def __availableTools__(self):
        tools = []
        for m in self.machines:
            for t in m.getAvailableTools():
                if t not in tools:
                    tools.append(t)
        return tools
    
    def updateCellTools(self):
        self.__allTools__ = self.__availableTools__()
        #self.__allTools__.append(self.__availableTools__())
    
    def __reader__(self, filename):
        with open(filename, newline='') as csvfile:
            return csv.DictReader(csvfile)
        
    def __getToolOrder__(self, Piece):
        return self.recipes.getRecipeData(Piece).get('Tools')