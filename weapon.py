from typing import Union

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

    def title_str(lang: str) -> str:
        if lang in Weapon.title:
            return Weapon.title[lang]
        return Weapon.title['en']

    def to_img(key: str) -> str:        
        return Weapon.weapon_img[key]


    def set_language(self: 'Weapon', lang: str) -> str:
        if lang == "en":
            self.weapon_str = Weapon.weapon_en
        elif lang == "fr":
            self.special_str = Weapon.weapon_fr
        elif lang == "ja":
            self.weapon_str = Weapon.weapon_ja
        else: #current default to en
            self.weapon_str = Weapon.weapon_en

    def __init__(self: 'Weapon', id: Union[list, bool]) -> None:
        self.key = self.weapon_ids[int(id)]

    def __str__(self: 'Weapon') -> str:
        return self.weapon_str[self.key]

    def to_str(key: str, lang:str = "en") -> str:
        if lang == "en":
            return Weapon.weapon_en[key]
        elif lang == "fr":
            return Weapon.weapon_fr[key]
        elif lang == "ja":
            return Weapon.weapon_ja[key]
        else: #current default to en
            return Weapon.weapon_en[key]
