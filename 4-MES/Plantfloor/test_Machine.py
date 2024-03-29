import unittest
import Machine

class testMachine(unittest.TestCase):
    def test_getID(self):
        machine = Machine.Machine(1, 'M1')
        self.assertEqual(machine.getID(), 1)

    def test_getType(self):
        machine = Machine.Machine(1, 'M1')
        self.assertEqual(machine.getType(), 'M1')
        machine = Machine.Machine(1, 'M4')
        self.assertEqual(machine.getType(), 'M4')
        
        with self.assertRaises(ValueError):
            machine = Machine.Machine(1, 'M5')
            machine = Machine.Machine(1, 'M0')
            machine = Machine.Machine(1, '')
            
    def test_setBusy(self):
        machine = Machine.Machine(1, 'M1')
        machine.setBusy()
        self.assertTrue(machine.isBusy())

    def test_setFree(self):
        machine = Machine.Machine(1, 'M1')
        machine.setBusy()
        machine.setFree()
        self.assertFalse(machine.isBusy())

    def test_isBusy(self):
        machine = Machine.Machine(1, 'M1')
        self.assertFalse(machine.isBusy())

    def test_retrieveToolList(self):
        machine = Machine.Machine(1, 'M1')
        self.assertEqual(machine.availableTools, ['T1', 'T2', 'T3'])
        machine = Machine.Machine(1, 'M2')
        self.assertEqual(machine.availableTools, ['T1', 'T2', 'T3'])
        machine = Machine.Machine(1, 'M3')
        self.assertEqual(machine.availableTools, ['T1', 'T4', 'T5'])
        machine = Machine.Machine(1, 'M4')
        self.assertEqual(machine.availableTools, ['T1', 'T4', 'T6'])
    
    def tes_getAvailableTools(self):
        machine = Machine.Machine(1, 'M1')
        self.assertEqual(machine.getAvailableTools(), ['T1', 'T2', 'T3'])
        machine = Machine.Machine(1, 'M2')
        self.assertEqual(machine.getAvailableTools(), ['T1', 'T2', 'T3'])
        machine = Machine.Machine(1, 'M3')
        self.assertEqual(machine.getAvailableTools(), ['T1', 'T4', 'T5'])
        machine = Machine.Machine(1, 'M4')
        self.assertEqual(machine.getAvailableTools(), ['T1', 'T4', 'T6'])

if __name__ == '__main__':
    unittest.main()