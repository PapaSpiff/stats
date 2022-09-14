
class Special:
    special_ids = {
        2: 'pitcher',
        7: 'presser',
        8: 'jetpack', 
        9: 'chakuchi',
        # NW
        20014: 'tripleinkstrike',
        20013: 'reefslider',
        20012: 'crabtank',
        20009: 'killerwail51',
        20007: 'wavebreaker',
        20006: 'booyahbomb',
        20010: 'jetpack', #same as SP2 '8'
    }
    special_en = {
        'presser' : "Sting Ray",
        'jetpack' : "Inkjet",
        'chakuchi': "Splashdown",
        'pitcher' : "Bomb Launcher",
        # NW
        'tripleinkstrike' : "Triple Inkstrike",
        'reefslider' : "Reefslider",
        'crabtank'   : "Crab Tank",
        'killerwail51' : "Killer Wail 5.1",
        'wavebreaker' : "Wave Breaker",
        'booyahbomb' : "Booyah Bomb",
    }
    special_fr = {
        'presser' : "Pigmalance",
        'jetpack' : "Chromo-jet",
        'chakuchi': "Choc chromatique",
        'pitcher' : "Lance-bombes splash",
        #NW
        'tripleinkstrike' : "Trimissile tornade",
        'reefslider' : "Cavalsquale",
        'crabtank' : "Crabe d'assaut",
        'killerwail51': "Haut-perceur 5.1",
        'wavebreaker' : "Sonar paf",
        'booyahbomb' : "Jolizator",
    }
    special_ja = {
        'presser' : "ハイパープレッサー",
        'jetpack' : "ジェットパック",
        'chakuchi': "スーパーチャクチ",
        'pitcher' : "ボムピッチャ",
        #NW
        'tripleinkstrike' : "トリプルトルネード",
        'reefslider' : "サメライド",
        'crabtank' : "カニタンク",
        'killerwail51' : "メガホンレーザー5.1ch",
        'wavebreaker' : "ホップソナー",
        'booyahbomb' : "ナイスダマ",
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

    def to_img(key: str) -> str:        
        return Special.special_img[key]

    def title_str(lang: str) -> str:
        if lang in Special.title:
            return Special.title[lang]
        return Special.title['en']

    def set_language(self: 'Special', lang: str) -> None:
        if lang == "en":
            self.special_str = Special.special_en
        elif lang == "fr":
            self.special_str = Special.special_fr
        elif lang == "ja":
            self.special_str = Special.special_ja
        else: #current default to en
            self.special_str = Special.special_en

    def __str__(self: 'Special') -> str:
        return self.special_str[self.key]

    def to_str(key: str, lang: str) -> str:
        if lang == "en":
            return Special.special_en[key]
        elif lang == "fr":
            return Special.special_fr[key]
        elif lang == "ja":
            return Special.special_ja[key]
        else: #current default to en
            return Special.special_en[key]

    def __init__(self: 'Special', id: str) -> None:
        self.key = self.special_ids[int(id)]
