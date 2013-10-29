#!/usr/bin/env python

# Andy Nguyen
# anguyenhuy@gmail.com

# This is the main script for caching all match data for a 
# player and performing analyses.

from dota2match import *
from dota2player import *
import getch
import urllib2
import json
import xml.dom.minidom as md
import sys
import getopt
import os
import math
import time

global api_key
global match_prefix
global econ_prefix
global matches

##### API KEY GOES HERE #####
api_key = '' # <-- PUT YOUR API KEY THERE
#############################

# If you need an API key, you can request one here: 
# http://steamcommunity.com/dev/apikey

match_prefix = 'https://api.steampowered.com/IDOTA2Match_570/'
econ_prefix = 'http://api.steampowered.com/IEconDOTA2_570/'
matches = []

# Print help message
def usage():
    print 'Usage: python dota2stats.py [-bmr] [-s batch_size] -n player_name'
    print '\nOptions:'
    print '    -b : Display hero performance stats'
    print '    -h : Show this help message and exit'
    print '    -i : Specify steam name'
    print '         (this will convert it to a player name)'
    print '    -m : Display entire match history'
    print '    -n : Specify player name'
    print '    -r : Download entire match history for the player'
    print '         using the WebAPI'
    print '    -s : Specify the batch size for the match history'
    
# Takes a login name and converts it into a community name
def login_to_community(steam_id):
    try:
        request = urllib2.urlopen('http://steamcommunity.com/id/%s/?xml=1' % (steam_id))
        xml_data = request.read()
        request.close()
    except Exception as err:
        print err
        return
    dom = md.parseString(xml_data)
    a_id = dom.getElementsByTagName('steamID')[0].toxml()
    a_id = a_id.replace('<steamID>', '').replace('</steamID>', '')
    a_id = a_id.replace('<![CDATA[', '').replace(']]>', '').lower()
    print '%s --> %s' % (steam_id, a_id)
    return a_id

# Reads the herolist file and loads the hero_id mappings into a list
def load_hero_list():
    if not os.path.exists('herolist'):
        print 'dota2stats: error: Herolist file could not be found.'
        print '    Please generate the hero list before attempting to read from it.'
        exit(1)
    else:
        hero_list_file = open('herolist', 'r')
        return hero_list_file.readlines()

# Makes a new directory for a player if the folder does not exist
def make_dir(player_name):
    if not os.path.exists('./players/' + player_name): 
        os.makedirs('./players/' + player_name)
        
# Removes a directory for a player, usually because player_name is invalid
# Precondition: player folder must be empty
def rem_dir(player_name):
    if not os.path.exists('./players/' + player_name): return
    os.rmdir('./players/' + player_name)
        
# This method uses the WebAPI to query the entire match history for the player,
# then saves the JSON object for each match in its own file. Files are named 
# by match_id.
def get_matches(player_name):
    last_mid = sys.maxint
    match_ids = []
    cached_ids = os.listdir('./players/' + player_name)
    
    curr_batch = 1
    total_batches = -1
    while curr_batch != total_batches + 1:
        if last_mid == sys.maxint: print 'Requesting first batch...'
        else: print 'Requesting next batch with last_mid = %d... (%d/%d)' % \
            (last_mid, curr_batch, total_batches)
        request = urllib2.Request(match_prefix + 
            "GetMatchHistory/V001/?key=%s&player_name=%s&start_at_match_id=%s" 
            % (api_key, player_name, last_mid - 1))
        try:
            opener = urllib2.build_opener()
            result = opener.open(request)
        except urllib2.URLError, err:
            print str(err)
            continue
            
        json_obj = json.load(result)
        if curr_batch == 1: 
            total_batches = json_obj['result']['total_results'] / 25 + \
                (1 if json_obj['result']['total_results'] % 25 != 0 else 0)
        curr_batch += 1
        for match in json_obj['result']['matches']:
            match_ids.append(match['match_id'])
        if not match_ids:
            print 'dota2stats: error: No matches found for specified player'
            rem_dir(player_name)
            exit(2)
        last_mid = match_ids[-1]
        
        for m_id in match_ids:
            if str(m_id) in cached_ids: 
                cached_ids.remove(str(m_id))
                continue
            print 'Requesting match with id = %d...' % (m_id)
            request = urllib2.Request(match_prefix + 
                "GetMatchDetails/V001/?key=%s&match_id=%s" % (api_key, m_id))
            try: 
                opener = urllib2.build_opener()
                result = opener.open(request)
            except urllib2.URLError, err:
                print str(err)
                continue
            
            match_file = open('./players/' + player_name + '/' + str(m_id), 'w')
            match_file.write(result.read() + '\n')
            match_file.close()
            result.close()
        
        match_ids = []
        
