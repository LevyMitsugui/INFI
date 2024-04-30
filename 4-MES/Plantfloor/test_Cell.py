import unittest
import Cell
import Machine
import sys
sys.path.append('path_to_customQueue_directory')  # Add the path to the customQueue directory

from customQueue.customQueue import customQueue

class testCell(unittest.TestCase):
    def test_addMachine(self):
        requestQueue = customQueue.customQueue()
        cell = Cell.Cell(1, requestQueue, './Recipes/recipes.csv')
        
        cellID = cell.getID()
        self.assertEqual(cellID, 1)

        machine = Machine.Machine(1, "M1")
        cell.addMachine(machine)
        self.assertEqual(len(cell.machines), 1)

    def test_setBusy(self):
        cell = Cell.Cell(1)
        cell.setBusy()
        self.assertTrue(cell.isBusy())

    def test_setFree(self):
        cell = Cell.Cell(1)
        cell.setBusy()
        cell.setFree()
        self.assertFalse(cell.isBusy())

if __name__ == '__main__':
    unittest.main()