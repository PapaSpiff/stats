from pstats import StatsProfile
import sys
import json
import os
import glob
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

class Wave:
    # https://splatoonwiki.org/wiki/Salmon_Run_data#Wave_type
    wave_percent_max = 2
    night_wave_percent_max = 0.7
    day_avg      = 75
    night_avg    = 25
    low_avg      = 20
    normal_avg   = 60
    high_avg     = 20
    ms_avg       = 4.2
    ms_ht_avg    = 0.8
    ms_nt_avg    = 2.5
    ms_lt_avg    = 0.8
    seek_avg     = 4.2
    seek_ht_avg  = 1.0
    seek_nt_avg  = 3.1
    cohock_avg   = 4.2
    rush_avg     = 4.2
    rush_ht_avg  = 1.0
    rush_nt_avg  = 3.1
    grill_avg    = 4.2
    grill_ht_avg = 1.0
    grill_nt_avg = 3.1
    fog_avg      = 4.2
    fog_ht_avg   = 0.8
    fog_nt_avg   = 2.5
    fog_lt_avg   = 0.8

    waves_en = {
        'day' : "Day",
        'days' : "Days",
        'night' : "Night",
        'nights' : "Nights",
        'tide' : "Water levels",
        'high' : "High tide",
        'low' : "Low tide",
        'normal' : "Normal",
        'rush' : "Rush",
        'fog' : "Fog",
        'griller' : "The Griller",
        'cohock-charge' : "Cohock Charge",
        'goldie-seeking' : "Goldie Seeking",
        'the-mothership' : "The Mothership",
        'water-levels' : "-"

    }
    waves_fr = {
        'day' : "Jour",
        'days': "Jours",
        'night' : "Nuit",
        'nights' : "Nuits",
        'tide' : "Niveau de Marée",
        'high' : "Marée haute",
        'low' : "Marée basse",
        'normal' : "Mi-marée",
        'rush' : "Ruées",
        'fog' : "Brouillard",
        'griller' : "Barbeurks",
        'cohock-charge' : "Charges de Sumoches",
        'goldie-seeking' : "Chasse aux Dorax",
        'the-mothership' : "Vaisseaux Mères",
        'water-levels' : "-"
    }

    waves_ja = {
        'day' : "昼間", #FIXME
        'days' : "昼間", #FIXME
        'night' : "夜", #FIXME
        'nights' : "夜", #FIXME
        'tide' : "水位",
        'high' : "満潮",
        'low' : "干潮",
        'normal' : "通常", # FIXME?
        'rush' : "ラッシュ",
        'fog' : "霧",
        'griller' : "グリル発進",
        'cohock-charge' : "ドスコイ大量発生",
        'goldie-seeking' : "キンシャケ探し",
        'the-mothership' : "ハコビヤ襲来",
        'water-levels' : "-"
    }

    other_en = {
        'title' : "Waves",
        'titlemax' : "Team total Golden Eggs",
        'average'  : "Average",
    }
    other_fr = {
        'title' : "Vagues",
        'titlemax' : "Totaux d'œufs dorés d'équipe",
        'average'  : "Moyenne",
    }
    other_ja = {
        'title' : "WAVE",
        'titlemax' : "チーム合計の金イクラ納品数",
        'average'  : "平均",
    }

    def other_str(key, lang):
        if lang == "en":
            return Wave.other_en[key]
        elif lang == "fr":
            return Wave.other_fr[key]
        elif lang == "ja":
            return Wave.other_ja[key]
        else: #current default to en
            return Wave.other_en[key]

    def to_str(key, lang):
        if lang == "en":
            return Wave.waves_en[key]
        elif lang == "fr":
            return Wave.waves_fr[key]
        elif lang == "ja":
            return Wave.waves_ja[key]
        else: #current default to en
            return Wave.waves_en[key]


