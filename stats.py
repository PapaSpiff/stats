from pstats import StatsProfile
import sys
import json
import os
import glob
from wave import Wave
from special import Special
from weapon import Weapon
from bosslist import SalmonBossList
from gamesession import GameSession
from htmlgen import print_html_head
from htmlgen import print_specials_html, print_weapons_html, print_waves_html
from datetime import datetime
from os.path import exists
from statistics import mean as mean
from statistics import pstdev as pstdev
from statistics import quantiles as quantiles
import urllib.request
import time
from time import strftime
import argparse
from io import StringIO

# job_id <num>
# my_result -> help_count
#              dead_count
#              golden_ikura_num
#              boss_kill_counts -> 
# boss_counts -> '<num>' -> count
#                        -> boss -> name
#                                -> key
# job_score <num>
# danger_rate <num>
# other_results [ array of ]
# kuma_point - <num>
# play_time - <num> (epoch)
# job_result -> failure_reason
#               failure_wave
#               is_clear (bool)
# grade_point - <num>
# grade_point_delta - <num>
# start_time - <num> (epoch)
# grade -> short_name
#          name
#          id
#          long_name
# end_time - <num> (epoch)
# job_rate - <num>
# wave_details 
# player_type
# schedule

            # ['goldie',     3, 'sakelien-golden'],
            # ['steelhead',  6, 'sakelien-bomber'],
            # ['flyfish',    9, 'sakelien-cup-twins'],
            # ['scrapper',  12, 'sakelien-shield'],
            # ['steel_eel', 13, 'sakelien-snake'],
            # ['stinger',   14, 'sakelien-tower'],
            # ['maws',      15, 'sakediver'],
            # ['griller',   16, 'sakedozer'],
            # ['drizzler',  21, 'sakerocket'],


