import unittest
import Cell
import Machine
import sys
import csv
import os

sys.path.append('C:\\Users\\Levy\\Documents\\GitHub\\INFI\\MES\\customQueue')  # Add the path to the customQueue directory  # Add the path to the customQueue directory
sys.path.append('C:\\Users\\Levy\\Documents\\GitHub\\INFI\\MES\\Plantfloor')  # Add the path to the customQueue directory  # Add the path to the customQueue directory
sys.path.append('C:\\Users\\Levy\\Documents\\GitHub\\INFI\\MES\\OPCUAClient')  # Add the path to the customQueue directory  # Add the path to the customQueue directory

import OPCUAClient
from customQueue import customQueue

class testCell(unittest.TestCase):
    def test_addMachine(self):
        requestQueue = customQueue()
        doneRequestQueue = customQueue()
        myopcuaclient = OPCUAClient.OPCUAClient()
        recipe = __csvReader__('../Recipe/recipes.csv')
        cell = Cell.Cell(1, requestQueue, doneRequestQueue, recipes=recipe)
        
        cellID = cell.getID()
        self.assertEqual(cellID, 1)

        machine = Machine.Machine(1, "M1", myopcuaclient)
        cell.addMachine(machine)
        self.assertEqual(len(cell.machines), 1)


    def test_arrangeSteps(self):
        requestQueue = customQueue()
        doneRequestQueue = customQueue()
        myopcuaclient = OPCUAClient.OPCUAClient()
        recipe = __csvReader__('../Recipe/recipes.csv')
        cell = Cell.Cell(1, requestQueue, doneRequestQueue, recipes=recipe)

        machine0 = Machine.Machine(1, "M1", myopcuaclient)
        machine1 = Machine.Machine(2, "M2", myopcuaclient)

        cell.addMachine(machine0)
        cell.addMachine(machine1)

        recipe = {'Piece': 'P6', 'Material': 'P1', 'Time': '45;15;25', 'Tools': 'T1;T2;T2'}
        steps = cell.__arrangeSteps__(recipe)
        self.assertEqual(len(steps), 3)
        self.assertEqual(steps[0], (0,1,45))
        self.assertEqual(steps[1], (1,2,15))
        self.assertEqual(steps[2], (1,2,25))
        recipe = {'Piece': 'P7', 'Material': 'P1', 'Time': '45;15;15', 'Tools': 'T1;T2;T3'}
        steps = cell.__arrangeSteps__(recipe)
        self.assertEqual(len(steps), 3)
        self.assertEqual(steps[0], (0,1,45))
        self.assertEqual(steps[1], (1,2,15))
        self.assertEqual(steps[2], (1,3,15))
        recipe = {'Piece': 'P9', 'Material': 'P2', 'Time': '45;45', 'Tools': 'T1;T5'}
        steps = cell.__arrangeSteps__(recipe)
        self.assertEqual(len(steps), 2)
        self.assertEqual(steps[0], (0,1,45))
        self.assertEqual(steps[1], (1,5,45))

    def test_removeDoneSteps(self):
        requestQueue = customQueue()
        doneRequestQueue = customQueue()
        myopcuaclient = OPCUAClient.OPCUAClient()
        recipe = __csvReader__('../Recipe/recipes.csv')
        cell = Cell.Cell(1, requestQueue, doneRequestQueue, recipes=recipe)

        machine0 = Machine.Machine(1, "M1", myopcuaclient)
        machine1 = Machine.Machine(2, "M2", myopcuaclient)

        cell.addMachine(machine0)
        cell.addMachine(machine1)

        stepsList = []
        
        recipe = {'Piece': 'P6', 'Material': 'P1', 'Time': '45;15;25', 'Tools': 'T1;T2;T2'}
        steps1 = cell.__arrangeSteps__(recipe)
        self.assertEqual(len(steps1), 3)
        self.assertEqual(steps1[0], (0,1,45))

        recipe = {'Piece': 'P7', 'Material': 'P1', 'Time': '45;15;15', 'Tools': 'T1;T2;T3'}
        steps2 = cell.__arrangeSteps__(recipe)
        self.assertEqual(len(steps2), 3)
        self.assertEqual(steps2[0], (0,1,45))
        
        stepsList.append(steps1)
        stepsList.append(steps2)

        self.assertEqual(len(stepsList), 2)
        self.assertEqual(stepsList[0], steps1)
        self.assertEqual(stepsList[1], steps2)

        steps0 = cell.__removeDoneSteps__(0, stepsList)
        self.assertNotEqual(stepsList[0], [(0,1,45), (1,2,15), (1,2,25)])
        self.assertEqual(stepsList[0], [(1,2,15), (1,2,25)])
        self.assertNotEqual(stepsList[1], [(0,1,45), (1,2,15), (1,3,15)])
        self.assertEqual(stepsList[1], [(1,2,15), (1,3,15)])

def __csvReader__(filename):
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct the full path to the file
    file_path = os.path.join(current_dir, filename)
    
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        return [row for row in reader]
    
if __name__ == '__main__':
    unittest.main()