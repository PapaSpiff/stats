from pstats import StatsProfile
import sys
import json
import os
import glob
from wave import Wave
from special import Special
from weapon import Weapon
from bosslist import SalmonBossList
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

class Stats:
    def get_stats(self, game_list):
        self.scores      = []
        self.kills       = []
        self.tkills      = []
        self.pctkills    = []
        self.pcttkills   = []
        self.boss_tot    = []
        self.wavespassed = []
        self.dangerrate  = []
        self.deaths      = []
        self.raises      = []
        self.goldeneggs  = []
        self.powereggs   = []
        self.goldentotal = []
        self.goldenraw   = []
        self.goldengen   = []
        self.powertotal  = []
        self.retr_rate   = []
        self.ht_geggs    = []
        self.ht_peggs    = []
        self.nt_geggs    = []
        self.nt_peggs    = []
        self.lt_geggs    = []
        self.lt_peggs    = []    
        self.day_geggs   = []
        self.day_peggs   = []
        self.night_geggs = []
        self.night_peggs = []
        self.wav_nt      = 0
        self.wav_ht      = 0
        self.wav_lt      = 0
        self.wav_day     = 0
        self.wav_night   = 0
        self.ev_moship   = 0
        self.ev_rush     = 0
        self.ev_grills   = 0
        self.ev_seek     = 0
        self.ev_fog      = 0
        self.ev_cohock   = 0
        self.ht_seek     = 0
        self.nt_seek     = 0
        self.ht_rush     = 0
        self.nt_rush     = 0
        self.ht_grills   = 0
        self.nt_grills   = 0
        self.ht_moship   = 0
        self.nt_moship   = 0
        self.lt_moship   = 0
        self.ht_fog      = 0
        self.nt_fog      = 0
        self.lt_fog      = 0
        self.ht_seek_g   = []
        self.nt_seek_g   = []
        self.ht_rush_g   = []
        self.nt_rush_g   = []
        self.ht_grills_g = []
        self.nt_grills_g = []
        self.ht_moship_g = []
        self.nt_moship_g = []
        self.lt_moship_g = []
        self.ht_fog_g    = []
        self.nt_fog_g    = []
        self.lt_fog_g    = []
        self.lt_cohock_g = []
        self.full_day_g  = []
        self.one_night_g = []
        self.two_nights_g= []
        self.all_nights_g= []
        self.full_day_p  = []
        self.one_night_p = []
        self.two_nights_p= []
        self.all_nights_p= []
        self.my_specials = {}
        self.us_specials = {}
        self.my_weapons  = {}
        self.wavetotal   = 0
        self.boss_list   = { "sakelien-bomber" : [], "sakelien-cup-twins" : [],
                             "sakelien-shield" : [], "sakelien-snake"     : [],
                             "sakelien-tower"  : [], "sakediver"          : [],
                             "sakedozer"       : [], "sakerocket"         : [],
                             "sakelien-golden" : [] }
        self.boss_kill   = { "sakelien-bomber" : [], "sakelien-cup-twins" : [],
                             "sakelien-shield" : [], "sakelien-snake"     : [],
                             "sakelien-tower"  : [], "sakediver"          : [],
                             "sakedozer"       : [], "sakerocket"         : [],
                             "sakelien-golden" : [] }
        for g in game_list:
            self.wavetotal += g.wavesplayed
            self.scores.append(g.score)
            self.boss_tot.append(g.boss_tot_num)
            self.kills.append(g.boss_kill_num)
            self.tkills.append(g.boss_tkill_n + g.boss_kill_num)
