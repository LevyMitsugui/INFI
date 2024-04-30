
import queue
import time
import threading

class customQueue(queue.Queue):
    #def peek(self):
    #    return self.queue[0]
    
    def peek(self, block=True, timeout=None):
        with self.not_empty:
            if not block:
                if not self._qsize():
                    print('empty queue')
            elif timeout is None:
                while not self._qsize():
                    self.not_empty.wait()
            elif timeout < 0:
                raise ValueError("'timeout' must be a non-negative number")
            else:
                endtime = time() + timeout
                while not self._qsize():
                    remaining = endtime - time()
                    if remaining <= 0.0:
                        print('empty queue')
                    self.not_empty.wait(remaining)
            item = self._peek()
            self.not_full.notify()
            return item
        
    def _peek(self):
        return self.queue[0]

    def orderedPut(self, item):
        #place item in queue ordered by due date
        for i in range(len(self.queue)):
            #if item['DueDate'] < self.queue[i]['DueDate']:
            if item['DueDate'] < self.queue[i]['DueDate']:
                self.queue.insert(i, item)
                break
        else:
            self.queue.append(item)

