import unittest
import Gates
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

class TestGates(unittest.TestCase):

    def test_spawnPieces(self):
        gates = Gates.Gates(GateUpdateQueue, OPCUAClient)
        gates.spawnPieces('P1', 10)
        self.assertEqual(GateUpdateQueue.qsize(), 4)

        self.assertEqual(GateUpdateQueue.get(), {'gate': 1, 'piece': 1, 'quantity': 4})
        self.assertEqual(GateUpdateQueue.get(), {'gate': 2, 'piece': 1, 'quantity': 2})
        self.assertEqual(GateUpdateQueue.get(), {'gate': 3, 'piece': 1, 'quantity': 2})
        self.assertEqual(GateUpdateQueue.get(), {'gate': 4, 'piece': 1, 'quantity': 2})

    def test_END(self):
        OPCUAClient.kill()

if __name__ == '__main__':
    unittest.main()