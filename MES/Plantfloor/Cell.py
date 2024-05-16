import time
import csv
import threading

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
        self.processedRequests = 0
        self.recipes = recipes
        self.transformations = transformations

        self.setsLists = []

        self.__allTools__ = []

        self.run()
        #self.printStatus()#TODO remove all functions related to printStatus ([]function, []thread)

    def addMachine(self, machine):
        #print('[Cell ', self.ID,' Cycle] Adding machine', machine.getID(), 'to cell', self.ID)
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
        threading.Thread(target=self.__cycle__, daemon=True).start()


    def __cycle__(self):
        #TODO implement this: while ocpcua Connected, because, for now, the code will run even if there is no connection
        while len(self.machines) < 2 or len(self.machines) > 2:
            time.sleep(1)
            print('[Cell ', self.ID,' Cycle] Machines improperly allocated to cell (machines:', len(self.machines), ')')
        
        while True:
            time.sleep(0.1)
            
            if self.machines[0].machineDone():
                request, recipe = self.getRequest()
                if request is None or recipe is None:
                    continue
                self.setBusy()

                self.setsLists.insert(0, self.__arrangeSteps__(recipe))
                #SET VARIABLES THROUGH OPCUA


                #when processed remove the steps done by the first machine
                
                
                self.setFree()
                self.doneRequestQueue.put(request['Piece'])

            if self.machines[1].machineDone() and self.machines[0].canUpdateTool():
                stepsM1 = self.setsLists.pop()
                self.machines[0].updateTool(stepsM1[1])

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
                    print('[Cell ', self.ID,' Cycle] Checking tool: ', tool, ' in recipe: ', tools, 'is valid: ', tool in self.__allTools)
                    valid.append(tool in self.__allTools__)
                print('[Cell ', self.ID,' Cycle] Valid: ', valid)
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
        tools = recipe['Tools'].split(';')
        midPieces = self.__midPieces__(recipe)
        #set steps of second machine first
        changes = 0
        for iterator in range(len(tools)-1, 0, -1):
            steps.insert(0, (1,tools[iterator], midPieces[len(midPieces)-1-changes]))
            changes += 1
            if changes == maxToolChange:
                break

        if len(tools) >= 2:
            steps.insert(0, (0,tools[0], midPieces[0]))

        
        return steps
    
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
    
    def __reader__(self, filename):
        with open(filename, newline='') as csvfile:
            return csv.DictReader(csvfile)
        
    def __getToolOrder__(self, Piece):
        return self.recipes.getRecipeData(Piece).get('Tools')