class Special:
    special_ids = {
        2: 'pitcher',
        7: 'presser',
        8: 'jetpack', 
        9: 'chakuchi'
    }
    special_en = {
        'presser' : "Sting Ray",
        'jetpack' : "Inkjet",
        'chakuchi': "Splashdown",
        'pitcher' : "Bomb Launcher"
    }
    special_fr = {
        'presser' : "Pigmalance",
        'jetpack' : "Chromo-jet",
        'chakuchi': "Choc chromatique",
        'pitcher' : "Lance-bombes splash"
    }
    special_ja = {
        'presser' : "ハイパープレッサー",
        'jetpack' : "ジェットパック",
        'chakuchi': "スーパーチャクチ",
        'pitcher' : "ボムピッチャ"
    }
    special_str = special_en

    special_img = {
        'presser' : "255dbac123ae410fb6418a3f9fd8fa4b.png",
        'jetpack' : "55b49f3fba5f914469c9fff532db4fd2.png",
        'chakuchi': "aa9dbd404a5d30229a9576c8930adc9c.png",
        'pitcher' : "5e78522afbc7115cf77b337e910c8798.png"
    }

    title = {
        'en' : 'Special weapons',
        'fr' : 'Armes spéciales',
        'ja' : 'スペシャルウェポン'
    }

    def to_img(key):        
        return Special.special_img[key]

    def title_str(lang):
        if lang in Special.title:
            return Special.title[lang]
        return Special.title['en']

    def set_language(self, lang):
        if lang == "en":
            self.special_str = Special.special_en
        elif lang == "fr":
            self.special_str = Special.special_fr
        elif lang == "ja":
            self.special_str = Special.special_ja
        else: #current default to en
            self.special_str = Special.special_en

    def __str__(self):
        return self.special_str[self.key]

    def to_str(key, lang):
        if lang == "en":
            return Special.special_en[key]
        elif lang == "fr":
            return Special.special_fr[key]
        elif lang == "ja":
            return Special.special_ja[key]
        else: #current default to en
            return Special.special_en[key]

    def __init__(self, id):
        self.key = self.special_ids[int(id)]


