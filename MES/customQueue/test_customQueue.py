import queue
import customQueue
import unittest


class testQueue(unittest.TestCase):
    def test_peek(self):
        order1 = {'clientID' : 'Client AA', 'Order Number' : 18, 'WorkPiece' : 'P5', 'Quantity' : 8, 'DueDate' : 7, 'LatePen' : 10, 'EarlyPen' : 5}
        order2 = {'clientID' : 'Client AA', 'Order Number' : 19, 'WorkPiece' : 'P5', 'Quantity' : 8, 'DueDate' : 8, 'LatePen' : 10, 'EarlyPen' : 5}
        order3 = {'clientID' : 'Client AA', 'Order Number' : 20, 'WorkPiece' : 'P5', 'Quantity' : 8, 'DueDate' : 9, 'LatePen' : 10, 'EarlyPen' : 5}
        q = customQueue.customQueue()
        q.put(order1)
        q.put(order2)
        q.put(order3)
        self.assertEqual(q.peek()['DueDate'], 7)
        self.assertEqual(q.get()['DueDate'], 7)
        self.assertEqual(q.peek()['DueDate'], 8)
        self.assertEqual(q.get()['DueDate'], 8)
        self.assertEqual(q.peek()['DueDate'], 9)
        self.assertEqual(q.get()['DueDate'], 9)

    def test_orederedPut(self):
        q = customQueue.customQueue()
        order1 = {'clientID' : 'Client AA', 'Order Number' : 18, 'WorkPiece' : 'P5', 'Quantity' : 8, 'DueDate' : 7, 'LatePen' : 10, 'EarlyPen' : 5}
        order2 = {'clientID' : 'Client AA', 'Order Number' : 19, 'WorkPiece' : 'P5', 'Quantity' : 8, 'DueDate' : 8, 'LatePen' : 10, 'EarlyPen' : 5}
        order3 = {'clientID' : 'Client AA', 'Order Number' : 20, 'WorkPiece' : 'P5', 'Quantity' : 8, 'DueDate' : 9, 'LatePen' : 10, 'EarlyPen' : 5}
        q.orderedPut(order3) #orders inserted "backwards"
        q.orderedPut(order2)
        q.orderedPut(order1)
        self.assertEqual(q.get()['DueDate'], 7)
        self.assertEqual(q.get()['DueDate'], 8)
        self.assertEqual(q.get()['DueDate'], 9)

        q.orderedPut(order3)
        q.orderedPut(order2)
        q.orderedPut(order1)
        #here order is 7, 8 and 9 . 7 will be popped first
        self.assertIsNot(q.get()['DueDate'], 8)
        #here order is 8 and 9 . 8 will be popped
        self.assertIsNot(q.get()['DueDate'], 9)
        #here order is 9 . Finally 9 will be popped
        self.assertEqual(q.get()['DueDate'], 9)

if __name__ == '__main__':
    unittest.main()