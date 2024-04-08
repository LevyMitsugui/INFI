
class Cell:
    def __init__(self, ID):
        """
        Initializes an instance of the class with the given ID.

        :param ID: An integer representing the ID of the instance.
        :return: None
        """
        self.ID = ID
        self.busy = False
        self.machines = []
        self.requests = []

    def addRequest(self, request):
        self.requests.append(request)

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
