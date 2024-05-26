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

        self.time = time.process_time()
        self.prevTime = self.time
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
        newThread = threading.Thread(target=self.__cycle__, daemon=True)
        newThread.setName('Cell ' + str(self.ID) + ' Cycle')
        newThread.start()


    def __cycle__(self):
        #TODO implement this: while ocpcua Connected, because, for now, the code will run even if there is no connection
        

        while len(self.machines) != 2:
            time.sleep(0.3)
            print('[Cell ', self.ID,' Cycle] Machines improperly allocated to cell (machines:', len(self.machines), ')')
                   
        
        print('[Cell ', self.ID,' Cycle] Machines allocated to cell (machines:', len(self.machines), ')')

        while True:
            self.time = time.process_time()
            if self.time - self.prevTime > 1:
                self.prevTime = self.time
                print('[Cell ', self.ID,' Cycle] Cell ', self.ID, ' running. Time: ', self.time)                

            self.machines[0].waitForMachineDone(self.ID)
            self.machines[1].waitForMachineDone(self.ID)
            request, recipe = self.getRequest() 
            if request is None or recipe is None:
                time.sleep(3)
                continue
            self.setBusy()
            print('[Cell ', self.ID,' Cycle] Processing request: ', request)

            if not 'Step' in request.keys() and request['Piece'] != 'P5' and request['Piece'] != 'P9':
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

            elif request['Piece']=='P9' and 'Steps' in request.keys():
                print('[Cell ', self.ID,' Cycle] Processing request: ', request)
                print('[Cell ', self.ID,' Cycle] Processing steps: ', request['Steps'])
                print('[Cell ', self.ID,' Cycle] steps length: ', len(request['Steps']))
                self.warehouses[0].outputPiece('P2', self.ID)
                #piece goes straight to the second machine (skips machine 0)
                self.machines[0].updateToolAndTime(self.ID, self.machines[0].getToolSelect(),0)#TODO update right tool

                steps = request['Steps']
                print('[Cell ', self.ID,' Cycle] steps: ', steps)
                step = steps.pop(0)
                print('[Cell ', self.ID,' Cycle] first step: ', step)
                print('[Cell ', self.ID,' Cycle] steps after removal: ', steps)
                print('[Cell ', self.ID,' Cycle] steps length: ', len(steps))	
                waitingTime = step['Time']
                #machine 1 is updated to process piece
                self.machines[1].updateToolAndTime(self.ID, step['Tool'],step['Time'])
                self.machines[1].waitForMachineNotDone(self.ID)
                #Waits to piece arive to the second machine and SHOULD wait to the machine start(waits for tool change)
                
                #when machine 1 starts, update machine 2
                step = steps.pop(0)      
                print('[Cell ', self.ID,' Cycle] second step: ', step)                                        #machine 1 is already processing P2 to P8
                waitingTime += step['Time']                                                 #machine 1 is processing P2 to P8
                self.machines[0].updateToolAndTime(self.ID, step['Tool'],step['Time'])      #machine 1 is processing P2 to P8
                self.warehouses[0].outputPiece('P8', self.ID)#sfs will wait til there's piece     #machine 1 is processing P2 to P8
                #machine 0 is updated to process piece                                      #machine 1 is processing P2 to P8

                self.machines[1].waitForMachineDone(self.ID)
                self.machines[1].updateToolAndTime(self.ID, self.machines[1].getToolSelect(), 0) #ignores the piece being processed at machine 0
                self.warehouses[1].inputPiece('P8' , 4 + self.ID)
                #Piece P8 is stored

                self.machines[1].waitForMachineDone(self.ID)
                self.warehouses[1].inputPiece('P9' , 4 + self.ID)
                #Piece P9 is stored

                self.setFree()

            self.doneRequestQueue.put(request['Piece'])




            

    def getRequest(self):
        """ request = self.requestQueue.get()
        if request['Piece'] == 'P9' and self.ID < 3:
            self.requestQueue.put(request)
            return (None, None)
        recipe = self.getRecipe(request)
        reqGotTup = self.db.processRequestByPiece(request['Piece'], "requests")
        if(recipe != None and self.requestQueue.qsize() > 0):
            if request['Piece'] == 'P9':
                    print('request ID: ', request['ID'])         
            if(reqGotTup != None):
                        self.db.returnRequestByPiece(reqGotTup[0][0], "requests")
            return (request, recipe)
        else :
            self.requestQueue.put(request)
            return (None, None) """


        for iterator in range(self.requestQueue.qsize()):
            request = self.requestQueue.peek(block = False, index = iterator)
            if request is None or request['Piece'] == 'P9' or request['Piece'] == 'P5': #TODO if want to implement P5 and P9, need to change this
                continue #TODO maybe not the solution, perhaps have to rest the hole cycle
            recipe = self.getRecipe(request)
            reqGotTup = self.db.processRequestByPiece(request['Piece'], "requests")

            if(recipe != None and self.requestQueue.qsize() > 0):
                requestGotten = self.requestQueue.get(iterator)
                
                if request['Piece'] == 'P9':
                    print('request ID: ', request['ID'])
                    print('requestGotten ID: ', requestGotten['ID'])

                if requestGotten != request: #TODO maybe revert this requestGotten['Piece'] != request['Piece']:
                    if(reqGotTup != None):
                        self.db.returnRequestByPiece(reqGotTup[0][0], "requests")
                    
                    self.requestQueue.put(requestGotten)
                    #print('!![Cell ', self.ID, ' getRequest]!! Failded to get right request')
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