class Weapon:
    weapon_ids = { # from https://github.com/frozenpandaman/splatnet2statink/blob/master/dbs.py
        0:    'bold',                   # Sploosh-o-matic
        10:   'wakaba',                 # Splattershot Jr.
        20:   'sharp',                  # Splash-o-matic
        30:   'promodeler_mg',          # Aerospray MG
        40:   'sshooter',               # Splattershot
        50:   '52gal',                  # .52 Gal
        60:   'nzap85',                 # N-ZAP '85
        70:   'prime',                  # Splattershot Pro
        80:   '96gal',                  # .96 Gal
        90:   'jetsweeper',             # Jet Squelcher
        200:  'nova',                   # Luna Blaster
        210:  'hotblaster',             # Blaster
        220:  'longblaster',            # Range Blaster
        230:  'clashblaster',           # Clash Blaster
        240:  'rapid',                  # Rapid Blaster
        250:  'rapid_elite',            # Rapid Blaster Pro
        300:  'l3reelgun',              # L-3 Nozzlenose
        310:  'h3reelgun',              # H-3 Nozzlenose
        400:  'bottlegeyser',           # Squeezer
        1000: 'carbon',                 # Carbon Roller
        1010: 'splatroller',            # Splat Roller
        1020: 'dynamo',                 # Dynamo Roller
        1030: 'variableroller',         # Flingza Roller
        1100: 'pablo',                  # Inkbrush
        1110: 'hokusai',                # Octobrush
        2000: 'squiclean_a',            # Classic Squiffer
        2010: 'splatcharger',           # Splat Charger
        2020: 'splatscope',             # Splatterscope
        2030: 'liter4k',                # E-liter 4K
        2040: 'liter4k_scope',          # E-liter 4K Scope
        2050: 'bamboo14mk1',            # Bamboozler 14 Mk I
        2060: 'soytuber',               # Goo Tuber
        3000: 'bucketslosher',          # Slosher
        3010: 'hissen',                 # Tri-Slosher
        3020: 'screwslosher',           # Sloshing Machine
        3030: 'furo',                   # Bloblobber
        3040: 'explosher',              # Explosher
        4000: 'splatspinner',           # Mini Splatling
        4010: 'barrelspinner',          # Heavy Splatling
        4020: 'hydra',                  # Hydra Splatling
        4030: 'kugelschreiber',         # Ballpoint Splatling
        4040: 'nautilus47',             # Nautilus 47
        5000: 'sputtery',               # Dapple Dualies
        5010: 'maneuver',               # Splat Dualies
        5020: 'kelvin525',              # Glooga Dualies
        5030: 'dualsweeper',            # Dualie Squelchers
        5040: 'quadhopper_black',       # Dark Tetra Dualies
        6000: 'parashelter',            # Splat Brella
        6010: 'campingshelter',         # Tenta Brella
        6020: 'spygadget',              # Undercover Brella
        20000: 'kuma_blaster',          # Grizzco Blaster
        20010: 'kuma_brella',           # Grizzco Brella
        20020: 'kuma_charger',          # Grizzco Charger
        20030: 'kuma_slosher'           # Grizzco Slosher
    }

    weapon_en = { 
        'bold': 'Sploosh-o-matic',
        'wakaba': 'Splattershot Jr.',
        'sharp': 'Splash-o-matic',
        'promodeler_mg': 'Aerospray MG',
        'sshooter': 'Splattershot',
        '52gal': '.52 Gal',
        'nzap85': 'N-ZAP \'85',
        'prime': 'Splattershot Pro',
        '96gal': '.96 Gal',
        'jetsweeper': 'Jet Squelcher',
        'nova': 'Luna Blaster',
        'hotblaster': 'Blaster',
        'longblaster': 'Range Blaster',
        'clashblaster': 'Clash Blaster',
        'rapid': 'Rapid Blaster',
        'rapid_elite': 'Rapid Blaster Pro',
        'l3reelgun': 'L-3 Nozzlenose',
        'h3reelgun': 'H-3 Nozzlenose',
        'bottlegeyser': 'Squeezer',
        'carbon': 'Carbon Roller',
        'splatroller': 'Splat Roller',
        'dynamo': 'Dynamo Roller',
        'variableroller': 'Flingza Roller',
        'pablo': 'Inkbrush',
        'hokusai': 'Octobrush',
        'squiclean_a': 'Classic Squiffer',
        'splatcharger': 'Splat Charger',
        'splatscope': 'Splatterscope',
        'liter4k': 'E-liter 4K',
        'liter4k_scope': 'E-liter 4K Scope',
        'bamboo14mk1': 'Bamboozler 14 Mk I',
        'soytuber': 'Goo Tuber',
        'bucketslosher': 'Slosher',
        'hissen': 'Tri-Slosher',
        'screwslosher': 'Sloshing Machine',
        'furo': 'Bloblobber',
        'explosher': 'Explosher',
        'splatspinner': 'Mini Splatling',
        'barrelspinner': 'Heavy Splatling',
        'hydra': 'Hydra Splatling',
        'kugelschreiber': 'Ballpoint Splatling',
        'nautilus47': 'Nautilus 47',
        'sputtery': 'Dapple Dualies',
        'maneuver': 'Splat Dualies',
        'kelvin525': 'Glooga Dualies',
        'dualsweeper': 'Dualie Squelchers',
        'quadhopper_black': 'Dark Tetra Dualies',
        'parashelter': 'Splat Brella',
        'campingshelter': 'Tenta Brella',
        'spygadget': 'Undercover Brella',
        'kuma_blaster': 'Grizzco Blaster',
        'kuma_brella': 'Grizzco Brella',
        'kuma_charger': 'Grizzco Charger',
        'kuma_slosher': 'Grizzco Slosher'
    }

    weapon_fr = { 
        'bold': 'Marqueur lourd',
        'wakaba': 'Liquidateur Jr.',
        'sharp': 'Marqueur léger',
        'promodeler_mg': 'Aérogun',
        'sshooter': 'Liquidateur',
        '52gal': 'Calibre 2000',
        'nzap85': 'N-ZAP 85',
        'prime': 'Liquidateur Pro',
        '96gal': 'Calibre 3000',
        'jetsweeper': 'Nettoyeur XL',
        'nova': 'Proxiblaster',
        'hotblaster': 'Éclablaster',
        'longblaster': 'Éclablaster XL',
        'clashblaster': 'Rafablaster',
        'rapid': 'Turboblaster',
        'rapid_elite': 'Turboblaster Pro',
        'l3reelgun': 'Arroseur léger',
        'h3reelgun': 'Arroseur lourd',
        'bottlegeyser': 'Compresseur',
        'carbon': 'Rouleau carbone',
        'splatroller': 'Rouleau',
        'dynamo': 'Dynamo-rouleau',
        'variableroller': 'Flexi-rouleau',
        'pablo': 'Épinceau',
        'hokusai': 'Épinceau brosse',
        'squiclean_a': 'Décap\'express Alpha',
        'splatcharger': 'Concentraceur',
        'splatscope': 'Concentraceur zoom',
        'liter4k': 'Extraceur +',
        'liter4k_scope': 'Extraceur + zoom',
        'bamboo14mk1': 'Bimbamboum Mk I',
        'soytuber': 'Détubeur',
        'bucketslosher': 'Seauceur',
        'hissen': 'Dépoteur',
        'screwslosher': 'Encrifugeur',
        'furo': 'Bassineur',
        'explosher': 'Détoneur',
        'splatspinner': 'Badigeonneur XS',
        'barrelspinner': 'Badigeonneur',
        'hydra': 'Exteinteur',
        'kugelschreiber': 'Badigeonneur stylo',
        'nautilus47': 'Nautilus 47',
        'sputtery': 'Double moucheteur',
        'maneuver': 'Double encreur',
        'kelvin525': 'Double Kelvin 525',
        'dualsweeper': 'Double nettoyeur',
        'quadhopper_black': 'Double voltigeur noir',
        'parashelter': 'Para-encre',
        'campingshelter': 'Para-encre XL',
        'spygadget': 'Para-encre espion',
        'kuma_blaster': 'Blaster M. Ours SA',
        'kuma_brella': 'Para-encre M. Ours SA',
        'kuma_charger': 'Fusil M. Ours SA',
        'kuma_slosher': 'Seau M. Ours SA'
    }

    weapon_ja = { 
        'bold': 'ボールドマーカー',
        'wakaba': 'わかばシューター',
        'sharp': 'シャープマーカー',
        'promodeler_mg': 'プロモデラーMG',
        'sshooter': 'スプラシューター',
        '52gal': '.52ガロン',
        'nzap85': 'N-ZAP85',
        'prime': 'プライムシューター',
        '96gal': '.96ガロン',
        'jetsweeper': 'ジェットスイーパー',
        'nova': 'ノヴァブラスター',
        'hotblaster': 'ホットブラスター',
        'longblaster': 'ロングブラスター',
        'clashblaster': 'クラッシュブラスター',
        'rapid': 'ラピッドブラスター',
        'rapid_elite': 'Rブラスターエリート',
        'l3reelgun': 'L3リールガン',
        'h3reelgun': 'H3リールガン',
        'bottlegeyser': 'ボトルガイザー',
        'carbon': 'カーボンローラー',
        'splatroller': 'スプラローラー',
        'dynamo': 'ダイナモローラー',
        'variableroller': 'ヴァリアブルローラー',
        'pablo': 'パブロ',
        'hokusai': 'ホクサイ',
        'squiclean_a': 'スクイックリンα',
        'splatcharger': 'スプラチャージャー',
        'splatscope': 'スプラスコープ',
        'liter4k': 'リッター4K',
        'liter4k_scope': '4Kスコープ',
        'bamboo14mk1': '14式竹筒銃・甲',
        'soytuber': 'ソイチューバー',
        'bucketslosher': 'バケットスロッシャー',
        'hissen': 'ヒッセン',
        'screwslosher': 'スクリュースロッシャー',
        'furo': 'オーバーフロッシャー',
        'explosher': 'エクスプロッシャー',
        'splatspinner': 'スプラスピナー',
        'barrelspinner': 'バレルスピナー',
        'hydra': 'ハイドラント',
        'kugelschreiber': 'クーゲルシュライバー',
        'nautilus47': 'ノーチラス47',
        'sputtery': 'スパッタリー',
        'maneuver': 'スプラマニューバー',
        'kelvin525': 'ケルビン525',
        'dualsweeper': 'デュアルスイーパー',
        'quadhopper_black': 'クアッドホッパーブラック',
        'parashelter': 'パラシェルター',
        'campingshelter': 'キャンピングシェルター',
        'spygadget': 'スパイガジェット',
        'kuma_blaster': 'クマサン印のブラスター',
        'kuma_brella': 'クマサン印のシェルター',
        'kuma_charger': 'クマサン印のチャージャー',
        'kuma_slosher': 'クマサン印のスロッシャー'
    }

    weapon_str = weapon_en

    weapon_img = { 
        'bold': '44e5c595ef678318da4f0bf5dd14ebf1.png',
        'wakaba': '4d301a50dc81317f9fbc99bdb231eb14.png',
        'sharp': 'c799d9df72e924f3b862fb5a3425ccda.png',
        'promodeler_mg': '6fde22a13edc4e911166400520ce176d.png',
        'sshooter': '37a4ff7f54573224b15be659204d8b64.png',
        '52gal': '6f321faf4070a1fbe969dfd559bef810.png',
        'nzap85': 'bf4bd4904ccaf182640d7bc1d7be6f0f.png',
        'prime': '78046a88e21a9817c8361e4e0e76f21f.png',
        '96gal': '2fdc89e7d1f73b95c7126741d77f5f2b.png',
        'jetsweeper': '86e03b524c541b36e5ada7d83751195e.png',
        'nova': 'd52bb88c0420ad10c18209d72701851b.png',
        'hotblaster': 'c038437cda5cea47ecc91f932e702255.png',
        'longblaster': '48e0088c0c2298168bb31046d51b723b.png',
        'clashblaster': '1295814d088991f2ed8d010c08076643.png',
        'rapid': '8724c342ee918c6794d90ac974296f2e.png',
        'rapid_elite': '7ecbcc9e27757b01b3cd3c6504523d36.png',
        'l3reelgun': 'd8676b5fe176261e835829f75d232a92.png',
        'h3reelgun': 'f437ae53be930e832113b9b46486e2fd.png',
        'bottlegeyser': '82a527238d4033b439a793fd79cc72d7.png',
        'carbon': '63aa1b065b96748328ac1edd920ebc82.png',
        'splatroller': '4c10384af88fa84ddbe4b3a49ce09ef1.png',
        'dynamo': 'f9ae7102ead909b638a7e42296ec75e3.png',
        'variableroller': 'bef0d7bdf0d88f8dbfa5202b2198aa7d.png',
        'pablo': '1966a5e3acd4e4f2a272783d1412bb96.png',
        'hokusai': '153659e8a12a89df89ca3e49deae7817.png',
        'squiclean_a': '06ca523f0a24336b090ba51039347b95.png',
        'splatcharger': '9e9224e92b566cf1bc85041c66881451.png',
        'splatscope': '8c265d0854f9528f288a3b75f716ae04.png',
        'liter4k': '0de38cdd10e341859fcf62ff5c336cf5.png',
        'liter4k_scope': '410c9543d0bf6b7a4911bc9a648e3be3.png',
        'bamboo14mk1': '5cae23798004706003eb0fc628cbf6de.png',
        'soytuber': '6e906bcaf46ce643f6444cb9d9e227ce.png',
        'bucketslosher': '6be9e6699ce1f14812444ebf3c631878.png',
        'hissen': '13d3aa3150e251c8cfc346286cee3184.png',
        'screwslosher': 'e8fa1c6c68e14fd97bd7b8f59c454527.png',
        'furo': 'eff28f2ee7c61650589222dbcacad8ac.png',
        'explosher': '065cc815cafc1d998528d3be4f42b843.png',
        'splatspinner': '05514967f03df66c6da66b6c42a9a0e7.png',
        'barrelspinner': 'bf5be6b2e1f5af728b02b7969070e419.png',
        'hydra': '7f0c5e62203cddd0b4232b4b50f21d1f.png',
        'kugelschreiber': '0bbf50aaf07c642735f8b3f40129f1c0.png',
        'nautilus47': '3e4d7514661e746a29dfa84b0d3a31fe.png',
        'sputtery': 'b84494290ded8366683525533ea1753c.png',
        'maneuver': 'b732df559c0a57f73a3469258b2ad394.png',
        'kelvin525': '7384a439a11c3c9fce0ac3c36cfeabe4.png',
        'dualsweeper': '7705de97e43f430a518f2ac73a779ffc.png',
        'quadhopper_black': '89ad35f13934953857155710a41b127b.png',
        'parashelter': '3a11f01b60ef06ffe5d269bf18c8e200.png',
        'campingshelter': 'b1e00e434e2a98079574cd6c081f0364.png',
        'spygadget': 'ee8259718e35e75c1b3cfbf4fef828bf.png',
        'kuma_blaster': '271f75dad44c6180ed86a10fcb0da9a9.png',
        'kuma_brella': 'b7d127f4c7d9b76d9e65c2467034628a.png',
        'kuma_charger': '77cdac16e8ef5004a9a63d7bf885d915.png',
        'kuma_slosher': '7ef8cab1679ad22d9532c6f8f6d5372d.png'
    }

    title = {
        'en' : 'Weapons',
        'fr' : 'Armes',
        'ja' : 'ブキ'
    }

    def title_str(lang):
        if lang in Weapon.title:
            return Weapon.title[lang]
        return Weapon.title['en']

    def to_img(key):        
        return Weapon.weapon_img[key]


    def set_language(self, lang):
        if lang == "en":
            self.weapon_str = Weapon.weapon_en
        elif lang == "fr":
            self.special_str = Weapon.weapon_fr
        elif lang == "ja":
            self.weapon_str = Weapon.weapon_ja
        else: #current default to en
            self.weapon_str = Weapon.weapon_en

    def __init__(self, id):
        self.key = self.weapon_ids[int(id)]

    def __str__(self):
        return self.weapon_str[self.key]

    def to_str(key, lang="en"):
        if lang == "en":
            return Weapon.weapon_en[key]
        elif lang == "fr":
            return Weapon.weapon_fr[key]
        elif lang == "ja":
            return Weapon.weapon_ja[key]
        else: #current default to en
            return Weapon.weapon_en[key]