class Game:
    def __str__(self):
        return  'Rotation start: ' + str(datetime.fromtimestamp(self.start_time))\
            + '\nRotation end  : ' + str(datetime.fromtimestamp(self.end_time))\
            + '\nGame time     : ' + str(datetime.fromtimestamp(self.play_time))\
            + '\nScore         : ' + str(self.score)\
            + '\nBoss List     : ' + str(self.boss_list)\
            + '\nBoss Kills    : ' + str(self.boss_kill)\
            + '\nFilename      : ' + str(self.fname)
 
    def process_game(self):
        if not "job_id" in self.data:
            print(f"Error in {self.fname}, {self.data['message']}")
            # set fake times
            self.play_time = 0
            return self
        self.job_id        = self.data['job_id']
        self.score         = self.data['job_score']
        self.start_time    = self.data['start_time']
        self.play_time     = self.data['play_time']
        self.end_time      = self.data['end_time']
        blist              = SalmonBossList(self.data['boss_counts'], self.fname)
        self.boss_list     = blist
        self.boss_tot_num  = blist.sum_boss()
        blist              = SalmonBossList(self.data['my_result']['boss_kill_counts'], self.fname)
        self.boss_kill     = blist
        self.boss_kill_num = blist.sum_boss()
        self.special       = Special(self.data['my_result']['special']['id'])
        self.special_usage = 0
        if 'special_counts' in self.data['my_result']:
            self.special_usage = sum(self.data['my_result']['special_counts'])
        self.weapon_list   = []
        for weapon in self.data['my_result']['weapon_list']:
            self.weapon_list.append(Weapon(weapon['id']))
        self.boss_k_team   = []
        self.players       = []
        self.boss_tkill_n  = 0
        for other_players in self.data['other_results']:
            player_bkill = SalmonBossList(other_players['boss_kill_counts'], self.fname)
            self.boss_k_team.append(player_bkill)
            self.boss_tkill_n += player_bkill.sum_boss()
            self.players.append({"name" : other_players['name'], "player_id" : other_players['pid']})
        self.danger_rate   = self.data['danger_rate']
        self.passed        = self.data['job_result']['is_clear']
        self.wavespassed   = 3 if self.passed else self.data['job_result']['failure_wave'] - 1
        self.wavesplayed   = 3 if self.passed else self.data['job_result']['failure_wave']
        self.waves_ht      = 0
        self.waves_nt      = 0
        self.waves_lt      = 0
        self.waves_day     = 0
        self.waves_night   = 0
        self.event_moship  = 0
        self.event_rush    = 0
        self.event_grills  = 0
        self.event_seeking = 0
        self.event_fog     = 0
        self.event_cohock  = 0
        self.waves_eggsgen = 0
        self.waves_eggs    = 0
        self.waves_powregg = 0
        self.ht_seek       = 0
        self.nt_seek       = 0
        self.ht_rush       = 0
        self.nt_rush       = 0
        self.ht_grills     = 0
        self.nt_grills     = 0
        self.ht_moship     = 0
        self.nt_moship     = 0
        self.lt_moship     = 0
        self.ht_fog        = 0
        self.nt_fog        = 0
        self.lt_fog        = 0
        self.night_geggs   = []
        self.night_peggs   = []
        self.day_geggs     = []
        self.day_peggs     = []
        self.ht_geggs      = []
        self.ht_peggs      = []
        self.nt_geggs      = []
        self.nt_peggs      = []
        self.lt_geggs      = []
        self.lt_peggs      = []
        self.ht_seek_g     = []
        self.nt_seek_g     = []
        self.ht_rush_g     = []
        self.nt_rush_g     = []
        self.ht_grills_g   = []
        self.nt_grills_g   = []
        self.ht_moship_g   = []
        self.nt_moship_g   = []
        self.lt_moship_g   = []
        self.ht_fog_g      = []
        self.nt_fog_g      = []
        self.lt_fog_g      = []
        self.lt_cohock_g   = []
        self.ht_seek_p     = []
        self.nt_seek_p     = []
        self.ht_rush_p     = []
        self.nt_rush_p     = []
        self.ht_grills_p   = []
        self.nt_grills_p   = []
        self.ht_moship_p   = []
        self.nt_moship_p   = []
        self.lt_moship_p   = []
        self.ht_fog_p      = []
        self.nt_fog_p      = []
        self.lt_fog_p      = []
        self.lt_cohock_p   = []
        for wave in self.data['wave_details']:
            wave_geggs = wave['golden_ikura_num']
            wave_peggs = wave['ikura_num']
            self.waves_eggsgen += wave['golden_ikura_pop_num']
            self.waves_eggs    += wave_geggs
            self.waves_powregg += wave_peggs

            water_level = wave['water_level']['key']
            if water_level == "normal":
                self.waves_nt += 1
                self.nt_geggs.append(wave_geggs)
                self.nt_peggs.append(wave_peggs)
            elif water_level == "low":
                self.waves_lt += 1
                self.lt_geggs.append(wave_geggs)
                self.lt_peggs.append(wave_peggs)
            elif water_level == "high":
                self.waves_ht += 1
                self.ht_geggs.append(wave_geggs)
                self.ht_peggs.append(wave_peggs)
            else:
                print(f"Error in {self.fname}, {str(wave)}")

            water_event = wave['event_type']['key']
            if water_event == "water-levels":
                self.waves_day += 1
                self.day_geggs.append(wave_geggs)
                self.day_peggs.append(wave_peggs)
            else:
                self.waves_night += 1
                self.night_geggs.append(wave_geggs)
                self.night_peggs.append(wave_peggs)
                if water_event == "cohock-charge":
                    self.event_cohock += 1
                    self.lt_cohock_g.append(wave_geggs)
                    self.lt_cohock_p.append(wave_peggs)
                elif water_event == "fog":
                    self.event_fog += 1
                    if water_level == "high":
                        self.ht_fog += 1
                        self.ht_fog_g.append(wave_geggs)
                        self.ht_fog_p.append(wave_peggs)
                    elif water_level == "normal":
                        self.nt_fog += 1
                        self.nt_fog_g.append(wave_geggs)
                        self.nt_fog_p.append(wave_peggs)
                    elif water_level == "low":
                        self.lt_fog += 1
                        self.lt_fog_g.append(wave_geggs)
                        self.lt_fog_p.append(wave_peggs)
                elif water_event == "goldie-seeking":
                    self.event_seeking += 1
                    if water_level == "high":
                        self.ht_seek += 1
                        self.ht_seek_g.append(wave_geggs)
                        self.ht_seek_p.append(wave_peggs)
                    elif water_level == "normal":
                        self.nt_seek += 1
                        self.nt_seek_g.append(wave_geggs)
                        self.nt_seek_p.append(wave_peggs)
                elif water_event == "griller":
                    self.event_grills += 1
                    if water_level == "high":
                        self.ht_grills += 1
                        self.ht_grills_g.append(wave_geggs)
                        self.ht_grills_p.append(wave_peggs)
                    elif water_level == "normal":
                        self.nt_grills += 1
                        self.nt_grills_g.append(wave_geggs)
                        self.nt_grills_p.append(wave_peggs)
                elif water_event == "rush":
                    self.event_rush += 1
                    if water_level == "high":
                        self.ht_rush += 1
                        self.ht_rush_g.append(wave_geggs)
                        self.ht_rush_p.append(wave_peggs)
                    elif water_level == "normal":
                        self.nt_rush += 1
                        self.nt_rush_g.append(wave_geggs)
                        self.nt_rush_p.append(wave_peggs)
                elif water_event == "the-mothership":
                    self.event_moship += 1
                    if water_level == "high":
                        self.ht_moship += 1
                        self.ht_moship_g.append(wave_geggs)
                        self.ht_moship_p.append(wave_peggs)
                    elif water_level == "normal":
                        self.nt_moship+= 1
                        self.nt_moship_g.append(wave_geggs)
                        self.nt_moship_p.append(wave_peggs)
                    elif water_level == "low":
                        self.lt_moship += 1
                        self.lt_moship_g.append(wave_geggs)
                        self.lt_moship_p.append(wave_peggs)
                else:
                    print(f"Error in {self.fname}, {water_event}")

        self.deaths        = self.data['my_result']['dead_count']
        self.raises        = self.data['my_result']['help_count']
        self.powereggs     = self.data['my_result']['ikura_num']
        self.goldeneggs    = self.data['my_result']['golden_ikura_num']
        self.goldtotal     = self.goldeneggs
        self.powertotal    = self.powereggs
        for player in self.data['other_results']:
            self.goldtotal += player['golden_ikura_num']
            self.powertotal += player['ikura_num']

    def load_images(self):
        if not "schedule" in self.data:
            return
        if not os.path.isdir("images"):
            os.mkdir("images")
            os.mkdir("images/special")
            os.mkdir("images/weapon")
            os.mkdir("images/coop_weapons")
            os.mkdir("images/coop_stage")

        # weapons
        for weapons in self.data['schedule']['weapons'] + self.data['my_result']['weapon_list']:
 #           RAWOut = open(1, 'w', encoding='utf8', closefd=False)
  #          print(f"weapon is : {weapons}", file=RAWOut)
            if "weapon" in weapons:
                key = "weapon"
            else:
                key = "coop_special_weapon"
            imgpath = weapons[key]['image']
            imgfile = imgpath.split('/')[-1]
            savpath = f"images/{imgpath.split('/')[2]}/{imgfile}"

            if not exists(savpath):
                print(f"Rerieving https://app.splatoon2.nintendo.net{imgpath} -> {savpath}")
                urllib.request.urlretrieve(f"https://app.splatoon2.nintendo.net{imgpath}", savpath)

            if key == "weapon":
                thbpath = weapons[key]['thumbnail']
                thbfile = thbpath.split('/')[-1]
                savthmb = f"images/{key}/{thbfile}"
                if not exists(savthmb):
                    print(f"Rerieving https://app.splatoon2.nintendo.net{thbpath} -> {savthmb}")
                    urllib.request.urlretrieve(f"https://app.splatoon2.nintendo.net{thbpath}", savthmb)

        # stage
        imgpath = self.data['schedule']['stage']['image']
        imgfile = imgpath.split('/')[-1]
        savpath = f"images/{imgpath.split('/')[2]}/{imgfile}"
        if not exists(savpath):
            print(f"Rerieving https://app.splatoon2.nintendo.net{imgpath} -> {savpath}")
            urllib.request.urlretrieve(f"https://app.splatoon2.nintendo.net{imgpath}", savpath)

        # specials
        for key in {"image_a", "image_b"}:
            imgpath = self.data['my_result']['special'][key]
            imgfile = imgpath.split('/')[-1]
            savpath = f"images/{imgpath.split('/')[2]}/{imgfile}"
            if not exists(savpath):
                print(f"Rerieving https://app.splatoon2.nintendo.net{imgpath} -> {savpath}")
                urllib.request.urlretrieve(f"https://app.splatoon2.nintendo.net{imgpath}", savpath)



    def check_game(self):
        # sanity check
        if self.play_time == 0:
            return False
