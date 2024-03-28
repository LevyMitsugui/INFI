
class Machine:
    def __init__(self, ID, type):
        """
        Initializes a new instance of the class.

        Args:
            ID (int): The ID of the instance.
            type (str): The type of the instance.

        Returns:
            None
        """
        self.ID = ID
        self.busy = False
        self.type = type

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