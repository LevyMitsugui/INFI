import unittest
import Warehouse
import sys
sys.path.append('C:\\Users\\Levy\\Documents\\GitHub\\INFI\\MES\\OPCUAClient')  # Add the path to the customQueue directory  # Add the path to the customQueue directory
sys.path.append('C:\\Users\\Levy\\Documents\\GitHub\\INFI\\MES\\customQueue')
from customQueue import customQueue
from OPCUAClient import OPCUAClient


inWHqueue = customQueue()
outWHqueue = customQueue()
machineUpdateQueue = customQueue()
OPCUAClient = OPCUAClient(inWHqueue, outWHqueue, machineUpdateQueue)
OPCUAClient.opcManager()


wh = Warehouse.Warehouse(1, OPCUAClient, inWHqueue, outWHqueue)

wh.inputPiece('P1', 5)
wh.outputPiece('P1', 1)
#wh.outputPiece('P9', 2)



input()
OPCUAClient.kill()
   