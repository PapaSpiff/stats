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
        'wavetype' : "Wave Type",
        'titlemax' : "Team total Golden Eggs",
        'average'  : "Average",
        'maximum'  : "Maximum",
        'max'      : "max",
        'minimum'  : "Minimum",
        'min'      : "min",
        'occurence': "occurences",
        'median'   : "median",
        'stddev'   : "std.dev",
    }
    other_fr = {
        'title' : "Vagues",
        'wavetype' : "Type de Vague",
        'titlemax' : "Totaux d'œufs dorés d'équipe",
        'average'  : "Moyenne",
        'maximum'  : "Maximum",
        'max'      : "max",
        'minimum'  : "Minimum",
        'min'      : "min",
        'occurence': "apparitions",
        'median'   : "médian",
        'stddev'   : "éc.type"
    }
    other_ja = {
        'title' : "WAVE",
        'wavetype' : "WAVE",
        'titlemax' : "チーム合計の金イクラ納品数",
        'average'  : "平均",
        'maximum'  : "最大",
        'max'      : "最大",
        'minimum'  : "最小",
        'min'      : "最小",
        'occurence': "出現数",
        'median'   : "中央",
        'stddev'   : "標準偏差",
    }

    def other_str(key: str, lang: str) -> str:
        if lang == "en":
            return Wave.other_en[key]
        elif lang == "fr":
            return Wave.other_fr[key]
        elif lang == "ja":
            return Wave.other_ja[key]
        else: #current default to en
            return Wave.other_en[key]

    def to_str(key: str, lang: str) -> str:
        if lang == "en":
            return Wave.waves_en[key]
        elif lang == "fr":
            return Wave.waves_fr[key]
        elif lang == "ja":
            return Wave.waves_ja[key]
        else: #current default to en
            return Wave.waves_en[key]

