from statistics import mean, pstdev
import jinja2
from player import Player
from rotation import Rotation
from gamesession import GameSession
from weapon import Weapon
from special import Special
from wave import Wave
from jinja2 import Environment, FileSystemLoader
from typing import Union
from time import strftime, gmtime

def epoch_to_gmt_str(epoch: Union[str,int]) -> str:
    return strftime('%Y-%m-%d %H:%M:%S %Z', gmtime(int(epoch)))

def weapon_key_to_img(key: str) -> str:
    return Weapon.to_img(key)

def special_key_to_img(key: str) -> str:
    return Special.to_img(key)

def weapon_name(key: str, lang: str="en") -> str:
    return Weapon.to_str(key, lang)

def special_name(key: str, lang: str="en") -> str:
    return Special.to_str(key, lang)

def wave_name(key: str, lang: str="en") -> str:
    return Wave.to_str(key, lang)

def wave_other(key: str, lang: str="en") -> str:
    return Wave.other_str(key, lang)

def html_player_rotation(player: Player, rotation: Rotation, session: GameSession, lang: str="en") -> str:
    env = Environment(loader=FileSystemLoader("tpl/", encoding='utf-8'))
    env.filters["epochgmttime"] = epoch_to_gmt_str
    env.filters["weapontoimg"]  = weapon_key_to_img
    env.filters["weaponname"]   = weapon_name
    env.filters["specialtoimg"] = special_key_to_img
    env.filters["specialname"]  = special_name
    env.filters["wavename"]     = wave_name
    env.filters["waveother"]    = wave_other
    env.filters["mean"]         = mean
    env.filters["pstdev"]       = pstdev
    tpl = env.get_template("player_rotation.html")
    rotation.set_language(lang)
    return tpl.render(player=player, rotation=rotation, session=session, 
                    specialtitle=Special.title_str(lang), weapontitle=Weapon.title_str(lang),
                    waves=Wave(),
                    lang=lang)
