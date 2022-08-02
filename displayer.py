import json
import os
import argparse
import gzip

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-name', action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument('idplayer', metavar='id', type=str, nargs='*', help='player id')
    args = parser.parse_args()

    RAWOut = open(1, 'w', encoding='utf8', closefd=False)
    players = dict()
    json_p_file = "players.json.gz"
    if os.path.exists(json_p_file):
        with gzip.open(json_p_file, 'rt', encoding="utf-8") as f:
            players = json.load(f)
    print(f"Players DB: {len(players)} entries", file=RAWOut)
    if len(args.idplayer) == 0:
        pidlist = players.keys()
    else:
        pidlist = args.idplayer

    for pid in pidlist:
        if args.name:
            # lookup by name (contained in real name)
            res = []
            for player in players:
                for name in players[player]:
                    if pid in name:
                        res.append(player)
            if len(res) > 0:
               for p in res:
                    playerdict = players[p]
                    ndict = dict()
                    for entry in playerdict:
                        ndict[entry] = len(playerdict[entry])
                    print(f"Player ID: \"{p}\"", file=RAWOut)
                    for k in dict(sorted(ndict.items(), reverse=True, key=lambda item: item[1])):
                        print(f"         -> \"{k} ({ndict[k]})", file=RAWOut)
        else:
            # lookup by id (exact)
            if pid in players:
                ndict = dict()
                playerdict = players[pid]
                for entry in playerdict:
                    ndict[entry] = len(playerdict[entry])
                print(f"Player ID: \"{pid}\"", file=RAWOut)
                for k in dict(sorted(ndict.items(), reverse=True, key=lambda item: item[1])):
                    print(f"         -> \"{k} ({ndict[k]})", file=RAWOut)
            else:
                print(f"Player ID '{pid}' not found", file=RAWOut)
        

