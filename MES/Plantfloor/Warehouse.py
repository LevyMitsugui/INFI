import sys
sys.path.append('C:\\Users\\Levy\\Documents\\GitHub\\INFI\\MES\\OPCUAClient')  # Add the path to the customQueue directory  # Add the path to the customQueue directory
import OPCUAClient
from math import floor
import time

class Warehouse:
    def __init__(self, ID, opcuaClient, inWHQueue, outWHQueue): #, database):
        self.opcuaClient = opcuaClient
        self.ID = ID
        self.pieces = [10,0,0,0,0,0,0,0,0]
        self.inputGates = []

        self.inWHQueue = inWHQueue
        self.outWHQueue = outWHQueue
        self.db = None #database

    #generic functions
    def getID(self):
        return self.ID
    def getStock(self):
        return self.pieces

    #in functions
    def inputPiece(self, piece, conveyour):
        """
        Adds a piece to the warehouse and puts a dictionary containing information about the piece and its conveyor into the input queue.

        Parameters:
            piece (str): The piece to be added to the warehouse.
            conveyour (str): The conveyor from which the piece was received 0 to 10, consult \MES\Plantfloor\Conveyours.png.

        Returns:
            None
        """
        self.pieces[int(piece.strip('P'))-1] += 1
        #TODO update in database
        piece = int(piece.strip('P'))
        update = {'conveyour' : conveyour, 'piece' : piece}
        self.inWHQueue.put(update)
    
    #out functions
    def outputPiece(self, piece, conveyour):
        """
        Removes a piece from the warehouse and puts a dictionary containing information about the piece and its output gate into the output queue.

        Parameters:
            piece (str): The piece to be removed from the warehouse.
            conveyour (str): The output gate to which the piece is being sent.

        Returns:
            None
        """
        self.pieces[int(piece.strip('P'))-1] -= 1
        #TODO update in database
        piece = int(piece.strip('P'))
        self.outWHQueue.put({'conveyour' : conveyour, 'piece' : piece})
        time.sleep(2)
        

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