# Deserializes Matchmaking games
# Note: this function will only deserialize matchmaking games, as 
# most (if not all) stats only consider MM games
def load_matches(player_name):
    if not os.path.exists('./players/' + player_name): 
        print 'dota2stats: error: No folder for player \'%s\'' % (player_name)
        return
    if len(os.listdir('./players/' + player_name)) == 0:
        print 'dota2stats: No matches cached in player folder'
        print 'Attempting aggregation of match history...'
        get_matches(player_name)
    print 'Deserializing matches...'
    for m_id in os.listdir('./players/' + player_name):
        curr_match_players = []
        m_file = open('./players/' + player_name + '/' + m_id)
        json_obj = json.load(m_file)
        if json_obj['result']['lobby_type'] != 0: continue
        for player in json_obj['result']['players']:
            curr_match_players.append(Player(player['account_id'], player['player_slot'],
                player['hero_id'], player['item_0'], player['item_1'], player['item_2'],
                player['item_3'], player['item_4'], player['item_5'], player['kills'], 
                player['deaths'], player['assists'], player['leaver_status'], 
                player['gold'], player['last_hits'], player['denies'],
                player['gold_per_min'], player['xp_per_min'], player['gold_spent'], 
                player['hero_damage'], player['tower_damage'], player['hero_healing'], 
                player['level'], player['player_name']))
        matches.append(Match(json_obj['result']['season'], 
            json_obj['result']['radiant_win'], json_obj['result']['duration'], 
            json_obj['result']['match_id'], json_obj['result']['starttime'], 
            json_obj['result']['tower_status_radiant'], json_obj['result']['tower_status_dire'],
            json_obj['result']['barracks_status_radiant'], 
            json_obj['result']['barracks_status_dire'], 
            json_obj['result']['cluster'], json_obj['result']['first_blood_time'],
            json_obj['result']['replay_salt'], json_obj['result']['lobby_type'], 
            json_obj['result']['human_players'], json_obj['result']['leagueid'], 
            curr_match_players))

# This will generate the metadata file found in a player's folder
def stats_by_hero(player_name):
    if not os.path.exists('./players/' + player_name):
        print 'dota2stats: error: No folder for player \'%s\'' % (player_name)
        return
    if not matches:
        load_matches(player_name)
    hero_stats = []
    for argi in xrange(108): 
        hero_stats.append({key: 0 for key in ['count', 'wins', 'kills', 
            'assists', 'deaths', 'gpm']})
        hero_stats[argi]['hero_id'] = argi
    for match in matches:
        for player in match.players:
            if player.player_name.lower() == player_name:
                if (match.radiant_win and player.player_slot < 10) or \
                    (not match.radiant_win and player.player_slot > 10):
                    hero_stats[player.hero_id]['wins'] = \
                        hero_stats[player.hero_id].get('wins', 0) + 1
                hero_stats[player.hero_id]['count'] = \
                    hero_stats[player.hero_id].get('count', 0) + 1
                hero_stats[player.hero_id]['kills'] = \
                    hero_stats[player.hero_id].get('kills', 0) + player.kills
                hero_stats[player.hero_id]['assists'] = \
                    hero_stats[player.hero_id].get('assists', 0) + player.assists
                hero_stats[player.hero_id]['deaths'] = \
                    hero_stats[player.hero_id].get('deaths', 0) + player.deaths
                hero_stats[player.hero_id]['gpm'] = \
                    hero_stats[player.hero_id].get('gpm', 0) + player.gold_per_min
    hero_list = load_hero_list()
    hero_stats = sorted(hero_stats, key=lambda k: k['count'], reverse=True)
    print '\n', 'Hero'.ljust(20), 'Games'.ljust(6), 'K/D'.ljust(5), '(K+A)/D'.ljust(8), \
        'Avg GPM'.ljust(8), 'Wins'.ljust(5), 'Losses'.ljust(7), 'Win Rate'.ljust(9)
    print '-' * 80
    for index in xrange(108):
        if hero_stats[index]['count'] != 0:
            print (hero_list[hero_stats[index]['hero_id'] - 1].strip()).ljust(20), \
                str(hero_stats[index]['count']).ljust(6), \
                str(round(float(hero_stats[index]['kills']) / \
                    float(hero_stats[index]['deaths']), 2)).ljust(5) if \
                    hero_stats[index]['deaths'] != 0 else 'inf'.ljust(5), \
                str(round(float((hero_stats[index]['kills'] + hero_stats[index]['assists'])) / \
                    float(hero_stats[index]['deaths']), 2)).ljust(8) if \
                    hero_stats[index]['deaths'] != 0 else 'inf'.ljust(8), \
                str(round(float(hero_stats[index]['gpm']) / \
                    float(hero_stats[index]['count']), 2)).ljust(8), \
                str(hero_stats[index]['wins']).ljust(5), \
                str(hero_stats[index]['count'] - hero_stats[index]['wins']).ljust(7), \
                (str(round(float(hero_stats[index]['wins']) / \
                    float(hero_stats[index]['count']), 4) * 100) + '%').ljust(9)
    print '\n', 'Total games: %d' % (len(matches))
    print 'Press any key to continue...'
    getch.getch()