#       not right as it represent the total per waves which is different when the mothership steal eggs
#        if self.goldtotal != self.waves_eggs:
#            print(f"Discrepancy in {self.fname}, golden eggs: {self.goldtotal}  (ignored) /  {self.waves_eggs} (real)")  
            
        if self.powertotal != self.waves_powregg:
            print(f"Discrepancy in {self.fname}, power eggs: {self.powertotal} (ignored) /  {self.waves_powregg} (real)") 
            return False
        return True

    def load_game(self, name, dirname):
        with open(dirname + "/" + name, 'r', encoding="utf-8") as f:
            g = json.load(f)
 
#        RAWOut = open(1, 'w', encoding='utf8', closefd=False)
#        for key, val in g.items():
#           print(key + " - " + str(val), file=RAWOut)
#           print(key, file=RAWOut)
#        print(g, file=RAWOut)
        return g

    def __init__(self, f, dirname="results"):
        self.fname = f
        self.data = self.load_game(f, dirname)
        self.process_game()
#        self.load_images()

def load_games(args):
    dirname = "results" if os.path.isdir("results") else "json"
    if (len(args.numgames) == 0):
        flist = glob.glob(dirname+"/*.json")
        if (len(flist) == 0):
            sys.exit(f"no games found in '{dirname}' dir")
        refpath = max(flist, key=os.path.getctime)
        refname = refpath.split('/')[1]
    else:
        refname = f"{args.numgames[0]}.json"
        refpath = f"{dirname}/{refname}"
        if not exists(refpath):
            sys.exit(f"{refname} not found in '{dirname}' dir")

    g = Game(refname, dirname)
    mintime = g.start_time
    maxtime = g.end_time
    mint = time.gmtime(mintime)
    maxt = time.gmtime(maxtime)
    print(f"Adding Games from {strftime('%Y-%m-%d %H:%M:%S %Z', mint)} to {strftime('%Y-%m-%d %H:%M:%S %Z', maxt)} => {strftime('%Y%m%d%H', mint)} (length = {((maxtime - mintime) / 3600):2.0f}h)")

    all_games = []
    if args.single:
        all_games.append(g)
        print(f"Games from {strftime('%Y-%m-%d %H:%M:%S %Z', mint)} to {strftime('%Y-%m-%d %H:%M:%S %Z', maxt)} => {strftime('%Y%m%d%H', mint)} (length = {((maxtime - mintime) / 3600):2.0f}h)")
        return all_games

    is_gamelist = len(args.numgames) > 1
    has_exclude = len(args.exclude) > 0
    rotonly = args.rotation or not (args.all or args.single or args.rotation or is_gamelist)
    for jsonfile in sorted([i.split('/')[1] for i in glob.glob(dirname+"/*.json")]):
