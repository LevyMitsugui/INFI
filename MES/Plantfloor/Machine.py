import csv
import os
import time

class Machine:
    def __init__(self, ID, type, opcuaClient):
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
        self.busy = False
        self.type = type
        self.toolSelect = ''
        self.time = 0
        self.availableTools = self.__retrieveToolList__()

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

    def setTime(self, time):
        self.time = time#TODO finish integration with OPCUA

    def setToolSelect(self, toolSelect):#TODO finish integration with OPCUA
        if toolSelect not in self.availableTools:
            raise ValueError('Invalid tool selection')
        self.toolSelect = toolSelect
        #opcuaClient.setTool(2, self.toolSelect)

    def getToolSelect(self):
        return self.toolSelect
    
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
        
    #mock functions #TODO should be removed when system is operating
    def machineDone(self, cell):
        if(self.opcuaClient.getMachineStatus(cell, self.ID)):
            return True
        return False
        
    def waitForMachineDone(self, cell):
        while(not self.opcuaClient.getMachineStatus(cell, self.ID)):
            time.sleep(1)
        return True
    
    def updateToolAndTime(self, cell, tool, time):
        self.opcuaClient.setMachineUpdate(1, (cell + (self.ID - 1)*6), tool, time)

    def canUpdateTool(self):#TODO finish integration with OPCUA
        return True