#!/usr/bin/env python

# Class definition for serializing JSON data for a match

class Match:
    def __init__(self):
        self.season = -1
        self.radiant_win = False
        self.duration = -1
        self.match_id = -1
        self.starttime = -1
        self.tower_status_radiant = -1
        self.tower_status_dire = -1
        self.barracks_status_radiant = -1
        self.barracks_status_dire = -1
        self.cluster = -1
        self.first_blood_time = -1
        self.replay_salt = -1
        self.lobby_type = -1
        self.human_players = -1
        self.leagueid = -1
        self.players = []
      
    def __init__(self, season, rw, duration, mid, stime, tsr, tsd, bsr, bsd, cluster,
        fbt, rs, lt, num_hp, lid, players):
        self.season = season
        self.radiant_win = rw
        self.duration = duration
        self.match_id = mid
        self.starttime = stime
        self.tower_status_radiant = tsr
        self.tower_status_dire = tsd
        self.barracks_status_radiant = bsr
        self.barracks_status_dire = bsd
        self.cluster = cluster
        self.first_blood_time = fbt
        self.replay_salt = rs
        self.lobby_type = lt
        self.human_players = num_hp
        self.leagueid = lid
        self.players = players
