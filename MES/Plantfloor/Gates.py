import sys
sys.path.append('C:\\Users\\Levy\\Documents\\GitHub\\INFI\\MES\\OPCUAClient')  # Add the path to the customQueue directory  # Add the path to the customQueue directory
import OPCUAClient
from math import floor
import time

class Gates:
    def __init__(self, gateUpdateQueue, opcuaClient, database):
        self.gateUpdateQueue = gateUpdateQueue
        self.opcuaClient = opcuaClient
        self.nGates = 4
        self.db = database

    def spawnPieces(self, pieceType, quantity):
        """ pType = int(pieceType.strip('P'))
        self.gateUpdateQueue.put({'gate': 1, 'piece': pType, 'quantity': quantity}) """

        piecesByGate = floor(quantity/self.nGates)
        print(piecesByGate)
        remainder = quantity%self.nGates
        pType = int(pieceType.strip('P'))

        updateGate1 = {'gate': 1, 'piece': pType, 'quantity': piecesByGate + remainder}
        updateGate2 = {'gate': 2, 'piece': pType, 'quantity': piecesByGate}
        updateGate3 = {'gate': 3, 'piece': pType, 'quantity': piecesByGate}
        updateGate4 = {'gate': 4, 'piece': pType, 'quantity': piecesByGate}
        self.gateUpdateQueue.put(updateGate1)
        self.db.insertInQueue("gateUpd", updateGate1, "mes")
        if piecesByGate > 0:
            self.gateUpdateQueue.put(updateGate2)
            self.db.insertInQueue("gateUpd", updateGate2, "mes")
            self.gateUpdateQueue.put(updateGate3)
            self.db.insertInQueue("gateUpd", updateGate3, "mes")
            self.gateUpdateQueue.put(updateGate4)
            self.db.insertInQueue("gateUpd", updateGate4, "mes")

    def waitGateDone(self, gate):
        time.sleep(1)
        while not self.opcuaClient.getSpawnStatus(gate-1):
            #print(self.opcuaClient.getSpawnStatus(gate-1))
            time.sleep(0.5)
        return True
    
    def waitAllGatesDone(self):
        self.waitGateDone(1)
        self.waitGateDone(2)
        self.waitGateDone(3)
        self.waitGateDone(4)