class SalmonBossList:
    boss_names = { "6"  : "sakelien-bomber", "9"  : "sakelien-cup-twins",
                   "12" : "sakelien-shield", "13" : "sakelien-snake",
                   "14" : "sakelien-tower",  "15" : "sakediver",
                   "21" : "sakerocket",      "3"  :  "sakelien-golden",
                   "16" : "sakedozer"}
    boss_en = { "sakelien-golden"    : "Goldie"   , "sakelien-bomber" : "Steelhead",
                "sakelien-cup-twins" : "Flyfish"  , "sakelien-shield" : "Scrapper",
                "sakelien-snake"     : "Steel eel", "sakelien-tower"  : "Stinger",
                "sakediver"          : "Maws"     , "sakedozer"       : "Griller",
                "sakerocket"         : "Drizzler" }
    boss_fr = { "sakelien-golden"    : "Dorax"    , "sakelien-bomber" : "Tête-de-pneu",
                "sakelien-cup-twins" : "Aéro Ben" , "sakelien-shield" : "Bricabrute",
                "sakelien-snake"     : "Carnacier", "sakelien-tower"  : "Marmirador",
                "sakediver"          : "Gobb"     , "sakedozer"       : "Barbeurk",
                "sakerocket"         : "Crachin" }
    boss_ja = { "sakelien-golden"    : "キンシャケ", "sakelien-bomber" : "バクダン",
                "sakelien-cup-twins" : "カタパッド", "sakelien-shield" : "テッパン",
                "sakelien-snake"     : "ヘビ",      "sakelien-tower"  : "タワー",
                "sakediver"          : "モグラ",    "sakedozer"       : "グリル",
                "sakerocket"         : "コウモリ" }
    
    boss_str = boss_en

    def get_boss_name(key, lang="en"):
        if lang == "en":
            return SalmonBossList.boss_en[key]
        elif lang == "fr":
            return SalmonBossList.boss_fr[key]
        elif lang == "ja":
            return SalmonBossList.boss_ja[key]
        return SalmonBossList.boss_en[key]

    def set_language(self, lang):
        if lang == "en":
            self.boss_str = SalmonBossList.boss_en
        elif lang == "fr":
            self.boss_str = SalmonBossList.boss_fr
        elif lang == "ja":
            self.boss_str = SalmonBossList.boss_ja
        else: #current default to en
            self.boss_str = SalmonBossList.boss_en

    def sum_boss(self):
        return sum(self.b_list.values())

    def __str__(self):
        return str(self.b_list)


    def __init__(self, gamedict, fname):
        self.b_list = {}
        for key, name in self.boss_names.items():
            self.b_list[name] = gamedict[key]['count']
            if name != gamedict[key]['boss']['key']:
                print("ERROR in game " + fname)


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
    str_buffer.write(f"<td class='daymaxeggs'><span title='min: {min(stats.day_geggs):6.2f}'>{max(stats.day_geggs):6.2f}</span></td>")
    str_buffer.write(f"<td class='dayavgeggs'><span title='stddev: {pstdev(stats.day_geggs):6.2f}'>{mean(stats.day_geggs):6.2f}</span></td></tr>\n")
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
    str_buffer.write(f"<td class='nightmaxeggs'><span title='min: {min(stats.night_geggs):6.2f}'>{max(stats.night_geggs):6.2f}</span></td>")
    str_buffer.write(f"<td class='nightavgeggs'><span title='stddev: {pstdev(stats.night_geggs):6.2f}'>{mean(stats.night_geggs):6.2f}</span></td></tr>\n")
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
    str_buffer.write(f"<td class='hightidemaxeggs'><span title='min: {min(stats.ht_geggs):6.2f}'>{max(stats.ht_geggs):6.2f}</span></td>")
    str_buffer.write(f"<td class='hightideavgeggs'><span title='stddev: {pstdev(stats.ht_geggs):6.2f}'>{mean(stats.ht_geggs):6.2f}</span></td></tr>\n")
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
    str_buffer.write(f"<td class='normaltidemaxeggs'><span title='min: {min(stats.nt_geggs):6.2f}'>{max(stats.nt_geggs):6.2f}</span></td>")
    str_buffer.write(f"<td class='normalideavgeggs'><span title='stddev: {pstdev(stats.nt_geggs):6.2f}'>{mean(stats.nt_geggs):6.2f}</span></td></tr>\n")
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
    str_buffer.write(f"<td class='lowtidemaxeggs'><span title='min: {min(stats.lt_geggs):6.2f}'>{max(stats.lt_geggs):6.2f}</span></td>")
    str_buffer.write(f"<td class='lowtideavgeggs'><span title='stddev: {pstdev(stats.lt_geggs):6.2f}'>{mean(stats.lt_geggs):6.2f}</span></td></tr>\n")
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