#            pctkills.append(g.boss_kill_num / (g.boss_tkill_n + g.boss_kill_num))
            if g.boss_tot_num != 0:
                self.pctkills.append(g.boss_kill_num / g.boss_tot_num)
                self.pcttkills.append((g.boss_tkill_n + g.boss_kill_num) / g.boss_tot_num)
            else:
                self.pctkills.append(0)
                self.pcttkills.append(0)
            self.wavespassed.append(g.wavespassed)
            self.dangerrate.append(g.danger_rate)
            self.deaths.append(g.deaths)
            self.raises.append(g.raises)
            self.goldeneggs.append(g.goldeneggs)
            self.powereggs.append(g.powereggs)
            self.goldenraw.append(g.goldtotal)
            self.goldentotal.append(g.waves_eggs)
            self.goldengen.append(g.waves_eggsgen)
            if g.waves_eggsgen != 0:
                self.retr_rate.append(g.waves_eggs / g.waves_eggsgen)
            else:
                self.retr_rate.append(0)
            self.powertotal.append(g.powertotal)
            for eggs in g.ht_geggs:
                self.ht_geggs.append(eggs)
            for eggs in g.ht_peggs:
                self.ht_peggs.append(eggs)
            for eggs in g.nt_geggs:
                self.nt_geggs.append(eggs)
            for eggs in g.nt_peggs:
                self.nt_peggs.append(eggs)
            for eggs in g.lt_geggs:
                self.lt_geggs.append(eggs)
            for eggs in g.lt_peggs:
                self.lt_peggs.append(eggs)
            for eggs in g.day_geggs:
                self.day_geggs.append(eggs)
            for eggs in g.day_peggs:
                self.day_peggs.append(eggs)
            for eggs in g.night_geggs:
                self.night_geggs.append(eggs)
            for eggs in g.night_peggs:
                self.night_peggs.append(eggs)
            for eggs in g.ht_seek_g:
                self.ht_seek_g.append(eggs)
            for eggs in g.nt_seek_g:
                self.nt_seek_g.append(eggs)
            for eggs in g.ht_rush_g:
                self.ht_rush_g.append(eggs)
            for eggs in g.nt_rush_g:
                self.nt_rush_g.append(eggs)
            for eggs in g.ht_grills_g:
                self.ht_grills_g.append(eggs)
            for eggs in g.nt_grills_g:
                self.nt_grills_g.append(eggs)
            for eggs in g.ht_moship_g:
                self.ht_moship_g.append(eggs)
            for eggs in g.nt_moship_g:
                self.nt_moship_g.append(eggs)
            for eggs in g.lt_moship_g:
                self.lt_moship_g.append(eggs)
            for eggs in g.ht_fog_g:
                self.ht_fog_g.append(eggs)
            for eggs in g.nt_fog_g:
                self.nt_fog_g.append(eggs)
            for eggs in g.lt_fog_g:
                self.lt_fog_g.append(eggs)
            for eggs in g.lt_cohock_g:
                self.lt_cohock_g.append(eggs)
            self.wav_ht    += g.waves_ht
            self.wav_nt    += g.waves_nt
            self.wav_lt    += g.waves_lt
            self.wav_day   += g.waves_day
            self.wav_night += g.waves_night
            if g.waves_day == 3:
                self.full_day_g.append(g.waves_eggs)
                self.full_day_p.append(g.waves_powregg)
            elif (g.waves_day == 2) and (g.waves_night == 1):
                self.one_night_g.append(g.waves_eggs)
                self.one_night_p.append(g.waves_powregg)
            elif (g.waves_day == 1) and (g.waves_night == 2):
                self.two_nights_g.append(g.waves_eggs)
                self.two_nights_p.append(g.waves_powregg)
            elif (g.waves_night == 3):
                self.all_nights_g.append(g.waves_eggs)
                self.all_nights_p.append(g.waves_powregg)
            #else: 
                # incomplete game, do not count them
                #print(f"Error in game, too many waves : {str(g)}")
            self.ev_moship += g.event_moship
            self.ev_rush   += g.event_rush
            self.ev_grills += g.event_grills
            self.ev_seek   += g.event_seeking
            self.ev_fog    += g.event_fog
            self.ev_cohock += g.event_cohock
            self.ht_seek   += g.ht_seek
            self.nt_seek   += g.nt_seek
            self.ht_rush   += g.ht_rush
            self.nt_rush   += g.nt_rush
            self.ht_grills += g.ht_grills
            self.nt_grills += g.nt_grills
            self.ht_moship += g.ht_moship
            self.nt_moship += g.nt_moship
            self.lt_moship += g.lt_moship
            self.ht_fog    += g.ht_fog
            self.nt_fog    += g.nt_fog
            self.lt_fog    += g.lt_fog
            for boss_name in SalmonBossList.boss_names.values():
                self.boss_list[boss_name].append(g.boss_list.b_list[boss_name])
                self.boss_kill[boss_name].append(g.boss_kill.b_list[boss_name])
            if g.special.key in self.my_specials:
                self.my_specials[g.special.key] += 1
                self.us_specials[g.special.key] += g.special_usage
            else:
                self.my_specials[g.special.key] = 1
                self.us_specials[g.special.key] = 1
            for weapon in g.weapon_list:
                if weapon.key in self.my_weapons:
                    self.my_weapons[weapon.key] += 1
                else:
                    self.my_weapons[weapon.key] = 1

            self.totwavenight = max(1, self.wav_night)

    def print_stats(self, lang="en"):
        print(f"Number of games        : {len(self.scores)}")
        print("\nTeam Totals")
        print(f"Golden eggs max/min    : {max(self.goldentotal):3d} / {min(self.goldentotal):d}")
        print(f"Golden eggs average    : {mean(self.goldentotal):6.2f} (stddev: {pstdev(self.goldentotal):.2f})")
        print(f"Power eggs average     : {mean(self.powertotal):6.1f} (stddev: {pstdev(self.powertotal):.2f})")
        print(f"Score max/min          : {max(self.scores):3d} / {min(self.scores):d}")
        print(f"Score average          : {mean(self.scores):6.2f} (stddev: {pstdev(self.scores):.2f})")
        print(f"Danger rate average    : {mean(self.dangerrate):6.2f} (stddev: {pstdev(self.dangerrate):.2f})")
        print(f"Team Boss kill average : {mean(self.tkills):6.2f} (stddev: {pstdev(self.tkills):.2f})")
        print(f"Total Boss             : {mean(self.boss_tot):6.2f} (stddev: {pstdev(self.boss_tot):.2f})")
        print(f"Boss kill percentage   : {mean(self.pcttkills):7.2%} (stddev: {pstdev(self.pcttkills):.2%})")
        print(f"Waves passed average   : {mean(self.wavespassed):6.2f} (stddev: {pstdev(self.wavespassed):.2f})")
        print(f"Produced eggs max/min  : {max(self.goldengen):3d} / {min(self.goldengen):d}")
        print(f"Produced eggs average  : {mean(self.goldengen):6.2f} (stddev: {pstdev(self.goldengen):.2f})")
        print(f"Retrieval rate max/min : {max(self.retr_rate):6.2%} / {min(self.retr_rate):.2%}")
        print(f"Retrieval rate average : {mean(self.retr_rate):6.2%} (stddev: {pstdev(self.retr_rate):.2%})")
        print("\nIndividual Totals")
        print(f"Golden eggs max/min    : {max(self.goldeneggs):3d} / {min(self.goldeneggs):d}")
        print(f"Golden eggs average    : {mean(self.goldeneggs):6.2f} (stddev: {pstdev(self.goldeneggs):.2f})")
        print(f"Power eggs max/min     : {max(self.powereggs):4d} / {min(self.powereggs):d}")
        print(f"Power eggs average     : {mean(self.powereggs):7.2f} (stddev: {pstdev(self.powereggs):.2f})")
        print(f"Boss kills average     : {mean(self.kills):6.2f} (stddev: {pstdev(self.kills):.2f})")
        print(f"Boss kills percentage  : {mean(self.pctkills):7.2%} (stddev: {pstdev(self.pctkills):.2%})")
        print(f"Deaths                 : {mean(self.deaths):6.2f} (stddev: {pstdev(self.deaths):.2f})")
        print(f"Raises                 : {mean(self.raises):6.2f} (stddev: {pstdev(self.raises):.2f})")
        if True: # if display_special weapons
            print(f"Specials               :")
            for special in Special.special_ids.values():
                if special in self.my_specials:
                    print(f"  {Special.to_str(special, lang):<20} : {self.my_specials[special]:3.0f} ({self.my_specials[special]/len(self.scores):5.2%}) usage: {self.us_specials[special]:3.0f} ({self.us_specials[special]/(2*self.my_specials[special]):5.2%})")

            print(f"Weapons                :")
            for weapon in Weapon.weapon_ids.values():
                if weapon in self.my_weapons:
                    print(f"  {Weapon.to_str(weapon, lang):<20} : {self.my_weapons[weapon]:3.0f} ({self.my_weapons[weapon]/self.wavetotal:6.2%})")

        print(f"Boss                   :")
        for boss_name in SalmonBossList.boss_names.values():
            if sum(self.boss_kill[boss_name]) != 0:
                print("  Kills - " + SalmonBossList.get_boss_name(boss_name, lang).ljust(12) + f" : {sum(self.boss_kill[boss_name]):3g} (average: {mean(self.boss_kill[boss_name]):5.2f}) ({sum(self.boss_kill[boss_name]) / sum(self.boss_list [boss_name]):6.2%})")

        print("\nWaves Information")
        sprefix = "Water levels"
        if self.wav_ht > 0:
            print(f"{sprefix}           :  High Tide    - {self.wav_ht:3g} ({self.wav_ht / self.wavetotal:6.2%} / 20%) (eggs average {mean(self.ht_geggs):6.2f}, max {max(self.ht_geggs):6.2f}, min {min(self.ht_geggs):6.2f}, stddev {pstdev(self.ht_geggs):6.2f})")
            sprefix = "            "
        if self.wav_nt > 0:
            print(f"{sprefix}           :  Normal Tide  - {self.wav_nt:3g} ({self.wav_nt / self.wavetotal:6.2%} / 60%) (eggs average {mean(self.nt_geggs):6.2f}, max {max(self.nt_geggs):6.2f}, min {min(self.nt_geggs):6.2f}, stddev {pstdev(self.nt_geggs):6.2f})")
            sprefix = "            "
        if self.wav_lt > 0:
            print(f"{sprefix}           :  Low Tide     - {self.wav_lt:3g} ({self.wav_lt / self.wavetotal:6.2%} / 20%) (eggs average {mean(self.lt_geggs):6.2f}, max {max(self.lt_geggs):6.2f}, min {min(self.lt_geggs):6.2f}, stddev {pstdev(self.lt_geggs):6.2f})")
        sprefix = "Events"
        if self.wav_day > 0:
            print(f"{sprefix}                 :  Days         - {self.wav_day:3g} ({self.wav_day / self.wavetotal:6.2%} / 75%) (eggs average {mean(self.day_geggs):6.2f}, max {max(self.day_geggs):6.2f}, min {min(self.day_geggs):6.2f}, stddev {pstdev(self.day_geggs):6.2f})")
            sprefix = "      "
        if self.wav_night > 0:
            print(f"{sprefix}                 :  Nights       - {self.wav_night:3g} ({self.wav_night / self.wavetotal:6.2%} / 25%) (eggs average {mean(self.night_geggs):6.2f}, max {max(self.night_geggs):6.2f}, min {min(self.night_geggs):6.2f}, stddev {pstdev(self.night_geggs):6.2f})")
        if (self.ev_moship > 0):
            print(f"                       :  . Mothership - {self.ev_moship:3g} ({self.ev_moship / self.wavetotal:6.2%} / 4.2%)")
            print(f"                       :  .            - Stolen eggs {sum(self.goldenraw) - sum(self.goldentotal):d}, (average: {(sum(self.goldenraw) - sum(self.goldentotal))/self.ev_moship:.2f})")  
            if (self.ht_moship > 0):
                print(f"                       :  .            - High   Tide: {self.ht_moship} ({self.ht_moship / self.wavetotal:6.2%} / 0.8%) (eggs average {mean(self.ht_moship_g):6.2f}, max {max(self.ht_moship_g):6.2f}, min {min(self.ht_moship_g):6.2f}, stddev {pstdev(self.ht_moship_g):6.2f})")    
            if (self.nt_moship > 0):
                print(f"                       :  .            - Normal Tide: {self.nt_moship} ({self.nt_moship / self.wavetotal:6.2%} / 2.5%) (eggs average {mean(self.nt_moship_g):6.2f}, max {max(self.nt_moship_g):6.2f}, min {min(self.nt_moship_g):6.2f}, stddev {pstdev(self.nt_moship_g):6.2f})")
            if (self.lt_moship > 0):
                print(f"                       :  .            - Low    Tide: {self.lt_moship} ({self.lt_moship / self.wavetotal:6.2%} / 0.8%) (eggs average {mean(self.lt_moship_g):6.2f}, max {max(self.lt_moship_g):6.2f}, min {min(self.lt_moship_g):6.2f}, stddev {pstdev(self.lt_moship_g):6.2f})")
        if (self.ev_rush > 0):
            print(f"                       :  . Rush       - {self.ev_rush:3g} ({self.ev_rush / self.wavetotal:6.2%} / 4.2%)")
            if (self.ht_rush > 0):
                print(f"                       :  .            - High   Tide: {self.ht_rush} ({self.ht_rush / self.wavetotal:6.2%} / 1.0%) (eggs average {mean(self.ht_rush_g):6.2f}, max {max(self.ht_rush_g):6.2f}, min {min(self.ht_rush_g):6.2f}, stddev {pstdev(self.ht_rush_g):6.2f})")    
            if (self.nt_rush > 0):
                print(f"                       :  .            - Normal Tide: {self.nt_rush} ({self.nt_rush / self.wavetotal:6.2%} / 3.1%) (eggs average {mean(self.nt_rush_g):6.2f}, max {max(self.nt_rush_g):6.2f}, min {min(self.nt_rush_g):6.2f}, stddev {pstdev(self.nt_rush_g):6.2f})")
        if (self.ev_grills > 0):
            print(f"                       :  . Grillers   - {self.ev_grills:3g} ({self.ev_grills / self.wavetotal:6.2%} / 4.2%)")
            if (self.ht_grills > 0):
                print(f"                       :  .            - High   Tide: {self.ht_grills} ({self.ht_grills / self.wavetotal:6.2%} / 1.0%) (eggs average {mean(self.ht_grills_g):6.2f}, max {max(self.ht_grills_g):6.2f}, min {min(self.ht_grills_g):6.2f}, stddev {pstdev(self.ht_grills_g):6.2f})")    
            if (self.nt_grills > 0):
                print(f"                       :  .            - Normal Tide: {self.nt_grills} ({self.nt_grills / self.wavetotal:6.2%} / 3.1%) (eggs average {mean(self.nt_grills_g):6.2f}, max {max(self.nt_grills_g):6.2f}, min {min(self.nt_grills_g):6.2f}, stddev {pstdev(self.nt_grills_g):6.2f})")
        if (self.ev_seek > 0):
            print(f"                       :  . Seeking    - {self.ev_seek:3g} ({self.ev_seek / self.wavetotal:6.2%} / 4.2%)")
            if (self.ht_seek > 0):
                print(f"                       :  .            - High   Tide: {self.ht_seek} ({self.ht_seek / self.wavetotal:6.2%} / 1.0%) (eggs average {mean(self.ht_seek_g):6.2f}, max {max(self.ht_seek_g):6.2f}, min {min(self.ht_seek_g):6.2f}, stddev {pstdev(self.ht_seek_g):6.2f})")    
            if (self.nt_seek > 0):
                print(f"                       :  .            - Normal Tide: {self.nt_seek} ({self.nt_seek / self.wavetotal:6.2%} / 3.1%) (eggs average {mean(self.nt_seek_g):6.2f}, max {max(self.nt_seek_g):6.2f}, min {min(self.nt_seek_g):6.2f}, stddev {pstdev(self.nt_seek_g):6.2f})")
        if (self.ev_fog > 0):
            print(f"                       :  . Fog        - {self.ev_fog:3g} ({self.ev_fog / self.wavetotal:6.2%} / 4.2%)")
            if (self.ht_fog > 0):
                print(f"                       :  .            - High   Tide: {self.ht_fog} ({self.ht_fog / self.wavetotal:6.2%} / 0.8%) (eggs average {mean(self.ht_fog_g):6.2f}, max {max(self.ht_fog_g):6.2f}, min {min(self.ht_fog_g):6.2f}, stddev {pstdev(self.ht_fog_g):6.2f})")    
            if (self.nt_fog > 0):
                print(f"                       :  .            - Normal Tide: {self.nt_fog} ({self.nt_fog / self.wavetotal:6.2%} / 2.5%) (eggs average {mean(self.nt_fog_g):6.2f}, max {max(self.nt_fog_g):6.2f}, min {min(self.nt_fog_g):6.2f}, stddev {pstdev(self.nt_fog_g):6.2f})")
            if (self.lt_fog > 0):
                print(f"                       :  .            - Low    Tide: {self.lt_fog} ({self.lt_fog / self.wavetotal:6.2%} / 0.8%) (eggs average {mean(self.lt_fog_g):6.2f}, max {max(self.lt_fog_g):6.2f}, min {min(self.lt_fog_g):6.2f}, stddev {pstdev(self.lt_fog_g):6.2f})")
        if (self.ev_cohock > 0):
            print(f"                       :  . Cannons    - {self.ev_cohock:3g} ({self.ev_cohock / self.wavetotal:6.2%} / 4.2%) ({self.ev_cohock / self.wavetotal:6.2%}/total) (eggs average {mean(self.lt_cohock_g):6.2f}, max {max(self.lt_cohock_g):6.2f}, min {min(self.lt_cohock_g):6.2f}, stddev {pstdev(self.lt_cohock_g):6.2f})")
        if (len(self.full_day_g) > 0):
            print(f"                       : All day    {len(self.full_day_g):2d} (Golden eggs : avg {mean(self.full_day_g):6.2f}, max {max(self.full_day_g):6.2f}, min {min(self.full_day_g):6.2f}, stddev: {pstdev(self.full_day_g):.2f})")
            print(f"                       :               (Power eggs  : avg {mean(self.full_day_p):6.2f} , max {max(self.full_day_p):6.2f}, min {min(self.full_day_p):6.2f}, stddev: {pstdev(self.full_day_p):.2f})")
        if (len(self.one_night_g) > 0):
            print(f"                       : One night  {len(self.one_night_g):2d} (Golden eggs : avg {mean(self.one_night_g):6.2f}, max {max(self.one_night_g):6.2f}, min {min(self.one_night_g):6.2f}, stddev: {pstdev(self.one_night_g):.2f})")
            print(f"                       :               (Power eggs  : avg {mean(self.one_night_p):6.2f} , max {max(self.one_night_p):6.2f}, min {min(self.one_night_p):6.2f}, stddev: {pstdev(self.one_night_p):.2f})")
        if (len(self.two_nights_g) > 0):
            print(f"                       : Two nights {len(self.two_nights_g):2d} (Golden eggs : avg {mean(self.two_nights_g):6.2f}, max {max(self.two_nights_g):6.2f}, min {min(self.two_nights_g):6.2f}, stddev: {pstdev(self.two_nights_g):.2f})")
            print(f"                       :               (Power eggs  : avg {mean(self.two_nights_p):6.2f} , max {max(self.two_nights_p):6.2f}, min {min(self.two_nights_p):6.2f}, stddev: {pstdev(self.two_nights_p):.2f})")
        if (len(self.all_nights_g) > 0):
            print(f"                       : All nights {len(self.all_nights_g):2d} (Golden eggs : avg {mean(self.all_nights_g):6.2f}, max {max(self.all_nights_g):6.2f}, min {min(self.all_nights_g):6.2f}, stddev: {pstdev(self.all_nights_g):.2f})")
            print(f"                       :               (Power eggs  : avg {mean(self.all_nights_p):6.2f} , max {max(self.all_nights_p):6.2f}, min {min(self.all_nights_p):6.2f}, stddev: {pstdev(self.all_nights_p):.2f})")                
        print("\nBoss Totals")
        for boss_name in SalmonBossList.boss_names.values():
            print("Boss - " + SalmonBossList.get_boss_name(boss_name, lang).ljust(15) + f" : {sum(self.boss_list[boss_name]):3g} (average: {mean(self.boss_list[boss_name]):5.2f}) (stddev: {pstdev(self.boss_list[boss_name]):5.2f})")


