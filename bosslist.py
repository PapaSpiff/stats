
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