# Displays a player's match history  
def match_history(player_name, matches_per_batch):
    if not os.path.exists('./players/' + player_name):
        print 'dota2stats: error: No folder for player \'%s\'' % (player_name)
        return
    if not matches: load_matches(player_name)
    hero_list = load_hero_list()
    curr_batch = 0
    show_next_batch = True
    while curr_batch < math.ceil(float(len(matches)) / float(matches_per_batch)) and show_next_batch:
        if os.name == 'nt': os.system('cls')
        else: os.system('clear')
        print '\n', 'Match ID'.center(9), 'Hero'.center(20), 'Game Length'.center(12), \
            'Kills'.center(6), 'Deaths'.center(7), 'Assists'.center(8), 'GPM'.center(4), \
            'W/L'.center(4)
        print '-' * 80
        l_bound = curr_batch * matches_per_batch 
        u_bound = (curr_batch + 1) * matches_per_batch
        for match in sorted(matches, key=lambda k: k.match_id, reverse=True)[l_bound:u_bound]:
            for player in match.players:
                if player.player_name.lower() == player_name:
                    print str(match.match_id).center(9), \
                        hero_list[player.hero_id - 1].strip().center(20), \
                        (str(match.duration / 60).zfill(2) + ':' + \
                            str(match.duration % 60).zfill(2)).center(12), \
                        str(player.kills).center(6), \
                        str(player.deaths).center(7), str(player.assists).center(8), \
                        str(player.gold_per_min).center(4), \
                        '+'.center(4) if (match.radiant_win and player.player_slot < 10) or \
                        (not match.radiant_win and player.player_slot > 10) else '-'.center(4)
        print 'Showing %d to %d of %d matches' % \
            (l_bound + 1, u_bound if u_bound < len(matches) else len(matches), len(matches))
        print 'Up/Right: next batch; Down/Left: previous batch; Any Other Key: exit'
        key = getch.getch()
        if os.name == 'nt':
            if key == '\xe0P' or key == '\xe0M': curr_batch += 1
            elif key == '\xe0H' or key == '\xe0K':
                if curr_batch > 0: curr_batch -=1
            else: show_next_batch = False
        else:
            if key == '\x1b[B' or key == '\x1b[C': curr_batch += 1
            elif key == '\x1b[A' or key == '\x1b[D': 
                if curr_batch > 0: curr_batch -= 1
            else: show_next_batch = False
    
# "Main" function for the script
if __name__ == '__main__':
    if api_key == '':
        print 'API KEY REQUIRED'
        exit(1)
    player_name = ''
    account_id = ''
    request_history = False
    show_match_history = False
    show_hero_stats = False
    matches_per_batch = 25
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'bhi:mn:rs:', ['name='])
    except getopt.GetoptError, err:
        print str(err)
        sys.exit(1)
    for opt, arg in opts:
        if opt == '-b': show_hero_stats = True
        elif opt == '-h':
            usage()
            exit(0)
        elif opt == '-i': player_name = login_to_community(arg.lower())
        elif opt == '-m': show_match_history = True
        elif opt in ('-n', '--name'): player_name = arg.lower()
        elif opt == '-r': request_history = True
        elif opt == '-s': matches_per_batch = int(arg)
    if player_name != '': 
        make_dir(player_name)
        if request_history: get_matches(player_name)
        load_hero_list()
        if show_hero_stats: stats_by_hero(player_name)
        if show_match_history: match_history(player_name, matches_per_batch)
    else:
        print 'dota2stats: error: A player name must be specified'
        usage()
        sys.exit(1)
         
