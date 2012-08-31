import threading
import json
import os
import sys

# Like thread_stats.py, this script creates multiple threads to request the 
# entire match history in an asynchronous fashion.
# Uses the date_max upper bound method. 

class DotA2StatsThread(threading.Thread):
    def __init__(self, date_max):
        self.date_max = date_max
        threading.Thread.__init__(self)
        
    def run(self):
        os.system('python dota2all.py -d' + str(self.date_max))

if __name__ == '__main__':
    start_times = []
    num_threads = int(sys.argv[1])
    most_recent_match = sorted(os.listdir('./players/all/'), key=lambda x: int(x))[-1]
    match_file = open('./players/all/' + most_recent_match)
    json_obj = json.load(match_file)
    date_max = int(json_obj['result']['starttime'])
    part_amt = (date_max - 1314000000) / num_threads
    start_times.append(9999999999)
    
    for argi in xrange(num_threads):
        if argi == 0: continue
        start_times.append(part_amt * argi + 1314000000)
    
    for time in start_times:
        DotA2StatsThread(time).start()
        
