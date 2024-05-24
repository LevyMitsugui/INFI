import sys
sys.path.append('C:\\Users\\Levy\\Documents\\GitHub\\INFI\\MES\\OPCUAClient')  # Add the path to the customQueue directory  # Add the path to the customQueue directory
import OPCUAClient
from math import floor
import time

class Gates:
    def __init__(self, gateUpdateQueue, opcuaClient):
        self.gateUpdateQueue = gateUpdateQueue
        self.opcuaClient = opcuaClient
        self.nGates = 4

    def spawnPieces(self, pieceType, quantity):
        piecesByGate = floor(quantity/self.nGates)
        remainder = quantity%self.nGates
        pType = int(pieceType.strip('P'))

        self.gateUpdateQueue.put({'gate': 1, 'piece': pType, 'quantity': piecesByGate + remainder})
        if piecesByGate > 0:
            self.gateUpdateQueue.put({'gate': 2, 'piece': pType, 'quantity': piecesByGate})
            self.gateUpdateQueue.put({'gate': 3, 'piece': pType, 'quantity': piecesByGate})
            self.gateUpdateQueue.put({'gate': 4, 'piece': pType, 'quantity': piecesByGate})

