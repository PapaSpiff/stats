import sys
import json
import os
import glob
from gamesession import GameSession
from game import Game
from htmlgen import print_html_head
from htmlgen import print_specials_html, print_weapons_html, print_waves_html
from os.path import exists
from statistics import mean as mean
from statistics import pstdev as pstdev
from statistics import quantiles as quantiles
import time
from time import strftime
import argparse

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

def load_games(args) -> list['Game']:
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

def update_players(all_games) -> None:
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

