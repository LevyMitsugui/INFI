
import queue
import time

class customQueue(queue.Queue):
    
    def peek(self, block=True, timeout=None, index=0):
        locked = False
        with self.not_empty:
            if not block:
                if not self._qsize():
                    print('empty queue')
            elif timeout is None:
                while not self._qsize():
                    self.not_empty.wait()
                    locked = True
            elif timeout < 0:
                raise ValueError("'timeout' must be a non-negative number")
            else:
                endtime = time() + timeout
                while not self._qsize():
                    remaining = endtime - time()
                    if remaining <= 0.0:
                        print('empty queue')
                    self.not_empty.wait(remaining)
            item = self._peek(index)
            if locked == True:
                self.not_full.notify()
                locked = False
            if item == None:
                return None
            return dict(item)
        
    def _peek(self, index=0):
        #if index is out of bounds
        if index >= len(self.queue) or index < 0:
            return None
        return self.queue[index]

    def orderedPut(self, item):
        #place item in queue ordered by due date
        for i in range(len(self.queue)):
            #if item['DueDate'] < self.queue[i]['DueDate']:
            if item['DueDate'] < self.queue[i]['DueDate']:
                self.queue.insert(i, item)
                break
        else:
            self.queue.append(item)


    def remove(self, item):
        for i in range(len(self.queue)):
            gotten = self.queue.get()
            if(item != gotten):
                self.queue.put(gotten)
            else:
                return gotten