def print_specials_html(stats, lang):
    str_buffer = StringIO()
    str_buffer.write("<div class='card' id='card-specials'>\n")
    str_buffer.write(f"<h1>{Special.title_str(lang)}</h1>")
    str_buffer.write("<div id='specials'>\n")
    specialsize = len(stats.my_specials)
    specialnum = 1
    specialpercent = 0.0
    all_scores = len(stats.scores)
    str_buffer.write("<div class='specials-gradient' style='background: conic-gradient(")
    for special in Special.special_ids.values():
        if special in stats.my_specials:
            if (specialnum > 1):
                str_buffer.write(', ')   
            str_buffer.write(f"hsl({specialnum*360/specialsize:.2f}deg 100% 50%) {specialpercent:5.2%}")  
            specialnum += 1
            specialpercent += stats.my_specials[special]/all_scores  
            str_buffer.write(f" {specialpercent:5.2%}")
    str_buffer.write(")'>")
    specialnum = 1
    specialpercent = 0.0
    for special in Special.special_ids.values():
        if special in stats.my_specials:
            newpercent = stats.my_specials[special]/all_scores
            str_buffer.write(f"<span class='special-percent' style='transform: translateY(-50%) rotate({180.0*(2*specialpercent+newpercent)-90:5.2f}deg)'> {newpercent:5.2%}</span>")  
            specialnum += 1
            specialpercent += newpercent
    str_buffer.write("</div>")
    str_buffer.write(f"<div class='specials-list'>")
    specialnum = 1
    for special in Special.special_ids.values():
        if special in stats.my_specials:
            str_buffer.write(f"<div class='special-{specialsize:1d}-{specialnum:1d}'>")
            str_buffer.write(f"<img class='special-img' src='images/special/{Special.to_img(special)}' alt='{Special.to_str(special, lang)}'> ")
            str_buffer.write(f"<span class='special-name'>{Special.to_str(special, lang)}</span> : ")
            str_buffer.write(f"<span class='special-count' title='special occurence'>{stats.my_specials[special]:3.0f}</span>")
