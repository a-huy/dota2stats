import threading
import json
import os
import sys

# Like thread_stats.py, this script creates multiple threads to request the 
# entire match history in an asynchronous fashion.
# Uses the linear search method.

class DotA2StatsThread(threading.Thread):
    def __init__(self, date_max):
        self.date_max = date_max
        threading.Thread.__init__(self)
        
    def run(self):
        os.system('python dota2all.py -i' + str(self.date_max))

if __name__ == '__main__':
    start_times = []
    num_threads = int(sys.argv[1])
    id_max = int(sys.argv[2])
    part_amt = 1000000 / num_threads
    
    for argi in xrange(num_threads):
        #if argi == 0: continue
        start_times.append(id_max - part_amt * argi)
    
    for time in start_times:
        DotA2StatsThread(time).start()
        
