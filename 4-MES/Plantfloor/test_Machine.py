import unittest
import Machine

class testMachine(unittest.TestCase):
    def test_setBusy(self):
        machine = Machine.Machine(1, "test")
        machine.setBusy()
        self.assertTrue(machine.isBusy())

    def test_setFree(self):
        machine = Machine.Machine(1, "test")
        machine.setBusy()
        machine.setFree()
        self.assertFalse(machine.isBusy())

    def test_isBusy(self):
        machine = Machine.Machine(1, "test")
        self.assertFalse(machine.isBusy())

    def test_getID(self):
        machine = Machine.Machine(1, "test")
        self.assertEqual(machine.getID(), 1)

    def test_getType(self):
        machine = Machine.Machine(1, "test")
        self.assertEqual(machine.getType(), "test")
        machine = Machine.Machine(1, 5)
        self.assertEqual(machine.getType(), 5)

if __name__ == '__main__':
    unittest.main()