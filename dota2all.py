#!/usr/bin/env python

# Andy Nguyen
# anguyenhuy@gmail.com

# This file contains function definitions that relate to the 
# aggregation of the entire match database and
# analyses on the entire dataset.

import dota2stats as d2s
import urllib2
import json
import os
import sys
import getopt
import shutil

def sort_all_matches():
    for dir_num in xrange(34):
        if not os.path.exists('./players/all/' + str(dir_num)):
            print 'folder %d not found' % dir_num
            os.makedirs('./players/all/' + str(dir_num))
    file_num = 0
    num_unsorted = len(os.listdir('./players/all/')) - 34
    for match_file in os.listdir('./players/all/'):
        if os.path.isdir('./players/all/' + match_file): continue
        if file_num % 25000 == 0: print '%d out of %d files processed' % (file_num, num_unsorted)
#        print 'Moving file %s to folder %d' % (match_file, int(match_file) / 1000000)
        if not os.path.exists('./players/all/' + str(int(match_file) / 1000000) + '/'):
            print 'folder not found!'
            exit(1)
        shutil.move('./players/all/' + match_file, 
            './players/all/' + str(int(match_file) / 1000000) + '/')
        file_num += 1

# Request entire match history using match_ids instead of start times
# ***WARNING*** This will take a very long time 
def req_all_matches(id_max = None):
    d2s.make_dir('all')
    if not id_max: id_max = 31000000
    if not os.path.exists('./players/all/blank'): os.makedirs('./players/all/blank')
    cached_ids = os.listdir('./players/all/' + str(int(id_max) / 1000000))
    bad_ids = os.listdir('./players/all/blank')
    
    print 'Starting id_max = %d' % (id_max)
    
    for argi in xrange(id_max):
        if str(id_max - argi) in cached_ids: continue
        if str(id_max - argi) in bad_ids: continue
        print 'Requesting match with id = %d...' % (id_max - argi)
        request = urllib2.Request(d2s.match_prefix + 
            "GetMatchDetails/V001/?key=%s&match_id=%s" % (d2s.api_key, id_max - argi))
        bad_id = False
        while True:
            try: 
                opener = urllib2.build_opener()
                result = opener.open(request)
                json_obj = result.read()
                break
            except urllib2.HTTPError, err:
                print str(err)
                if err.code == 401 or err.code == 500:
                    os.system('touch ./players/all/blank/' + str(id_max - argi))
                    bad_id = True
                    break
                else: 
                    print '** Error occurred with id %d, reattemting request... **' % (id_max - argi)
            except Exception as err:
                print str(err)
                print '** Error occurred with id %d, reattemting request... **' % (id_max - argi)
        
        if not bad_id: 
            match_file = open('./players/all/' + str((id_max - argi) / 1000000) + \
                '/' + str(id_max - argi), 'w')
            match_file.write(json_obj + '\n')
            match_file.close()
            result.close()
        cached_ids = os.listdir('./players/all/' + str(int(id_max - argi) / 1000000)) 
        bad_ids = os.listdir('./players/all/blank')
          
