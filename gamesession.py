from wave import Wave
from special import Special
from weapon import Weapon
from bosslist import SalmonBossList
from game import Game
from statistics import mean as mean
from statistics import pstdev as pstdev
from statistics import quantiles as quantiles


class GameSession:
    def get_stats(self: 'GameSession', game_list: list[Game]) -> None:
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
        self.ht_day      = 0
        self.nt_day      = 0
        self.lt_day      = 0
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
        self.ht_day_g    = []
        self.nt_day_g    = []
        self.lt_day_g    = []
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
        self.boss_tkill  = { "sakelien-bomber" : [], "sakelien-cup-twins" : [],
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
            for eggs in g.ht_day_g:
                self.ht_day_g.append(eggs)
            for eggs in g.nt_day_g:
                self.nt_day_g.append(eggs)
            for eggs in g.lt_day_g:
                self.lt_day_g.append(eggs)
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
            self.ht_day    += g.ht_day
            self.nt_day    += g.nt_day
            self.lt_day    += g.lt_day
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
                tkill = 0
                for player_kill in g.boss_k_team:
                    tkill = tkill + player_kill.b_list[boss_name]
                self.boss_tkill[boss_name].append(tkill)
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

    def print_stats(self: 'GameSession', lang:str="en") -> None:
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
