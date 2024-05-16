from OPCUAClient import OPCUAClient
import time

class Warehouse:
    def __init__(self, ID, outputs, opcuaClient):
        self.opcuaClient = opcuaClient
        self.ID = ID
        self.pieces = []
        self.inputGates = []

    def addPiece(self, Piece):
        pieces = self.opcuaClient.getWH1Pieces(self.ID)
        self.pieces.append(Piece)

    def getStock(self):
        return self.pieces
    
    def Output(self, piece, outputGate):
        self.opcuaClient
        

class Warehouse1(Warehouse):
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
