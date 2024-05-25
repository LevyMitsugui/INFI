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
GateUpdateQueue = customQueue()
OPCUAClient = OPCUAClient(inWHqueue, outWHqueue, machineUpdateQueue, GateUpdateQueue)
OPCUAClient.opcManager()
class TestWarehouse(unittest.TestCase):

    def test_getID(self):
        warehouse = Warehouse.Warehouse(1, OPCUAClient, inWHqueue, outWHqueue)
        self.assertEqual(warehouse.getID(), 1)
        

    def test_getStock(self):
        wh = Warehouse.Warehouse(1, OPCUAClient, inWHqueue, outWHqueue)
        self.assertEqual(wh.getID(), 1)
        
        self.assertEqual(wh.getStock(), [10,0,0,0,0,0,0,0,0])

    def test_inputPiece(self):
        wh = Warehouse.Warehouse(1, OPCUAClient, inWHqueue, outWHqueue)
        self.assertEqual(wh.getID(), 1)
        
        wh.inputPiece('P1', 1)
        self.assertEqual(wh.getStock(), [11,0,0,0,0,0,0,0,0])
        self.assertEqual(inWHqueue.qsize(), 1)
        wh.inputPiece('P9', 2)
        self.assertEqual(wh.getStock(), [11,0,0,0,0,0,0,0,1])
        self.assertEqual(inWHqueue.qsize(), 2)

        inWHqueue.get()
        self.assertEqual(inWHqueue.qsize(), 1)
        inWHqueue.get()
        self.assertEqual(inWHqueue.qsize(), 0)

    def test_outputPiece(self):
        wh = Warehouse.Warehouse(1, OPCUAClient, inWHqueue, outWHqueue)
        self.assertEqual(wh.getID(), 1)


        wh.inputPiece('P9', 2)
        self.assertEqual(wh.getStock(), [10,0,0,0,0,0,0,0,1])
        self.assertEqual(inWHqueue.qsize(), 1)

        wh.outputPiece('P1', 1)
        self.assertEqual(wh.getStock(), [9,0,0,0,0,0,0,0,1])
        self.assertEqual(outWHqueue.qsize(), 1)
        wh.outputPiece('P9', 2)
        self.assertEqual(wh.getStock(), [9,0,0,0,0,0,0,0,0])
        self.assertEqual(outWHqueue.qsize(), 2)

    def test_END(self):
        OPCUAClient.kill()

if __name__ == '__main__':
    unittest.main()
    