from wave import Wave
from special import Special
from weapon import Weapon
from bosslist import SalmonBossList
from gamesession import GameSession
from statistics import mean as mean
from statistics import pstdev as pstdev
from statistics import quantiles as quantiles
from io import StringIO


def print_specials_html(stats: GameSession, lang: str) -> str:
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
            str_buffer.write(f"<img class='special-img' src='/images/special/{Special.to_img(special)}' alt='{Special.to_str(special, lang)}'> ")
            str_buffer.write(f"<span class='special-name'>{Special.to_str(special, lang)}</span> : ")
            str_buffer.write(f"<span class='special-count' title='special occurence'>{stats.my_specials[special]:3.0f}</span>")
#            str_buffer.write(f" <span class='special-percent'>({stats.my_specials[special]/all_scores:5.2%})</span>")
            str_buffer.write(f" <span class='special-usage-percent' title='special usage'>({stats.us_specials[special]/(2*stats.my_specials[special]):5.2%})</span>")
            str_buffer.write("</div>\n")
            specialnum += 1
    str_buffer.write("</div>\n</div>\n</div>\n")
    return str_buffer.getvalue()

def print_weapons_html(stats: GameSession, lang: str) -> str:
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
        str_buffer.write(f"<img class='weapon-img' src='/images/weapon/{Weapon.to_img(weapon)}' alt='{Weapon.to_str(weapon, lang)}'> ")
        str_buffer.write(f"<span class='weapon-name'>{Weapon.to_str(weapon, lang)}</span> : ")
        str_buffer.write(f"<span class='weapon-count' title='weapon occurence'>{weaponoccurence:3.0f}</span>")
        str_buffer.write(f" <span class='weapon-occurence-percent' title='percentage of all occurences'>({weaponoccurence/all_waves:5.2%})</span>")
        str_buffer.write("</div>\n")
        if weaponnum < 5:
            weaponnum += 1
    str_buffer.write("</div>\n</div>\n</div>\n")
    return str_buffer.getvalue()