# Request the entire match history (around 31 million matches)
# ***WARNING*** This will take a very long time  
def get_all_matches(date_max = None):
    d2s.make_dir('all')
    last_mid = sys.maxint
    match_ids = []
    cached_ids = os.listdir('./players/all/')
    if date_max: last_date = date_max
    elif cached_ids:
        last_file = open('./players/all/' + sorted(cached_ids)[0])
        last_date = json.load(last_file)['result']['starttime']
    else: last_date = 9999999999

    print 'Starting date_max = %d' % (last_date)

    curr_batch = 1
    while True:
        print 'Requesting first batch...' if last_mid == sys.maxint else \
            '\nRequesting batch %d' % (curr_batch)
        request = urllib2.Request(d2s.match_prefix + 
            "GetMatchHistory/V001/?key=%s&date_max=%s" 
            % (d2s.api_key, last_date))
        try:
            opener = urllib2.build_opener()
            result = opener.open(request)
            json_obj = json.load(result)
        except urllib2.URLError, err:
            print str(err)
            continue

        curr_batch += 1
        for match in json_obj['result']['matches']: 
            match_ids.append(match['match_id'])
        last_date = json_obj['result']['matches'][-1]['start_time']
        if not match_ids: return
        last_mid = match_ids[-1]
        
        for m_id in match_ids:
            if str(m_id) in cached_ids: 
                cached_ids.remove(str(m_id))
                continue
            print 'Requesting match with id = %d...' % (m_id)
            request = urllib2.Request(match_prefix + 
                "GetMatchDetails/V001/?key=%s&match_id=%s" % (d2s.api_key, m_id))
            try: 
                opener = urllib2.build_opener()
                result = opener.open(request)
            except urllib2.URLError, err:
                print str(err)
                continue
                
            match_file = open('./players/all/' + str(m_id), 'w')
            match_file.write(result.read() + '\n')
            match_file.close()
            result.close()
        
        cached_ids = os.listdir('./players/all') # updated shared memory for threads
        match_ids = []
        
# Test function to ensure functionality of making API calls
def api_request_test():
    d2s.make_dir('test')
    print 'Test directory created'
    last_mid = sys.maxint
    match_ids = []
    curr_batch = 1
    total_batches = -1
    
    print 'Beginning test...'
    test_start = time.time()
    while curr_batch != total_batches + 1:
        if last_mid == sys.maxint: print 'Requesting first batch...'
        else: print '\nRequesting next batch with last_mid = %d... (%d/%d)' % \
            (last_mid, curr_batch, total_batches)
        request = urllib2.Request(match_prefix + 
            "GetMatchHistory/V001/?key=%s&player_name=oppenheimer&start_at_match_id=%s" 
            % (d2s.api_key, last_mid - 1))
        try:
            opener = urllib2.build_opener()
            result = opener.open(request)
        except Exception as err:
            print str(err)
            continue
        json_obj = json.load(result)
        if curr_batch == 1: 
            total_batches = json_obj['result']['total_results'] / 25 + \
                (1 if json_obj['result']['total_results'] % 25 != 0 else 0)
        curr_batch += 1
        for match in json_obj['result']['matches']: 
            match_ids.append(match['match_id'])
        if not match_ids: break
        last_mid = match_ids[-1]
        
        for m_id in match_ids:
            print 'Requesting match with id = %d...' % (m_id)
            request = urllib2.Request(d2s.match_prefix + 
                "GetMatchDetails/V001/?key=%s&match_id=%s" % (d2s.api_key, m_id))
            try: 
                opener = urllib2.build_opener()
                result = opener.open(request)
                match_file = open('./players/test/' + str(m_id), 'w')
                match_file.write(result.read() + '\n')
                match_file.close()
                result.close()
            except Exception as err:
                print str(err)
                continue
        
        match_ids = []
    test_end = time.time()
    print 'Test completed with a running time of %fs' % (test_end - test_start)
    os.system('rm -r ./players/test/')
    print 'Test directory deleted'
    
if __name__ == '__main__':
    if d2s.api_key == '':
        print 'API KEY REQUIRED'
        exit(1)
    start_id = -1
    date_max = -1
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'd:hi:s', ['date=', 'id=', 'help', 'sort', 'test'])
    except getopt.GetoptError, err:
        print str(err)
        sys.exit(1)
    for opt, arg in opts:
        if opt in ('-d', '--date'): date_max = int(arg)
        elif opt in ('-h', '--help'):
            print 'help'
            exit(0)
        elif opt in ('-i', '--id'): start_id = int(arg)
        elif opt in ('-s', '--sort'): 
            sort_all_matches()
            exit(0)
        elif opt == '--test':
            api_request_test()
            exit(0)
    if (start_id == -1 and date_max == -1) or \
        (start_id != -1 and date_max != -1): exit(1)
    if start_id != -1: req_all_matches(start_id)
    else: get_all_matches(date_max)
    

