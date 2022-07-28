from time import strftime, gmtime

class Rotation:
    start_time:int = 0
    end_time:int = 0
    rotation_id: str
    key: str

    img_to_idx = {
        '/images/coop_stage/6d68f5baa75f3a94e5e9bfb89b82e7377e3ecd2c.png' : 'outpost',
        '/images/coop_stage/e07d73b7d9f0c64e552b34a2e6c29b8564c63388.png' : 'bay',
        '/images/coop_stage/50064ec6e97aac91e70df5fc2cfecf61ad8615fd.png' : 'ark',
        '/images/coop_stage/e9f7c7b35e6d46778cd3cbc0d89bd7e1bc3be493.png' : 'yard',
        '/images/coop_stage/65c68c6f0641cc5654434b78a6f10b0ad32ccdee.png' : 'grounds'
    }
    idx_to_img = {
        'outpost' : "f0d891a6a76c551b05fe935a3182029e.png",
        'bay' : "0f395e81fa046b86c83662cfcd344409.png",
        'ark' : "f2f0410d58297b9fed54fddd0c390ab7.png",
        'yard' : "c9e683fa389effd22ab99aa603b0c7d4.png",
        'grounds' : "6f63dba901ac7c041437bf0c16588479.png"
    }
    stages_en = {
        'outpost' : "Lost Outpost",
        'bay' : "Marooner's Bay",
        'ark' : "Ruins of Ark Polaris",
        'yard' : "Salmonid Smokeyard",
        'grounds' : "Spawning Grounds"
    }
    stages_fr = {
        'outpost' : "Baraque Barracuda",
        'bay' : "Épave des braves",
        'ark' : "Station Polaris",
        'yard' : "Fumoir Sans-Espoir",
        'grounds' : "Barrage salmonoïde"
    }

    stages_ja = {
        'outpost' : "海上集落シャケト場",
        'bay' : "難破船ドン・ブラコ",
        'ark' : "朽ちた箱舟 ポラリス",
        'yard' : "トキシラズいぶし工房",
        'grounds' : "シェケナダム"
    }

    other_en = {
        'title' : "Rotation",
    }
    other_fr = {
        'title' : "Rotation",
    }
    other_ja = {
        'title' : "スケジュール",
    }

    def to_img(key: str) -> str:        
        return Rotation.idx_to_img[key]

    def other_str(key: str, lang: str) -> str:
        if lang == "en":
            return Rotation.other_en[key]
        elif lang == "fr":
            return Rotation.other_fr[key]
        elif lang == "ja":
            return Rotation.other_ja[key]
        else: #current default to en
            return Rotation.other_en[key]

    def to_str(key: str, lang: str) -> str:
        if lang == "en":
            return Rotation.waves_en[key]
        elif lang == "fr":
            return Rotation.waves_fr[key]
        elif lang == "ja":
            return Rotation.waves_ja[key]
        else: #current default to en
            return Rotation.waves_en[key]

    def __init__(self: 'Rotation', raw_rotation: dict) -> None:
        # We use the image to derive the key as we don't have any id, and would need to rely on 
        # implementing all languages
        self.key         = Rotation.img_to_idx[raw_rotation['stage']['image']]
        self.start_time  = raw_rotation['start_time']
        self.end_time    = raw_rotation['end_time']
        self.rotation_id = strftime('%Y%m%d%H', gmtime(self.start_time))

    def __eq__(self: 'Rotation', other: 'Rotation'):
        if isinstance(other, self.__class__):
            return self.start_time == other.start_time
        else:
            return False

    def __ne__(self: 'Rotation', other: 'Rotation'):
        return not self.__eq__(other)