def print_waves_html(stats: GameSession, lang: str) -> str:
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
    if (stats.wav_day > 0):
        str_buffer.write(f"<td class='daymaxeggs'><span title='min: {min(stats.day_geggs):6.2f}'>{max(stats.day_geggs):6.2f}</span></td>")
        str_buffer.write(f"<td class='dayavgeggs'><span title='stddev: {pstdev(stats.day_geggs):6.2f}'>{mean(stats.day_geggs):6.2f}</span></td></tr>\n")
    else:
        str_buffer.write(f"<td class='daymaxeggs'><span title='min: -'>-</span></td>")
        str_buffer.write(f"<td class='dayavgeggs'><span title='stddev: -'>-</span></td></tr>\n")
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
    if (stats.wav_night > 0):
        str_buffer.write(f"<td class='nightmaxeggs'><span title='min: {min(stats.night_geggs):6.2f}'>{max(stats.night_geggs):6.2f}</span></td>")
        str_buffer.write(f"<td class='nightavgeggs'><span title='stddev: {pstdev(stats.night_geggs):6.2f}'>{mean(stats.night_geggs):6.2f}</span></td></tr>\n")
    else:
        str_buffer.write(f"<td class='nightmaxeggs'><span title='min: -'>-</span></td>")
        str_buffer.write(f"<td class='nightavgeggs'><span title='stddev: -'>-</span></td></tr>\n")
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
    if (stats.wav_ht > 0):
        str_buffer.write(f"<td class='hightidemaxeggs'><span title='min: {min(stats.ht_geggs):6.2f}'>{max(stats.ht_geggs):6.2f}</span></td>")
        str_buffer.write(f"<td class='hightideavgeggs'><span title='stddev: {pstdev(stats.ht_geggs):6.2f}'>{mean(stats.ht_geggs):6.2f}</span></td></tr>\n")
    else:
        str_buffer.write(f"<td class='hightidemaxeggs'><span title='min: -'>-</span></td>")
        str_buffer.write(f"<td class='hightideavgeggs'><span title='stddev: -'>-</span></td></tr>\n")
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
    if (stats.wav_nt > 0):
        str_buffer.write(f"<td class='normaltidemaxeggs'><span title='min: {min(stats.nt_geggs):6.2f}'>{max(stats.nt_geggs):6.2f}</span></td>")
        str_buffer.write(f"<td class='normalideavgeggs'><span title='stddev: {pstdev(stats.nt_geggs):6.2f}'>{mean(stats.nt_geggs):6.2f}</span></td></tr>\n")
    else:
        str_buffer.write(f"<td class='normaltidemaxeggs'><span title='min: -'>-</span></td>")
        str_buffer.write(f"<td class='normalideavgeggs'><span title='stddev: -'>-</span></td></tr>\n")
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
    if (stats.wav_lt > 0):
        str_buffer.write(f"<td class='lowtidemaxeggs'><span title='min: {min(stats.lt_geggs):6.2f}'>{max(stats.lt_geggs):6.2f}</span></td>")
        str_buffer.write(f"<td class='lowtideavgeggs'><span title='stddev: {pstdev(stats.lt_geggs):6.2f}'>{mean(stats.lt_geggs):6.2f}</span></td></tr>\n")
    else:
        str_buffer.write(f"<td class='lowtidemaxeggs'><span title='min: -'>-</span></td>")
        str_buffer.write(f"<td class='lowtideavgeggs'><span title='stddev: -'>-</span></td></tr>\n")
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
    if (stats.wav_night > 0):
        str_buffer.write("<table id='nightwavemax'>\n<thead><tr>")
        str_buffer.write(f"<th>{Wave.other_str('titlemax',lang)}</th><th scope='col'>{Wave.to_str('tide',lang)}</th><th scope='col'>%</th><th scope='col'>Max Eggs</th><th scope='col'>Average</th></tr></thead><tbody>")
        # moship
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
            str_buffer.write(f"<td class='moshipavg'><span title='stddev: {pstdev(moship_g):.2f}'>{mean(moship_g):.2f}</span></td></tr>")
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
                str_buffer.write(f"<td class='moshipavg'><span title='stddev: {pstdev(stats.ht_moship_g):.2f}'>{mean(stats.ht_moship_g):.2f}</span></td></tr>")
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
                str_buffer.write(f"<td class='moshipavg'><span title='stddev: {pstdev(stats.nt_moship_g):.2f}'>{mean(stats.nt_moship_g):.2f}</span></td></tr>")
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
                str_buffer.write(f"<td class='moshipavg'><span title='stddev: {pstdev(stats.lt_moship_g):.2f}'>{mean(stats.lt_moship_g):.2f}</span></td></tr>")
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
            str_buffer.write(f"<td class='rushavg'><span title='stddev: {pstdev(rush_g):.2f}'>{mean(rush_g):.2f}</span></td></tr>")
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
                str_buffer.write(f"<td class='rushavg'><span title='stddev: {pstdev(stats.ht_rush_g):.2f}'>{mean(stats.ht_rush_g):.2f}</span></td></tr>")
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
                str_buffer.write(f"<td class='rushavg'><span title='stddev: {pstdev(stats.nt_rush_g):.2f}'>{mean(stats.nt_rush_g):.2f}</span></td></tr>")
        # seek
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
            str_buffer.write(f"<td class='seekavg'><span title='stddev: {pstdev(seek_g):.2f}'>{mean(seek_g):.2f}</span></td></tr>")
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
                str_buffer.write(f"<td class='seekavg'><span title='stddev: {pstdev(stats.ht_seek_g):.2f}'>{mean(stats.ht_seek_g):.2f}</span></td></tr>")
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
                str_buffer.write(f"<td class='seekavg'><span title='stddev: {pstdev(stats.nt_seek_g):.2f}'>{mean(stats.nt_seek_g):.2f}</span></td></tr>")
        # grillers
        if (stats.ev_grills > 0):
            rpan = 1
            if (stats.ht_grills > 0):
                rpan += 1
            if (stats.nt_grills > 0):
                rpan += 1
            str_buffer.write(f"<tr><th class='grillers' rowspan='{rpan}'>{Wave.to_str('griller', lang)}</th>")
            str_buffer.write(f"<td></td>")
            ev_pct = stats.ev_grills / stats.wavetotal
            if (ev_pct * 100) > (Wave.grill_avg + Wave.night_wave_percent_max):
                str_buffer.write(f"<td class='grillpct'><span class='statshigh' title='{Wave.grill_avg/100:3.2%}'>{ev_pct:3.2%}</span></td>")
            elif (ev_pct * 100) < (Wave.grill_avg - Wave.night_wave_percent_max):
                str_buffer.write(f"<td class='grillpct'><span class='statslow' title='{Wave.grill_avg/100:3.2%}'>{ev_pct:3.2%}</span></td>")
            else:
                str_buffer.write(f"<td class='grillpct'><span class='statsnormal' title='{Wave.grill_avg/100:3.2%}'>{ev_pct:3.2%}</span></td>")
            grill_g = stats.ht_grills_g + stats.nt_grills_g
            str_buffer.write(f"<td class='grillmax'><span title='min: {min(grill_g)}'>{max(grill_g)}</span></td>")
            str_buffer.write(f"<td class='grillavg'><span title='stddev: {pstdev(grill_g):.2f}'>{mean(grill_g):.2f}</span></td></tr>")
            if (stats.ht_grills > 0):
                str_buffer.write(f"<tr><td>{Wave.to_str('high', lang)}</td>")
                ev_pct = stats.ht_grills / stats.wavetotal
                if (ev_pct * 100) > (Wave.grill_ht_avg + Wave.night_wave_percent_max):
                    str_buffer.write(f"<td class='grillpct'><span class='statshigh' title='{Wave.grill_ht_avg/100:3.2%}'>{ev_pct:3.2%}</span></td>")
                elif (ev_pct * 100) < (Wave.grill_ht_avg - Wave.night_wave_percent_max):
                    str_buffer.write(f"<td class='grillpct'><span class='statslow' title='{Wave.grill_ht_avg/100:3.2%}'>{ev_pct:3.2%}</span></td>")
                else:
                    str_buffer.write(f"<td class='grillpct'><span class='statsnormal' title='{Wave.grill_ht_avg/100:3.2%}'>{ev_pct:3.2%}</span></td>")
                str_buffer.write(f"<td class='grillmax'><span title='min: {min(stats.ht_grills_g)}'>{max(stats.ht_grills_g)}</span></td>")
                str_buffer.write(f"<td class='grillavg'><span title='stddev: {pstdev(stats.ht_grills_g):.2f}'>{mean(stats.ht_grills_g):.2f}</span></td></tr>")
            if (stats.nt_grills > 0):
                str_buffer.write(f"<tr><td>{Wave.to_str('normal', lang)}</td>")
                ev_pct = stats.nt_grills / stats.wavetotal
                if (ev_pct * 100) > (Wave.grill_nt_avg + Wave.night_wave_percent_max):
                    str_buffer.write(f"<td class='grillpct'><span class='statshigh' title='{Wave.grill_nt_avg/100:3.2%}'>{ev_pct:3.2%}</span></td>")
                elif (ev_pct * 100) < (Wave.grill_nt_avg - Wave.night_wave_percent_max):
                    str_buffer.write(f"<td class='grillpct'><span class='statslow' title='{Wave.grill_nt_avg/100:3.2%}'>{ev_pct:3.2%}</span></td>")
                else:
                    str_buffer.write(f"<td class='grillpct'><span class='statsnormal' title='{Wave.grill_nt_avg/100:3.2%}'>{ev_pct:3.2%}</span></td>")
                str_buffer.write(f"<td class='grillmax'><span title='min: {min(stats.nt_grills_g)}'>{max(stats.nt_grills_g)}</span></td>")
                str_buffer.write(f"<td class='grillavg'><span title='stddev: {pstdev(stats.nt_grills_g):.2f}'>{mean(stats.nt_grills_g):.2f}</span></td></tr>")
        # TODO fog
        if (stats.ev_fog > 0):
            rpan = 1
            if (stats.ht_fog > 0):
                rpan += 1
            if (stats.nt_fog > 0):
                rpan += 1
            if (stats.lt_fog > 0):
                rpan += 1
            str_buffer.write(f"<tr><th class='mothership' rowspan='{rpan}'>{Wave.to_str('fog', lang)}</th>")
            str_buffer.write(f"<td></td>")
            ev_pct = stats.ev_fog / stats.wavetotal
            if (ev_pct * 100) > (Wave.fog_avg + Wave.night_wave_percent_max):
                str_buffer.write(f"<td class='fogpct'><span class='statshigh' title='{Wave.fog_avg/100:3.2%}'>{ev_pct:3.2%}</span></td>")
            elif (ev_pct * 100) < (Wave.fog_avg - Wave.night_wave_percent_max):
                str_buffer.write(f"<td class='fogpct'><span class='statslow' title='{Wave.fog_avg/100:3.2%}'>{ev_pct:3.2%}</span></td>")
            else:
                str_buffer.write(f"<td class='fogpct'><span class='statsnormal' title='{Wave.fog_avg/100:3.2%}'>{ev_pct:3.2%}</span></td>")
            fog_g = stats.ht_fog_g + stats.nt_fog_g + stats.lt_fog_g
            str_buffer.write(f"<td class='fogmax'><span title='min: {min(fog_g)}'>{max(fog_g)}</span></td>")
            str_buffer.write(f"<td class='fogavg'><span title='stddev: {pstdev(fog_g):.2f}'>{mean(fog_g):.2f}</span></td></tr>")
            if (stats.ht_fog > 0):
                str_buffer.write(f"<tr><td>{Wave.to_str('high', lang)}</td>")
                ev_pct = stats.ht_fog / stats.wavetotal
                if (ev_pct * 100) > (Wave.fog_ht_avg + Wave.night_wave_percent_max):
                    str_buffer.write(f"<td class='fogpct'><span class='statshigh' title='{Wave.fog_ht_avg/100:3.2%}'>{ev_pct:3.2%}</span></td>")
                elif (ev_pct * 100) < (Wave.fog_ht_avg - Wave.night_wave_percent_max):
                    str_buffer.write(f"<td class='fogpct'><span class='statslow' title='{Wave.fog_ht_avg/100:3.2%}'>{ev_pct:3.2%}</span></td>")
                else:
                    str_buffer.write(f"<td class='fogpct'><span class='statsnormal' title='{Wave.fog_ht_avg/100:3.2%}'>{ev_pct:3.2%}</span></td>")
                str_buffer.write(f"<td class='fogmax'><span title='min: {min(stats.ht_fog_g)}'>{max(stats.ht_fog_g)}</span></td>")
                str_buffer.write(f"<td class='fogavg'><span title='stddev: {pstdev(stats.ht_fog_g):.2f}'>{mean(stats.ht_fog_g):.2f}</span></td></tr>")
            if (stats.nt_fog > 0):
                str_buffer.write(f"<tr><td>{Wave.to_str('normal', lang)}</td>")
                ev_pct = stats.nt_fog / stats.wavetotal
                if (ev_pct * 100) > (Wave.ms_nt_avg + Wave.night_wave_percent_max):
                    str_buffer.write(f"<td class='fogpct'><span class='statshigh' title='{Wave.fog_nt_avg/100:3.2%}'>{ev_pct:3.2%}</span></td>")
                elif (ev_pct * 100) < (Wave.ms_nt_avg - Wave.night_wave_percent_max):
                    str_buffer.write(f"<td class='fogpct'><span class='statslow' title='{Wave.fog_nt_avg/100:3.2%}'>{ev_pct:3.2%}</span></td>")
                else:
                    str_buffer.write(f"<td class='fogpct'><span class='statsnormal' title='{Wave.fog_nt_avg/100:3.2%}'>{ev_pct:3.2%}</span></td>")
                str_buffer.write(f"<td class='fogmax'><span title='min: {min(stats.nt_fog_g)}'>{max(stats.nt_fog_g)}</span></td>")
                str_buffer.write(f"<td class='fogavg'><span title='stddev: {pstdev(stats.nt_fog_g):.2f}'>{mean(stats.nt_fog_g):.2f}</span></td></tr>")
            if (stats.lt_fog > 0):
                str_buffer.write(f"<tr><td>{Wave.to_str('low', lang)}</td>")
                ev_pct = stats.lt_fog / stats.wavetotal
                if (ev_pct * 100) > (Wave.ms_lt_avg + Wave.night_wave_percent_max):
                    str_buffer.write(f"<td class='fogpct'><span class='statshigh' title='{Wave.fog_lt_avg/100:3.2%}'>{ev_pct:3.2%}</span></td>")
                elif (ev_pct * 100) < (Wave.ms_lt_avg - Wave.night_wave_percent_max):
                    str_buffer.write(f"<td class='fogpct'><span class='statslow' title='{Wave.fog_lt_avg/100:3.2%}'>{ev_pct:3.2%}</span></td>")
                else:
                    str_buffer.write(f"<td class='fogpct'><span class='statsnormal' title='{Wave.fog_lt_avg/100:3.2%}'>{ev_pct:3.2%}</span></td>")
                str_buffer.write(f"<td class='fogmax'><span title='min: {min(stats.lt_fog_g)}'>{max(stats.lt_fog_g)}</span></td>")
                str_buffer.write(f"<td class='fogavg'><span title='stddev: {pstdev(stats.lt_fog_g):.2f}'>{mean(stats.lt_fog_g):.2f}</span></td></tr>")
        # canons
        if (stats.ev_cohock > 0):
            str_buffer.write(f"<tr><th class='cohock'>{Wave.to_str('cohock-charge', lang)}</th>")
            str_buffer.write(f"<td>{Wave.to_str('low', lang)}</td>")
            ev_pct = stats.ev_cohock / stats.wavetotal
            if (ev_pct * 100) > (Wave.cohock_avg + Wave.night_wave_percent_max):
                str_buffer.write(f"<td class='cohockpct'><span class='statshigh' title='{Wave.cohock_avg/100:3.2%}'>{ev_pct:3.2%}</span></td>")
            elif (ev_pct * 100) < (Wave.cohock_avg - Wave.night_wave_percent_max):
                str_buffer.write(f"<td class='cohockpct'><span class='statslow' title='{Wave.cohock_avg/100:3.2%}'>{ev_pct:3.2%}</span></td>")
            else:
                str_buffer.write(f"<td class='cohockpct'><span class='statsnormal' title='{Wave.cohock_avg/100:3.2%}'>{ev_pct:3.2%}</span></td>")
            str_buffer.write(f"<td class='cohockmax'><span title='min: {min(grill_g)}'>{max(grill_g)}</span></td>")
            str_buffer.write(f"<td class='cohockavg'><span title='stddev: {pstdev(grill_g):.2f}'>{mean(grill_g):.2f}</span></td></tr>")
        
    str_buffer.write("\n</tbody></table>")
    return str_buffer.getvalue()    

def print_html_head(stats: GameSession, lang:str="en") -> str:
    str_buffer = StringIO()
    str_buffer.write("<!DOCTYPE html>\n")
    str_buffer.write(f"<html lang='{lang}'>\n<meta charset='utf-8'>\n")
    str_buffer.write("<base href='https://www.salmon-stats.ink/'>")
    str_buffer.write(f"<title>test</title>\n") # TODO localized title
    str_buffer.write("<link rel='stylesheet' href='style/sr.css'>\n")
    str_buffer.write("</head><body>\n")
    return str_buffer.getvalue()    
