import sys
sys.path.append('C:\\Users\\Levy\\Documents\\GitHub\\INFI\\MES\\OPCUAClient')  # Add the path to the customQueue directory  # Add the path to the customQueue directory
import OPCUAClient
from math import floor
import time

class Warehouse:
    def __init__(self, ID, opcuaClient, inWHQueue, outWHQueue, database):
        self.opcuaClient = opcuaClient
        self.ID = ID
        self.pieces = self.__getInitialWHState__()
        self.inputGates = []

        self.inWHQueue = inWHQueue
        self.outWHQueue = outWHQueue
        self.db = database #database

    #generic functions
    def getID(self):
        return self.ID
    def getStock(self):
        return self.pieces
    
    def setStock(self, pieceType, quantity):
        """
        Sets the stock for a specific type of piece in the warehouse.

        Parameters:
            pieceType (str): The type of piece to be updated.
            quantity (int): The new quantity for the specified piece type.

        Returns:
            None
        """
        pieceIndex = int(pieceType.strip('P')) - 1
        if 0 <= pieceIndex < len(self.pieces):
            self.pieces[pieceIndex] = quantity

    #in functions
    def inputPiece(self, piece, conveyor):
        """
        Adds a piece to the warehouse and puts a dictionary containing information about the piece and its conveyor into the input queue.

        Parameters:
            piece (str): The piece to be added to the warehouse.
            conveyor (str): The conveyor from which the piece was received 0 to 10, consult \MES\Plantfloor\conveyors.png.

        Returns:
            None
        """
        self.pieces[int(piece.strip('P'))-1] += 1
        #TODO update in database
        piece = int(piece.strip('P'))
        update = {'conveyor' : conveyor, 'piece' : piece}
        self.inWHQueue.put(update)
        self.db.insertInQueue("inWH", update, "mes")
    
    #out functions
    def outputPiece(self, piece, conveyor):
        """
        Removes a piece from the warehouse and puts a dictionary containing information about the piece and its output gate into the output queue.

        Parameters:
            piece (str): The piece to be removed from the warehouse.
            conveyor (str): The output gate to which the piece is being sent.

        Returns:
            None
        """
        self.pieces[int(piece.strip('P'))-1] -= 1
        #TODO update in database
        piece = int(piece.strip('P'))
        
        if conveyor >= 7 and self.ID == 1:
            while self.opcuaClient.getOutputWarehouseStatus(conveyor) == True:
                time.sleep(0.5)
        update = {'conveyor' : conveyor, 'piece' : piece}
        self.outWHQueue.put(update)
        self.db.insertInQueue("outWH", update, "mes")
        time.sleep(2)

    def __getInitialWHState__(self):
        if self.getID() == 0:
            return [20,0,0,0,0,0,0,0,0]
        elif self.getID() == 1:
            return [0,0,0,0,0,0,0,0,10]
        else:
            raise ValueError("Invalid warehouse ID")
        

class WarehouseUp(Warehouse):
    def __init__(self, ID, opcuaClient):
        super().__init__(ID, opcuaClient)

    def spawnPieces(self, pieceType, quantity, gates = [1,2,3,4]):
        piecesByGate = floor(quantity/len(gates))
        remainder = quantity%len(gates)
        self.opcuaClient.setPieceSpawn(1, 1, pieceType.strip('P'), gates)

        spawnGatesStatus = [False]
        
        while not all(spawnGatesStatus):
            for i in range(4):
                spawnGatesStatus[i] = self.opcuaClient.getGateStatus(i+1)

            time.sleep(0.5)

        return piecesByGate