#            str_buffer.write(f" <span class='special-percent'>({stats.my_specials[special]/all_scores:5.2%})</span>")
            str_buffer.write(f" <span class='special-usage-percent' title='special usage'>({stats.us_specials[special]/(2*stats.my_specials[special]):5.2%})</span>")
            str_buffer.write("</div>\n")
            specialnum += 1
    str_buffer.write("</div>\n</div>\n</div>\n")
    return str_buffer.getvalue()

def print_weapons_html(stats, lang):
    str_buffer = StringIO()
    str_buffer.write("<div class='card' id='card-weapons'>\n")
    str_buffer.write(f"<h1>{Weapon.title_str(lang)}</h1>")
    str_buffer.write("<div id='weapons'>\n")
    weaponsize = len(stats.my_weapons)
    sorted_weapons = sorted(stats.my_weapons.items(), key=lambda x: x[1], reverse=True)
    weaponnum = 1
    weaponpercent = 0.0
    all_waves = stats.wavetotal
    if (weaponsize > 5):
        sorted_limited_weapons = []
        posnum = 0
        weaponsall = 0
        for (weapon, weaponoccurence) in sorted_weapons:
            if posnum < 4:
                sorted_limited_weapons.append( (weapon, weaponoccurence) )
                posnum += 1
            else:
                weaponsall += weaponoccurence
        sorted_limited_weapons.append(("other", weaponsall))
        weaponsize = 5
        # now we add the missing weapons (wildcard sessions)
        for weapon in Weapon.weapon_ids.values():
            if weapon.startswith("kuma"):
                continue
            if not weapon in stats.my_weapons:
                sorted_weapons.append((weapon, 0))
    else:
        sorted_limited_weapons = sorted_weapons

    str_buffer.write(f"<div class='weapons-gradient' style='background: conic-gradient(")
    for (weapon, weaponoccurence) in sorted_limited_weapons:
        if (weaponnum > 1):
            str_buffer.write(', ') 
        str_buffer.write(f"hsl({weaponnum*360/weaponsize:.2f}deg 100% 50%) {weaponpercent:5.2%}") 
        weaponnum += 1
        weaponpercent += weaponoccurence / all_waves
        str_buffer.write(f" {weaponpercent:5.2%}")  
    str_buffer.write(")'>") 
    weaponnum = 1
    weaponpercent = 0.0 
    for (weapon, weaponoccurence) in sorted_limited_weapons:
        newpercent = weaponoccurence / all_waves
        str_buffer.write(f"<span class='weapon-percent' style='transform: translateY(-50%) rotate({180.0*(2*weaponpercent+newpercent)-90:5.2f}deg)'> {newpercent:5.2%}</span>")
        weaponnum +=1
        weaponpercent += newpercent
    str_buffer.write("</div>")

    str_buffer.write(f"<div class='weapons-list'>")
    weaponnum = 1
    for (weapon, weaponoccurence) in sorted_weapons:
        str_buffer.write(f"<div class='weapon-{weaponsize:1d}-{weaponnum:1d}'>")
        str_buffer.write(f"<img class='weapon-img' src='images/weapon/{Weapon.to_img(weapon)}' alt='{Weapon.to_str(weapon, lang)}'> ")
        str_buffer.write(f"<span class='weapon-name'>{Weapon.to_str(weapon, lang)}</span> : ")
        str_buffer.write(f"<span class='weapon-count' title='weapon occurence'>{weaponoccurence:3.0f}</span>")
        str_buffer.write(f" <span class='weapon-occurence-percent' title='percentage of all occurences'>({weaponoccurence/all_waves:5.2%})</span>")
        str_buffer.write("</div>\n")
        if weaponnum < 5:
            weaponnum += 1
    str_buffer.write("</div>\n</div>\n</div>\n")
    return str_buffer.getvalue()


