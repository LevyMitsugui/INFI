from Plantfloor import *
from Recipe.Recipe import *
import threading
import time
import queue

class newQueue(queue.Queue):
    def peek(self):
        return self.queue[0]

buffer = [['P5', 'P9'], "uma info", "outra info", 0]
myQueue = newQueue()
myQueue.put(buffer)


class Manager():
    def __printRecipes(self, queue):   
        myRecipe = Recipe()
        lastCount = -1
        while True:
            time.sleep(0.5)
            if queue.qsize() > 0 and queue.peek()[3] != lastCount: 
                buff = queue.peek()
                lastCount = buff[3]
                print(buff[0])
                for r in buff[0]:
                    print(myRecipe.getRecipes(r))

    def __counter(self, queue):
        buff = queue.get()
        
        while True:
            time.sleep(1)
            print("\ncounter: ", buff[3], "  queue size: ", queue.qsize())
            buff[3] = buff[3] + 1
            queue.queue.clear()
            queue.put(buff)

    def __print(self, queue):
        while True:
            time.sleep(2)
            
            print(queue.get())
        
    
    def printRecipes(self, queue):
        threading.Thread(target=self.__printRecipes, daemon=True, args=(queue,)).start()

    def counter(self):
        threading.Thread(target=self.__counter, daemon=True,args=(myQueue,)).start()

    def print(self, queue):
        threading.Thread(target=self.__print, daemon=True, args=(queue,)).start()




manager = Manager()
manager.printRecipes(myQueue)
manager.counter()
manager.print(myQueue)

Input = input("press enter to stop")