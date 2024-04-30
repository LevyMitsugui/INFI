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
        self.__verifyType(type)
        
        self.ID = ID
        self.busy = False
        self.type = type
        self.toolSelect = ''
        self.availableTools = self.__retrieveToolList()

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

    def setToolSelect(self, toolSelect):
        if toolSelect not in self.availableTools:
            raise ValueError('Invalid tool selection')
        self.toolSelect = toolSelect

    def getToolSelect(self):
        return self.toolSelect
    
    def getAvailableTools(self):
        return self.availableTools
    
    def __retrieveToolList(self):
        with open('Plantfloor/Tools.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            tools = []
            for row in reader:
                if row['Type'] == self.type:
                    tools = row['Tools'].split(';')
            return tools
        
    def __verifyType(self, type):
        if type != 'M1' and type != 'M2' and type != 'M3' and type != 'M4':
            raise ValueError('Invalid machine type')
