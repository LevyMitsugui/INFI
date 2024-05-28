import csv
import os
import time
import Database

class Machine:
    def __init__(self, ID, type, opcuaClient, machineUpdateQueue, database):
        """
        Initializes a new instance of the class.

        Args:
            ID (int): The ID of the Machine.
            type (str): The type of the Machine (M1, M2, M3, or M4).

        Returns:
            None
        """
        self.__verifyType__(type)
        
        self.ID = ID
        self.opcuaClient = opcuaClient
        self.machineUpdateQueue = machineUpdateQueue
        self.busy = False
        self.type = type
        self.__toolSelect__ = 1
        self.time = 0
        self.availableTools = self.__retrieveToolList__()
        self.db = database

    def setBusy(self):
        self.busy = True

    def setFree(self):
        self.busy = False

    def isBusy(self):
        return self.busy
    
    def getID(self):
        return self.ID

    def getType(self):
        return self.type

    def getToolSelect(self):
        return self.__toolSelect__

    def setToolSelect(self, toolSelect):
        if isinstance(toolSelect, int):
            self.__toolSelect__ = toolSelect
        elif 'T' in toolSelect:
            self.__toolSelect__ = int(toolSelect.strip('T'))
        else:
            raise ValueError('Invalid tool selection')

    def getAvailableTools(self):
        return self.availableTools
    
    def __retrieveToolList__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, 'Tools.csv')
        with open(file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            tools = []
            for row in reader:
                if row['Type'] == self.type:
                    tools = row['Tools'].split(';')
            return tools
        
    def __verifyType__(self, type):
        if type != 'M1' and type != 'M2' and type != 'M3' and type != 'M4':
            raise ValueError('Invalid machine type')
        
    def machineDone(self, cell):
        if(self.opcuaClient.getMachineStatus(cell, self.ID)):
            return True
        return False
        
    def waitForMachineDone(self, cell):
        while(not self.opcuaClient.getMachineStatus(cell, self.ID)):
            time.sleep(1)
        return True
    
    def waitForMachineNotDone(self, cell):
        while(self.opcuaClient.getMachineStatus(cell, self.ID)):
            time.sleep(1)
        return True
    
    def updateToolAndTime(self, cell, tool, time, secondTime = 0):
        machine = cell + self.ID*6
        self.setToolSelect('T'+str(tool))
        #self.opcuaClient.setMachineUpdate(1, (cell + (self.ID - 1)*6), tool, time)
        update = {'machine': machine, 'tool': tool, 'time': time, 'secondTime': secondTime}
        self.machineUpdateQueue.put(update)
        self.db.insertInQueue("machineUpd", update, "mes")

    def canUpdateTool(self):#TODO finish integration with OPCUA
        return True