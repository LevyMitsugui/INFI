import unittest
import Cell
import Machine

class testCell(unittest.TestCase):
    def test_addMachine(self):
        cell = Cell.Cell(1)
        
        cellID = cell.getID()
        self.assert_Equal(cellID, 1)

        machine = Machine.Machine(1, "test")
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