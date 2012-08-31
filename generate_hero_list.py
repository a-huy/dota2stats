#!/usr/bin/env python

# Andy Nguyen
# anguyenhuy@gmail.com

# This script will generate a file that translates hero codes to 
# proper string names.

# The hero_id of each hero is the line # of the hero's name.
# For example, Anti-Mage is on line 1, and his hero_id is 1.
# Note that when storing the hero list in a data structure, 
# the ADT is (usually) 0-indexed. 

import dota2stats
import urllib2
import json
import sys

def generate_hero_list():
    hero_list = [''] * 108
    request = urllib2.Request(dota2stats.econ_prefix + 
        'GetHeroes/V001/?language=en_us&key=%s' % (dota2stats.api_key))

    # Attempt to download the json data
    try:
        opener = urllib2.build_opener()
        result = opener.open(request)
    except urllib2.URLError, err:
        print str(err)
        sys.exit(1)
    json_obj = json.load(result)

    # Iterate through every hero
    for hero in json_obj['result']['heroes']:
        hero_list[hero['id'] - 1] = str(hero['localized_name'])

    # Write the mappings to file
    outfile = open('herolist', 'w')
    for hero in hero_list:
        outfile.write(hero + '\n')
    outfile.close()
        
if __name__ == '__main__':
    generate_hero_list()
    
