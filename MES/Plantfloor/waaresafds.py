import unittest
import Warehouse
import Gates
import sys
import time

sys.path.append('C:\\Users\\Levy\\Documents\\GitHub\\INFI\\MES\\OPCUAClient')  # Add the path to the customQueue directory  # Add the path to the customQueue directory
sys.path.append('C:\\Users\\Levy\\Documents\\GitHub\\INFI\\MES\\customQueue')
sys.path.append('C:\\Users\\Levy\\Documents\\GitHub\\INFI\\Database')
from customQueue import customQueue
from OPCUAClient import OPCUAClient
from Database import Database

database = Database("root", "admin")

inWHqueue = customQueue()
outWHqueue = customQueue()
machineUpdateQueue = customQueue()
gateUpdateQueue = customQueue()
OPCUAClient = OPCUAClient(inWHqueue, outWHqueue, machineUpdateQueue, gateUpdateQueue, database)
OPCUAClient.opcManager()


wh0  = Warehouse.Warehouse(0, OPCUAClient, inWHqueue, outWHqueue, database)
wh1 = Warehouse.Warehouse(1, OPCUAClient, inWHqueue, outWHqueue, database)
gt = Gates.Gates(gateUpdateQueue, OPCUAClient, database)

#wh.inputPiece('P1', 5)
#wh.outputPiece('P1', 1)

""" wh1.outputPiece('P9', 0)
while OPCUAClient.getTransferCellStatusEdge() in ['None', 'Fall']:
    time.sleep(1)
print('bruh')
wh0.inputPiece('P9', 0)

wh1.outputPiece('P9', 0)
while OPCUAClient.getTransferCellStatusEdge() in ['None', 'Fall']:
    time.sleep(1)
print('bruh')
wh0.inputPiece('P9', 0)

wh1.outputPiece('P9', 0)
while OPCUAClient.getTransferCellStatusEdge() in ['None', 'Fall']:
    time.sleep(1)
print('bruh')
wh0.inputPiece('P9', 0) """

""" wh1.outputPiece('P9', 7)
time.sleep(2) """


gt.spawnPieces('P2', 8)
#gt.waitAllGatesDone()
#gt.spawnPieces('P2', 17)



input()
OPCUAClient.kill()
   