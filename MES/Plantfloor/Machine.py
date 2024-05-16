import csv

class Machine:
    def __init__(self, ID, type):
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
        with open('./Tools.csv', newline='') as csvfile:
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
    def machineDone(self):#TODO finish integration with OPCUA   
        return True
    
    def canUpdateTool(self):#TODO finish integration with OPCUA
        return True