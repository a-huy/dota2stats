#!/usr/bin/env python

# Class definition for serializing JSON data for a player in a match

class Player:
    def __init__(self):
        self.account_id = -1
        self.player_slot = -1
        self.hero_id = -1
        self.item_0 = -1
        self.item_1 = -1
        self.item_2 = -1
        self.item_3 = -1
        self.item_4 = -1
        self.item_5 = -1
        self.kills = -1
        self.deaths = -1
        self.assists = -1
        self.leaver_status = -1
        self.gold = -1
        self.last_hits = -1
        self.denies = -1
        self.gold_per_min = -1
        self.xp_per_min = -1
        self.gold_spent = -1
        self.hero_damage = -1
        self.tower_damage = -1
        self.hero_healing = -1
        self.level = -1
        self.player_name = ''

    def __init__(self, aid, pslot, hid, i0, i1, i2, i3, i4, i5, kills, deaths, assists,
        lstatus, gold, cs, cd, gpm, xpm, gspent, hdam, tdam, hheal, level, name):
        self.account_id = aid
        self.player_slot = pslot
        self.hero_id = hid
        self.item_0 = i0
        self.item_1 = i1
        self.item_2 = i2
        self.item_3 = i3
        self.item_4 = i4
        self.item_5 = i5
        self.kills = kills
        self.deaths = deaths
        self.assists = assists
        self.leaver_status = lstatus
        self.gold = gold
        self.last_hits = cs
        self.denies = cd
        self.gold_per_min = gpm
        self.xp_per_min = xpm
        self.gold_spent = gspent
        self.hero_damage = hdam
        self.tower_damage = tdam
        self.hero_healing = hheal
        self.level = level
        self.player_name = name
