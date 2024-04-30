import unittest
import Cell
import Machine
import sys
sys.path.append('C:\\Users\\Levy\\Documents\\GitHub\\INFI\\MES\\customQueue')  # Add the path to the customQueue directory  # Add the path to the customQueue directory

from customQueue import customQueue

class testCell(unittest.TestCase):
    def test_addMachine(self):
        requestQueue = customQueue()
        cell = Cell.Cell(1, requestQueue, 'recipes.csv')
        
        cellID = cell.getID()
        self.assertEqual(cellID, 1)

        machine = Machine.Machine(1, "M1")
        cell.addMachine(machine)
        self.assertEqual(len(cell.machines), 1)

    def test_setBusy(self):
        requestQueue = customQueue()
        cell = Cell.Cell(1, requestQueue, 'recipes.csv')
        cell.setBusy()
        self.assertTrue(cell.isBusy())

    def test_setFree(self):
        requestQueue = customQueue()
        cell = Cell.Cell(1, requestQueue, 'recipes.csv')
        cell.setBusy()
        cell.setFree()
        self.assertFalse(cell.isBusy())

if __name__ == '__main__':
    unittest.main()