#        print(f'Working on {jsonfile}')
        ng = Game(jsonfile, dirname)
        if not ng.check_game():
            continue
        # exclusion
        if has_exclude and jsonfile.split('.')[0] in args.exclude:
            continue
        # rotation? check time boundaries
        if rotonly and ((ng.play_time < mintime) or (ng.play_time > maxtime)):
            continue
        # list of games? check non-existence]
        if is_gamelist and jsonfile.split('.')[0] not in args.numgames:
            continue 
        if args.dangermax and ng.danger_rate != 200:
            continue
        if args.winonly and (ng.wavespassed != 3):
            continue
        if args.lossonly and (ng.wavespassed == 3):
            continue
        if args.alldays and ((ng.wavespassed != 3) or (ng.waves_night != 0)):
            continue
        print(f"Adding {ng.job_id}")
        all_games.append(ng)
    print(f"Games from {strftime('%Y-%m-%d %H:%M:%S %Z', mint)} to {strftime('%Y-%m-%d %H:%M:%S %Z', maxt)} => {strftime('%Y%m%d%H', mint)} (length = {((maxtime - mintime) / 3600):2.0f}h)")
    return all_games

def update_players(all_games):
#    RAWOut = open(1, 'w', encoding='utf8', closefd=False)
    players = dict()
    json_p_file = "players.json"
    if os.path.exists(json_p_file):
        with open(json_p_file, 'r', encoding="utf-8") as f:
            players = json.load(f)
    print(f"Players DB: {len(players)} entries")
    for game in all_games:
        player_list = game.players
        for player in player_list:
            if player['player_id'] in players:
                if (isinstance(players[player['player_id']], str)):
                    if players[player['player_id']] != player['name']: 
                        players[player['player_id']] = [ players[player['player_id']], player['name'] ]
                else:
                    if not player['name'] in players[player['player_id']]:
                        players[player['player_id']].append(player['name'])
            else:
                players[player['player_id']] = player['name']
    with open(json_p_file, 'w', encoding="utf-8") as f:
        json.dump(players, f)    
    print(f"Updated Players DB: {len(players)} entries")



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-dangermax', action=argparse.BooleanOptionalAction, default=False)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-winonly', action=argparse.BooleanOptionalAction, default=False)
    group.add_argument('-lossonly', action=argparse.BooleanOptionalAction, default=False)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-rotation', action=argparse.BooleanOptionalAction, default=False)
    group.add_argument('-single', action=argparse.BooleanOptionalAction, default=False)
    group.add_argument('-all', action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument('-alldays', action=argparse.BooleanOptionalAction, help="implies -winonly", default=False)
    parser.add_argument('-exclude', nargs=1, type=str, help='excluded json number', default=[])
    parser.add_argument('-lang', type=str, help='lang', default="en")
    parser.add_argument('-out', type=str, help="output file", default="statistics.html")
    parser.add_argument('numgames', metavar='N', type=str, nargs='*', help='json number')
    args = parser.parse_args()
#   print(args)

    all_games = load_games(args)
    if len(all_games) == 0:
        print("No games loaded")
    else:
        session = GameSession()
        session.get_stats(all_games)
        with open(args.out, 'w', encoding="utf-8") as f:
            f.write(print_html_head(session, args.lang))
            f.write(print_specials_html(session, args.lang))
            f.write(print_weapons_html(session, args.lang))
            f.write(print_waves_html(session, args.lang))
        session.print_stats(args.lang)
#        print(print_specials_html(stats, args.lang))
        update_players(all_games)

