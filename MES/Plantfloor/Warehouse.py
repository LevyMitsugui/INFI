from OPCUAClient import OPCUAClient
import time

class Warehouse:
    def __init__(self, ID, outputs, opcuaClient, inWHQueue, outWHQueue):
        self.opcuaClient = opcuaClient
        self.ID = ID
        self.pieces = [10,0,0,0,0,0,0,0,0]
        self.inputGates = []

        self.inWHQueue = inWHQueue
        self.outWHQueue = outWHQueue

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
        self.pieces.append(piece.strip('P'))
        self.inWHQueue.put({'conveyour' : conveyour, 'piece' : piece})
    
    #out functions
    def outputPiece(self, piece, outputGate):
        """
        Removes a piece from the warehouse and puts a dictionary containing information about the piece and its output gate into the output queue.

        Parameters:
            piece (str): The piece to be removed from the warehouse.
            outputGate (str): The output gate to which the piece is being sent.

        Returns:
            None
        """
        self.pieces.remove(piece.strip('P'))
        self.outWHQueue.put({'outputGate' : outputGate, 'piece' : piece})
        

class WarehouseUp(Warehouse):
    def __init__(self, ID, outputs, opcuaClient):
        super().__init__(ID, outputs, opcuaClient)

    def spawnPieces(self, pieceType, quantity, gates = [1,2,3,4]):
        piecesByGate = quantity/len(gates)
        self.opcuaClient.spawn(pieceType, piecesByGate, gates)

        spawnGatesStatus = [False]
        
        while not all(spawnGatesStatus):
            for i in range(4):
                spawnGatesStatus[i] = self.opcuaClient.getGateStatus(i+1)

            time.sleep(0.5)

        return piecesByGate
