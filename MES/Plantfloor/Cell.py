import time
import csv
import threading
import sys
sys.path.append("..")
from Database import Database
import Plantfloor

class Cell:
    def __init__(self, ID, requestQueue, doneRequestQueue, recipes, transformations):
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
        self.transformations = transformations
        self.setsLists = []
        self.db = Database("root", "admin")


        self.__allTools__ = []

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
        threading.Thread(target=self.__cycle__, daemon=True).start()


    def __cycle__(self):
        #TODO implement this: while ocpcua Connected, because, for now, the code will run even if there is no connection
        

        while len(self.machines) != 2:
            time.sleep(0.3)
            print('[Cell ', self.ID,' Cycle] Machines improperly allocated to cell (machines:', len(self.machines), ')')
                   
        
        print('[Cell ', self.ID,' Cycle] Machines allocated to cell (machines:', len(self.machines), ')')

        while True:
             
            self.machines[0].waitForMachineDone(self.ID)
            self.machines[1].waitForMachineDone(self.ID)
            request, recipe = self.getRequest() 
            if request is None or recipe is None:
                time.sleep(3)
                continue
            self.setBusy()

            if not 'Step' in request.keys():
                self.warehouses[0].outputPiece(self.__getPrimaryMaterial__(recipe), self.ID)
                steps = self.__arrangeSteps__(recipe)
                
                if len(steps) == 1:
                    self.machines[0].updateToolAndTime(self.ID, self.machines[0].getToolSelect(),0) #pass straight to the second machine
                    step = steps.pop(0)
                    waitingTime = step['Time']
                    self.machines[1].updateToolAndTime(self.ID, step['Tool'],step['Time'])

                    self.machines[1].waitForMachineNotDone(self.ID)
                    self.machines[1].waitForMachineDone(self.ID)

                    self.warehouses[1].inputPiece(recipe['Piece'] , 4 + self.ID)



                if len(steps) == 2:
                    step = steps.pop(0)
                    waitingTime = step['Time']
                    self.machines[0].updateToolAndTime(self.ID, step['Tool'],step['Time'])
                    
                    step = steps.pop(0)
                    waitingTime += step['Time']
                    if 'SecondTime' in  step.keys():
                        self.machines[1].updateToolAndTime(self.ID, step['Tool'],step['Time'], step['SecondTime'])
                    else:
                        self.machines[1].updateToolAndTime(self.ID, step['Tool'],step['Time'])

                    #self.verifyUnfinished(recipe, steps)

                    #time.sleep(waitingTime)
                    self.machines[1].waitForMachineNotDone(self.ID)
                    self.machines[1].waitForMachineDone(self.ID)

                    self.warehouses[1].inputPiece(recipe['Piece'] , 4 + self.ID)#ha de ser alterado
                self.setFree()
            
            elif 'Step' in request.keys():
                self.warehouses[0].outputPiece('P4', self.ID)
                self.machines[0].updateToolAndTime(self.ID, self.machines[0].getToolSelect(),0)    
                
                step = request['Step']
                waitingTime = step['Time']
                self.machines[1].updateToolAndTime(self.ID, step['Tool'],step['Time'])
                time.sleep(waitingTime)
                self.machines[1].waitForMachineNotDone(self.ID)
                self.machines[1].waitForMachineDone(self.ID)

                self.warehouses[1].inputPiece(recipe['Piece'] , 4 + self.ID)#ha de ser alterado
                self.setFree()




            

    def getRequest(self):
        for iterator in range(self.requestQueue.qsize()):
            request = self.requestQueue.peek(block = False, index = iterator)
            reqGotTup = self.db.processRequestByPiece(request['Piece'], "requests")
            recipe = self.getRecipe(request)

            if(recipe != None and self.requestQueue.qsize() > 0):
                requestGotten = self.requestQueue.get(iterator)
                
                if requestGotten['Piece'] != request['Piece']:
                    if(reqGotTup != None):
                        self.db.returnRequestByPiece(reqGotTup[0][0], "requests")
                    self.requestQueue.put(requestGotten)
                    print('!![Cell ', self.ID, ' getRequest]!! Failded to get right request')
                    return (None, None)
                    
                #print('**[Cell ', self.ID, ' getRequest]** verified request gave recipe: ', recipe)
                return (request, recipe)
            
            else: #There is no recipe for this request
                request = None
        
        return (None, None)

    def getRecipe(self, request):
    
        for recipe in self.recipes:
            valid = []
            if recipe['Piece'] == request['Piece']:
                if ';' in recipe['Tools']:
                    tools = recipe['Tools'].split(';')
                else:
                    tools = [recipe['Tools']]
                
                for tool in tools:#for a tool in the recipe
                    if len(valid) == len(tools):
                        break
                    #print('[Cell ', self.ID,' Cycle] Checking tool: ', tool, ' in available tools: ', self.__allTools__, 'is valid: ', tool in self.__allTools__)
                    valid.append(tool in self.__allTools__)
                #print('[Cell ', self.ID,' Cycle] Valid: ', valid)
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
        if len(tools) == 1:
            steps.insert(0, {'Machine': 1, 'Tool':tools[0], 'Time': times[0]})
        elif len(tools) == 2:
            steps.insert(0, {'Machine': 1, 'Tool':tools[1], 'Time': times[1]})
            steps.insert(0, {'Machine': 0,'Tool':tools[0],'Time': times[0]})
        elif len(tools) == 3:
            for iterator in range(len(tools)-1, 0, -1):
                steps.insert(0, {'Machine': 1, 'Tool':tools[iterator], 'Time': times[iterator]})
                
                changes += 1
                if changes == maxToolChange:
                    break
        
            steps.insert(0, {'Machine': 0,'Tool':tools[0],'Time': times[0]})
            if(steps[1]['Tool'] == steps[2]['Tool']): #if the tools are the same
                removed = steps.pop()
                steps[1]['SecondTime'] = removed['Time'] #add the time of the removed step to the second step

        return steps
    
    def verifyUnfinished(self, recipe, steps):
        if len(steps)>0:
            self.requestQueue.put({'Piece':recipe['Piece']})
            return True

        else:
            return False

    def getMaterial(self, recipe):
        if ';' in recipe['Material']:
            return recipe['Material'].split(';')
        else:
            return [recipe['Material']]
    
    def __getPrimaryMaterial__(self,recipe):
        if ';' in recipe['Material']:
            return recipe['Material'].split(';')[0]
        else:
            return recipe['Material']

    def __midPieces__(self, recipe):
        midPieces = []
        material = recipe['Material']
        tools = recipe['Tools'].split(';')
        midPieces.append(material)
        for t in tools:
            for transformation in self.transformations:
                if transformation['Tool'] == t and transformation['Material'] == material:
                    if transformation['Piece'] == recipe['Piece']:
                        break
                    midPieces.append(transformation['Piece'])
                    material = transformation['Piece']
                    break
        
        return midPieces
    

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