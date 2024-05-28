import sys
sys.path.append('C:\\Users\\Levy\\Documents\\GitHub\\INFI\\MES\\OPCUAClient')
import OPCUAClient
from math import floor
import time

class Gates:
    def __init__(self, gateUpdateQueue, opcuaClient, database):
        self.gateUpdateQueue = gateUpdateQueue
        self.opcuaClient = opcuaClient
        self.nGates = 4
        self.db = database
        self.lastGate = 1  # Track the last gate used

    def spawnPieces(self, pieceType, quantity):
        piecesByGate = floor(quantity / self.nGates)
        remainder = quantity % self.nGates
        pType = int(pieceType.strip('P'))

        # Start distributing from the next gate after the last one used
        gate = self.lastGate

        for _ in range(self.nGates):
            quantityForGate = piecesByGate
            if remainder > 0:
                quantityForGate += 1
                remainder -= 1
            
            updateGate = {'gate': gate, 'piece': pType, 'quantity': quantityForGate}
            self.gateUpdateQueue.put(updateGate)
            self.db.insertInQueue("gateUpd", updateGate, "mes")

            # Move to the next gate in sequence
            gate = (gate % self.nGates) + 1

        # Remember the last gate used
        self.lastGate = gate

    def waitGateDone(self, gate):
        time.sleep(1)
        while not self.opcuaClient.getSpawnStatus(gate - 1):
            time.sleep(0.5)
        return True
    
    def waitAllGatesDone(self):
        self.waitGateDone(1)
        self.waitGateDone(2)
        self.waitGateDone(3)
        self.waitGateDone(4)
