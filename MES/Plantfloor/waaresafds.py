import unittest
import Warehouse
import Gates
import sys
sys.path.append('C:\\Users\\Levy\\Documents\\GitHub\\INFI\\MES\\OPCUAClient')  # Add the path to the customQueue directory  # Add the path to the customQueue directory
sys.path.append('C:\\Users\\Levy\\Documents\\GitHub\\INFI\\MES\\customQueue')
from customQueue import customQueue
from OPCUAClient import OPCUAClient


inWHqueue = customQueue()
outWHqueue = customQueue()
machineUpdateQueue = customQueue()
gateUpdateQueue = customQueue()
OPCUAClient = OPCUAClient(inWHqueue, outWHqueue, machineUpdateQueue, gateUpdateQueue)
OPCUAClient.opcManager()


wh = Warehouse.Warehouse(1, OPCUAClient, inWHqueue, outWHqueue)
#gt = Gates.Gates(gateUpdateQueue, OPCUAClient)

#wh.inputPiece('P1', 5)
wh.outputPiece('P1', 1)
#gt.spawnPieces('P1', 1)



input()
OPCUAClient.kill()
   