def print_waves_html(stats, lang):
    str_buffer = StringIO()
    str_buffer.write("<div class='card' id='card-waves'>\n")
    str_buffer.write(f"<h1>{Wave.other_str('title', lang)}</h1>")
    str_buffer.write("<table id='waves'>\n<thead><tr>")
    # TODO l10n
    str_buffer.write("<th scope='col'>Wave Types</th><th scope='col'>Occurences</th><th scope='col'>%</th><th scope='col'>Max Eggs</th><th scope='col'>Average</th></tr>")
    str_buffer.write("</thead>\n<tbody>")
    # Days
    str_buffer.write("<tr class='daywaves'>")
    str_buffer.write(f"<th scope='row' class='day'>{Wave.to_str('day', lang)}</th>")
    str_buffer.write(f"<td class='daynum'>{stats.wav_day:3g}</td>")
    daypct = stats.wav_day / stats.wavetotal
    if (daypct * 100) > (Wave.day_avg + Wave.wave_percent_max):
        str_buffer.write(f"<td class='daypct'><span class='statshigh' title='{Wave.day_avg/100:6.2%}'>{daypct:6.2%}</span></td>")
    elif (daypct * 100) < (Wave.day_avg - Wave.wave_percent_max):
        str_buffer.write(f"<td class='daypct'><span class='statslow' title='{Wave.day_avg/100:6.2%}'>{daypct:6.2%}</span></td>")
    else:
        str_buffer.write(f"<td class='daypct'><span class='statsnormal' title='{Wave.day_avg/100:6.2%}'>{daypct:6.2%}</span></td>")
    if (stats.wav_day > 0):
        str_buffer.write(f"<td class='daymaxeggs'><span title='min: {min(stats.day_geggs):6.2f}'>{max(stats.day_geggs):6.2f}</span></td>")
        str_buffer.write(f"<td class='dayavgeggs'><span title='stddev: {pstdev(stats.day_geggs):6.2f}'>{mean(stats.day_geggs):6.2f}</span></td></tr>\n")
    else:
        str_buffer.write(f"<td class='daymaxeggs'><span title='min: -'>-</span></td>")
        str_buffer.write(f"<td class='dayavgeggs'><span title='stddev: -'>-</span></td></tr>\n")
    # Nights
    str_buffer.write("<tr class='nightwaves'>")
    str_buffer.write(f"<th scope='row' class='night'>{Wave.to_str('night', lang)}</th>")
    str_buffer.write(f"<td class='nightnum'>{stats.wav_night:3g}</td>")
    nightpct = stats.wav_night / stats.wavetotal
    if (nightpct * 100) > (Wave.night_avg + Wave.wave_percent_max):
        str_buffer.write(f"<td class='nightpct'><span class='statshigh' title='{Wave.night_avg/100:6.2%}'>{nightpct:6.2%}</span></td>")
    elif (nightpct * 100) < (Wave.night_avg - Wave.wave_percent_max):
        str_buffer.write(f"<td class='nightpct'><span class='statslow' title='{Wave.night_avg/100:6.2%}'>{nightpct:6.2%}</span></td>")
    else:
        str_buffer.write(f"<td class='nightpct'><span class='statsnormal' title='{Wave.night_avg/100:6.2%}'>{nightpct:6.2%}</span></td>")
    if (stats.wav_night > 0):
        str_buffer.write(f"<td class='nightmaxeggs'><span title='min: {min(stats.night_geggs):6.2f}'>{max(stats.night_geggs):6.2f}</span></td>")
        str_buffer.write(f"<td class='nightavgeggs'><span title='stddev: {pstdev(stats.night_geggs):6.2f}'>{mean(stats.night_geggs):6.2f}</span></td></tr>\n")
    else:
        str_buffer.write(f"<td class='nightmaxeggs'><span title='min: -'>-</span></td>")
        str_buffer.write(f"<td class='nightavgeggs'><span title='stddev: -'>-</span></td></tr>\n")
    # High tide
    str_buffer.write("<tr class='hightidewaves'>")
    str_buffer.write(f"<th scope='row' class='hightide'>{Wave.to_str('high', lang)}</th>")
    str_buffer.write(f"<td class='hightidenum'>{stats.wav_ht:3g}</td>")
    highpct = stats.wav_ht / stats.wavetotal
    if (highpct * 100) > (Wave.high_avg + Wave.wave_percent_max):
        str_buffer.write(f"<td class='hightidepct'><span class='statshigh' title='{Wave.high_avg/100:6.2%}'>{highpct:6.2%}</span></td>")
    elif (highpct * 100) < (Wave.high_avg - Wave.wave_percent_max):
        str_buffer.write(f"<td class='hightidepct'><span class='statslow' title='{Wave.high_avg/100:6.2%}'>{highpct:6.2%}</span></td>")
    else:
        str_buffer.write(f"<td class='hightidepct'><span class='statsnormal' title='{Wave.high_avg/100:6.2%}'>{highpct:6.2%}</span></td>")
    if (stats.wav_ht > 0):
        str_buffer.write(f"<td class='hightidemaxeggs'><span title='min: {min(stats.ht_geggs):6.2f}'>{max(stats.ht_geggs):6.2f}</span></td>")
        str_buffer.write(f"<td class='hightideavgeggs'><span title='stddev: {pstdev(stats.ht_geggs):6.2f}'>{mean(stats.ht_geggs):6.2f}</span></td></tr>\n")
    else:
        str_buffer.write(f"<td class='hightidemaxeggs'><span title='min: -'>-</span></td>")
        str_buffer.write(f"<td class='hightideavgeggs'><span title='stddev: -'>-</span></td></tr>\n")
    # Normal tide
    str_buffer.write("<tr class='normaltidewaves'>")
    str_buffer.write(f"<th scope='row' class='normaltide'>{Wave.to_str('normal', lang)}</th>")
    str_buffer.write(f"<td class='normaltidenum'>{stats.wav_nt:3g}</td>")
    normalpct = stats.wav_nt / stats.wavetotal
    if (normalpct * 100) > (Wave.normal_avg + Wave.wave_percent_max):
        str_buffer.write(f"<td class='normaltidepct'><span class='statshigh' title='{Wave.normal_avg/100:6.2%}'>{normalpct:6.2%}</span></td>")
    elif (normalpct * 100) < (Wave.normal_avg - Wave.wave_percent_max):
        str_buffer.write(f"<td class='normaltidepct'><span class='statslow' title='{Wave.normal_avg/100:6.2%}'>{normalpct:6.2%}</span></td>")
    else:
        str_buffer.write(f"<td class='normaltidepct'><span class='statsnormal' title='{Wave.normal_avg/100:6.2%}'>{normalpct:6.2%}</span></td>")
    if (stats.wav_nt > 0):
        str_buffer.write(f"<td class='normaltidemaxeggs'><span title='min: {min(stats.nt_geggs):6.2f}'>{max(stats.nt_geggs):6.2f}</span></td>")
        str_buffer.write(f"<td class='normalideavgeggs'><span title='stddev: {pstdev(stats.nt_geggs):6.2f}'>{mean(stats.nt_geggs):6.2f}</span></td></tr>\n")
    else:
        str_buffer.write(f"<td class='normaltidemaxeggs'><span title='min: -'>-</span></td>")
        str_buffer.write(f"<td class='normalideavgeggs'><span title='stddev: -'>-</span></td></tr>\n")
    # Low tide
    str_buffer.write("<tr class='lowtidewaves'>")
    str_buffer.write(f"<th scope='row' class='lowtide'>{Wave.to_str('low', lang)}</th>")
    str_buffer.write(f"<td class='lowtidenum'>{stats.wav_lt:3g}</td>")
    lowpct = stats.wav_lt / stats.wavetotal
    if (lowpct * 100) > (Wave.low_avg + Wave.wave_percent_max):
        str_buffer.write(f"<td class='lowtidepct'><span class='statshigh' title='{Wave.low_avg/100:6.2%}'>{lowpct:6.2%}</span></td>")
    elif (lowpct * 100) < (Wave.low_avg - Wave.wave_percent_max):
        str_buffer.write(f"<td class='lowtidepct'><span class='statslow' title='{Wave.low_avg/100:6.2%}'>{lowpct:6.2%}</span></td>")
    else:
        str_buffer.write(f"<td class='lowtidepct'><span class='statsnormal' title='{Wave.low_avg/100:6.2%}'>{lowpct:6.2%}</span></td>")
    if (stats.wav_lt > 0):
        str_buffer.write(f"<td class='lowtidemaxeggs'><span title='min: {min(stats.lt_geggs):6.2f}'>{max(stats.lt_geggs):6.2f}</span></td>")
        str_buffer.write(f"<td class='lowtideavgeggs'><span title='stddev: {pstdev(stats.lt_geggs):6.2f}'>{mean(stats.lt_geggs):6.2f}</span></td></tr>\n")
    else:
        str_buffer.write(f"<td class='lowtidemaxeggs'><span title='min: -'>-</span></td>")
        str_buffer.write(f"<td class='lowtideavgeggs'><span title='stddev: -'>-</span></td></tr>\n")
    str_buffer.write("</tbody></table>")

    str_buffer.write("<table id='wavemax'>\n<thead><tr>")
    str_buffer.write(f"<th colspan='7'>{Wave.other_str('title',lang)}</tr></thead><tbody>")
    # TODO l10n
    night = Wave.to_str("night", lang)
    nights = Wave.to_str("nights", lang)
    days = Wave.to_str("days", lang)
    str_buffer.write(f"<tr><td rowspan='2'>{Wave.other_str('titlemax',lang)}</td><td>Overall</td>")
    str_buffer.write(f"<td>3 {nights}</td><td>2 {nights}</td><td>1 {night}</td><td>3 {days}</td>")
    str_buffer.write(f"<td>{Wave.other_str('average',lang)}</td></tr>\n")
    str_buffer.write("<tr>")
    str_buffer.write(f"<td class='maxgoldeneggs'><span title='occurences: {len(stats.scores)}'>{max(stats.goldentotal):3g}</span></td>")
    if len(stats.all_nights_g) > 0:
        str_buffer.write(f"<td class='maxgoldeneggs3nights'><span title='occurences: {len(stats.all_nights_g)}, average: {mean(stats.all_nights_g):.2f}'>{max(stats.all_nights_g):3g}</span></td>")
    else:
        str_buffer.write(f"<td class='maxgoldeneggs3nights'><span title='occurences: 0, average -'>-</span></td>") 
    if len(stats.two_nights_g) > 0:
        str_buffer.write(f"<td class='maxgoldeneggs2nights'><span title='occurences: {len(stats.two_nights_g)}, average: {mean(stats.two_nights_g):.2f}'>{max(stats.two_nights_g):3g}</span></td>")
    else:
        str_buffer.write(f"<td class='maxgoldeneggs2nights'><span title='occurences: 0, average -'>-</span></td>") 
    if len(stats.one_night_g) > 0:
        str_buffer.write(f"<td class='maxgoldeneggs1night'><span title='occurences: {len(stats.one_night_g)}, average: {mean(stats.one_night_g):.2f}'>{max(stats.one_night_g):3g}</span></td>")
    else:
        str_buffer.write(f"<td class='maxgoldeneggs1night'><span title='occurences: 0, average -'>-</span></td>")
    if len(stats.full_day_g) > 0:
        str_buffer.write(f"<td class='maxgoldeneggs3days'><span title='occurences: {len(stats.full_day_g)}, average: {mean(stats.full_day_g):.2f}'>{max(stats.full_day_g):3g}</span></td>")
    else:
        str_buffer.write(f"<td class='maxgoldeneggs3days'><span title='occurences: 0, average -'>-</span></td>")
    str_buffer.write(f"<td class='maxgoldeneggs'><span title='stddev: {pstdev(stats.goldentotal):.2f}'>{mean(stats.goldentotal):.2f}</span></td>")
    str_buffer.write("</tr>\n</tbody></table>")
    # Night tables
    str_buffer.write("<table id='nightwavemax'>\n<thead><tr>")
    str_buffer.write(f"<th>{Wave.other_str('titlemax',lang)}</th><th scope='col'>{Wave.to_str('tide',lang)}</th><th scope='col'>%</th><th scope='col'>Max Eggs</th><th scope='col'>Average</th></tr></thead><tbody>")
    if (stats.ev_moship > 0):
        rpan = 1
        if (stats.ht_moship > 0):
            rpan += 1
        if (stats.nt_moship > 0):
            rpan += 1
        if (stats.lt_moship > 0):
            rpan += 1
        str_buffer.write(f"<tr><th class='mothership' rowspan='{rpan}' title='stolen eggs:{sum(stats.goldenraw) - sum(stats.goldentotal):d}, average: {(sum(stats.goldenraw) - sum(stats.goldentotal))/stats.ev_moship:.2f}'>{Wave.to_str('the-mothership', lang)}</th>")
        str_buffer.write(f"<td></td>")
        moship_pct = stats.ev_moship / stats.wavetotal
        if (moship_pct * 100) > (Wave.ms_avg + Wave.night_wave_percent_max):
            str_buffer.write(f"<td class='moshippct'><span class='statshigh' title='{Wave.ms_avg/100:3.2%}'>{moship_pct:3.2%}</span></td>")
        elif (moship_pct * 100) < (Wave.ms_avg - Wave.night_wave_percent_max):
            str_buffer.write(f"<td class='moshippct'><span class='statslow' title='{Wave.ms_avg/100:3.2%}'>{moship_pct:3.2%}</span></td>")
        else:
            str_buffer.write(f"<td class='moshippct'><span class='statsnormal' title='{Wave.ms_avg/100:3.2%}'>{moship_pct:3.2%}</span></td>")
        moship_g = stats.ht_moship_g + stats.nt_moship_g + stats.lt_moship_g
        str_buffer.write(f"<td class='moshipmax'><span title='min: {min(moship_g)}'>{max(moship_g)}</span></td>")
        str_buffer.write(f"<td class='moshipavg'><span title='stddev: {pstdev(moship_g)}'>{mean(moship_g)}</span></td></tr>")
        if (stats.ht_moship > 0):
            str_buffer.write(f"<tr><td>{Wave.to_str('high', lang)}</td>")
            moship_pct = stats.ht_moship / stats.wavetotal
            if (moship_pct * 100) > (Wave.ms_ht_avg + Wave.night_wave_percent_max):
                str_buffer.write(f"<td class='moshippct'><span class='statshigh' title='{Wave.ms_ht_avg/100:3.2%}'>{moship_pct:3.2%}</span></td>")
            elif (moship_pct * 100) < (Wave.ms_ht_avg - Wave.night_wave_percent_max):
                str_buffer.write(f"<td class='moshippct'><span class='statslow' title='{Wave.ms_ht_avg/100:3.2%}'>{moship_pct:3.2%}</span></td>")
            else:
                str_buffer.write(f"<td class='moshippct'><span class='statsnormal' title='{Wave.ms_ht_avg/100:3.2%}'>{moship_pct:3.2%}</span></td>")
            str_buffer.write(f"<td class='moshipmax'><span title='min: {min(stats.ht_moship_g)}'>{max(stats.ht_moship_g)}</span></td>")
            str_buffer.write(f"<td class='moshipavg'><span title='stddev: {pstdev(stats.ht_moship_g)}'>{mean(stats.ht_moship_g)}</span></td></tr>")
        if (stats.nt_moship > 0):
            str_buffer.write(f"<tr><td>{Wave.to_str('normal', lang)}</td>")
            moship_pct = stats.nt_moship / stats.wavetotal
            if (moship_pct * 100) > (Wave.ms_nt_avg + Wave.night_wave_percent_max):
                str_buffer.write(f"<td class='moshippct'><span class='statshigh' title='{Wave.ms_nt_avg/100:3.2%}'>{moship_pct:3.2%}</span></td>")
            elif (moship_pct * 100) < (Wave.ms_nt_avg - Wave.night_wave_percent_max):
                str_buffer.write(f"<td class='moshippct'><span class='statslow' title='{Wave.ms_nt_avg/100:3.2%}'>{moship_pct:3.2%}</span></td>")
            else:
                str_buffer.write(f"<td class='moshippct'><span class='statsnormal' title='{Wave.ms_nt_avg/100:3.2%}'>{moship_pct:3.2%}</span></td>")
            str_buffer.write(f"<td class='moshipmax'><span title='min: {min(stats.nt_moship_g)}'>{max(stats.nt_moship_g)}</span></td>")
            str_buffer.write(f"<td class='moshipavg'><span title='stddev: {pstdev(stats.nt_moship_g)}'>{mean(stats.nt_moship_g)}</span></td></tr>")
        if (stats.lt_moship > 0):
            str_buffer.write(f"<tr><td>{Wave.to_str('low', lang)}</td>")
            moship_pct = stats.lt_moship / stats.wavetotal
            if (moship_pct * 100) > (Wave.ms_lt_avg + Wave.night_wave_percent_max):
                str_buffer.write(f"<td class='moshippct'><span class='statshigh' title='{Wave.ms_lt_avg/100:3.2%}'>{moship_pct:3.2%}</span></td>")
            elif (moship_pct * 100) < (Wave.ms_lt_avg - Wave.night_wave_percent_max):
                str_buffer.write(f"<td class='moshippct'><span class='statslow' title='{Wave.ms_lt_avg/100:3.2%}'>{moship_pct:3.2%}</span></td>")
            else:
                str_buffer.write(f"<td class='moshippct'><span class='statsnormal' title='{Wave.ms_lt_avg/100:3.2%}'>{moship_pct:3.2%}</span></td>")
            str_buffer.write(f"<td class='moshipmax'><span title='min: {min(stats.lt_moship_g)}'>{max(stats.lt_moship_g)}</span></td>")
            str_buffer.write(f"<td class='moshipavg'><span title='stddev: {pstdev(stats.lt_moship_g)}'>{mean(stats.lt_moship_g)}</span></td></tr>")
    # rush
    if (stats.ev_rush > 0):
        rpan = 1
        if (stats.ht_rush > 0):
            rpan += 1
        if (stats.nt_rush> 0):
            rpan += 1
        str_buffer.write(f"<tr><th class='rush' rowspan='{rpan}'>{Wave.to_str('rush', lang)}</th>")
        str_buffer.write(f"<td></td>")
        ev_pct = stats.ev_rush / stats.wavetotal
        if (ev_pct * 100) > (Wave.rush_avg + Wave.night_wave_percent_max):
            str_buffer.write(f"<td class='rushpct'><span class='statshigh' title='{Wave.rush_avg/100:3.2%}'>{ev_pct:3.2%}</span></td>")
        elif (ev_pct * 100) < (Wave.rush_avg - Wave.night_wave_percent_max):
            str_buffer.write(f"<td class='rushpct'><span class='statslow' title='{Wave.rush_avg/100:3.2%}'>{ev_pct:3.2%}</span></td>")
        else:
            str_buffer.write(f"<td class='rushpct'><span class='statsnormal' title='{Wave.rush_avg/100:3.2%}'>{ev_pct:3.2%}</span></td>")
        rush_g = stats.ht_rush_g + stats.nt_rush_g
        str_buffer.write(f"<td class='rushmax'><span title='min: {min(rush_g)}'>{max(rush_g)}</span></td>")
        str_buffer.write(f"<td class='rushavg'><span title='stddev: {pstdev(rush_g)}'>{mean(rush_g)}</span></td></tr>")
        if (stats.ht_rush > 0):
            str_buffer.write(f"<tr><td>{Wave.to_str('high', lang)}</td>")
            ev_pct = stats.ht_rush / stats.wavetotal
            if (ev_pct * 100) > (Wave.ms_ht_avg + Wave.night_wave_percent_max):
                str_buffer.write(f"<td class='rushpct'><span class='statshigh' title='{Wave.rush_ht_avg/100:3.2%}'>{ev_pct:3.2%}</span></td>")
            elif (ev_pct * 100) < (Wave.ms_ht_avg - Wave.night_wave_percent_max):
                str_buffer.write(f"<td class='rushpct'><span class='statslow' title='{Wave.rush_ht_avg/100:3.2%}'>{ev_pct:3.2%}</span></td>")
            else:
                str_buffer.write(f"<td class='rushpct'><span class='statsnormal' title='{Wave.rush_ht_avg/100:3.2%}'>{ev_pct:3.2%}</span></td>")
            str_buffer.write(f"<td class='rushmax'><span title='min: {min(stats.ht_rush_g)}'>{max(stats.ht_rush_g)}</span></td>")
            str_buffer.write(f"<td class='rushavg'><span title='stddev: {pstdev(stats.ht_rush_g)}'>{mean(stats.ht_rush_g)}</span></td></tr>")
        if (stats.nt_rush > 0):
            str_buffer.write(f"<tr><td>{Wave.to_str('normal', lang)}</td>")
            ev_pct = stats.nt_rush / stats.wavetotal
            if (ev_pct * 100) > (Wave.rush_nt_avg + Wave.night_wave_percent_max):
                str_buffer.write(f"<td class='rushpct'><span class='statshigh' title='{Wave.rush_nt_avg/100:3.2%}'>{ev_pct:3.2%}</span></td>")
            elif (ev_pct * 100) < (Wave.ms_nt_avg - Wave.night_wave_percent_max):
                str_buffer.write(f"<td class='rushpct'><span class='statslow' title='{Wave.rush_nt_avg/100:3.2%}'>{ev_pct:3.2%}</span></td>")
            else:
                str_buffer.write(f"<td class='rushpct'><span class='statsnormal' title='{Wave.rush_nt_avg/100:3.2%}'>{ev_pct:3.2%}</span></td>")
            str_buffer.write(f"<td class='rushmax'><span title='min: {min(stats.nt_rush_g)}'>{max(stats.nt_rush_g)}</span></td>")
            str_buffer.write(f"<td class='rushavg'><span title='stddev: {pstdev(stats.nt_rush_g)}'>{mean(stats.nt_rush_g)}</span></td></tr>")
     # rseek
    if (stats.ev_seek > 0):
        rpan = 1
        if (stats.ht_seek > 0):
            rpan += 1
        if (stats.nt_seek> 0):
            rpan += 1
        str_buffer.write(f"<tr><th class='seek' rowspan='{rpan}'>{Wave.to_str('goldie-seeking', lang)}</th>")
        str_buffer.write(f"<td></td>")
        ev_pct = stats.ev_seek / stats.wavetotal
        if (ev_pct * 100) > (Wave.seek_avg + Wave.night_wave_percent_max):
            str_buffer.write(f"<td class='seekpct'><span class='statshigh' title='{Wave.seek_avg/100:3.2%}'>{ev_pct:3.2%}</span></td>")
        elif (ev_pct * 100) < (Wave.seek_avg - Wave.night_wave_percent_max):
            str_buffer.write(f"<td class='seekpct'><span class='statslow' title='{Wave.seek_avg/100:3.2%}'>{ev_pct:3.2%}</span></td>")
        else:
            str_buffer.write(f"<td class='seekpct'><span class='statsnormal' title='{Wave.seek_avg/100:3.2%}'>{ev_pct:3.2%}</span></td>")
        seek_g = stats.ht_seek_g + stats.nt_seek_g
        str_buffer.write(f"<td class='seekmax'><span title='min: {min(seek_g)}'>{max(seek_g)}</span></td>")
        str_buffer.write(f"<td class='seekavg'><span title='stddev: {pstdev(seek_g)}'>{mean(seek_g)}</span></td></tr>")
        if (stats.ht_seek > 0):
            str_buffer.write(f"<tr><td>{Wave.to_str('high', lang)}</td>")
            ev_pct = stats.ht_seek / stats.wavetotal
            if (ev_pct * 100) > (Wave.ms_ht_avg + Wave.night_wave_percent_max):
                str_buffer.write(f"<td class='seekpct'><span class='statshigh' title='{Wave.seek_ht_avg/100:3.2%}'>{ev_pct:3.2%}</span></td>")
            elif (ev_pct * 100) < (Wave.ms_ht_avg - Wave.night_wave_percent_max):
                str_buffer.write(f"<td class='seekpct'><span class='statslow' title='{Wave.seek_ht_avg/100:3.2%}'>{ev_pct:3.2%}</span></td>")
            else:
                str_buffer.write(f"<td class='seekpct'><span class='statsnormal' title='{Wave.seek_ht_avg/100:3.2%}'>{ev_pct:3.2%}</span></td>")
            str_buffer.write(f"<td class='seekmax'><span title='min: {min(stats.ht_seek_g)}'>{max(stats.ht_seek_g)}</span></td>")
            str_buffer.write(f"<td class='seekavg'><span title='stddev: {pstdev(stats.ht_seek_g)}'>{mean(stats.ht_seek_g)}</span></td></tr>")
        if (stats.nt_seek > 0):
            str_buffer.write(f"<tr><td>{Wave.to_str('normal', lang)}</td>")
            ev_pct = stats.nt_seek / stats.wavetotal
            if (ev_pct * 100) > (Wave.seek_nt_avg + Wave.night_wave_percent_max):
                str_buffer.write(f"<td class='seekpct'><span class='statshigh' title='{Wave.seek_nt_avg/100:3.2%}'>{ev_pct:3.2%}</span></td>")
            elif (ev_pct * 100) < (Wave.ms_nt_avg - Wave.night_wave_percent_max):
                str_buffer.write(f"<td class='seekpct'><span class='statslow' title='{Wave.seek_nt_avg/100:3.2%}'>{ev_pct:3.2%}</span></td>")
            else:
                str_buffer.write(f"<td class='seekpct'><span class='statsnormal' title='{Wave.seek_nt_avg/100:3.2%}'>{ev_pct:3.2%}</span></td>")
            str_buffer.write(f"<td class='seekmax'><span title='min: {min(stats.nt_seek_g)}'>{max(stats.nt_seek_g)}</span></td>")
            str_buffer.write(f"<td class='seekavg'><span title='stddev: {pstdev(stats.nt_seek_g)}'>{mean(stats.nt_seek_g)}</span></td></tr>")
        
        
#TODOTODO
    str_buffer.write("\n</tbody></table>")
    return str_buffer.getvalue()    

def print_html_head(stats, lang="en"):
    str_buffer = StringIO()
    str_buffer.write("<!DOCTYPE html>\n")
    str_buffer.write(f"<html lang='{lang}'>\n<meta charset='utf-8'>\n")
    str_buffer.write(f"<title>test</title>\n") # TODO localized title
    str_buffer.write("<link rel='stylesheet' href='style/sr.css'>\n")
    str_buffer.write("</head><body>\n")
    return str_buffer.getvalue()    

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
        stats = Stats()
        stats.get_stats(all_games)
        with open(args.out, 'w', encoding="utf-8") as f:
            f.write(print_html_head(stats, args.lang))
            f.write(print_specials_html(stats, args.lang))
            f.write(print_weapons_html(stats, args.lang))
            f.write(print_waves_html(stats, args.lang))
        stats.print_stats(args.lang)
#        print(print_specials_html(stats, args.lang))
        update_players(all_games)

