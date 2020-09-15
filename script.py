import requests
import datetime
import pandas as pd
import pretty_html_table
import pytz
import timezonefinder
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse


def build_html_for_answer(title, *content):
    s = ['<HTML>', '<HEAD><TITLE>', title, '</TITLE></HEAD>', '<BODY>', '<br>'.join(list(content)), '</BODY></HTML>']
    html = ''.join(s)
    return html


def transliteration(text):
    cyrillic = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    latin = "a|b|v|g|d|e|e|zh|z|i|y|k|l|m|n|o|p|r|s|t|u|f|kh|tc|ch|sh|shch||y|’|e|ju|" \
            "ja|A|B|V|G|D|E|E|Zh|Z|I|Y|K|L|M|N|O|P|R|S|T|U|F|Kh|Tc|Ch|Sh|Shch||Y||E|Ju|Ja".split('|')
    return text.translate({ord(k): v for k, v in zip(cyrillic, latin)})


app = FastAPI()
data = pd.read_csv('RU.txt', sep="\t", header=None, low_memory=False)
data.columns = ['geoname_id', 'name', 'ascii_name', 'alternate_names', 'latitude', 'longitude', 'feature_class',
                'feature_code', 'country_code', 'cc2', 'admin1_code', 'admin2_code', 'admin3_code', 'admin4_code',
                'population', 'elevation', 'dem', 'timezone', 'modification_date']
data['Russian_names'] = pd.Series(x.split(sep=',')[-1] if type(x) == str else 'nan' for x in data['alternate_names'])


@app.get("/get_geoname", response_class=HTMLResponse)
async def get_geoname(geonameid):
    return build_html_for_answer('First Method',
                                 pretty_html_table.build_table(data.query('geoname_id == @geonameid'), 'blue_light'))


@app.get("/get_html", response_class=HTMLResponse)
async def get_html(count: int, page):
    page = requests.get(page)
    html = page.content.decode("utf-8")
    selection = {}
    for geoname, population, ident in zip(data['Russian_names'], data['population'], data.index):
        if geoname in html and geoname != 'nan':
            if geoname not in selection.keys():
                selection[geoname] = [population, ident]
            elif selection[geoname][0] < population:
                selection[geoname] = [population, ident]
    df = pd.DataFrame.from_dict(selection, orient='index', columns=['population', 'geoname_id']).sort_values(
        'population')[::-1]
    id_list = df.iloc[:count].geoname_id.to_list()
    x = []
    for ident in id_list:
        x.append(data.iloc[ident].to_list())
    answer = pd.DataFrame(x, columns=data.columns)
    return build_html_for_answer('Second Method',
                                 pretty_html_table.build_table(answer, 'blue_light'))


@app.get("/compare_two_geonames", response_class=HTMLResponse)
async def compare_two_geonames(first_geoname, second_geoname):
    first = transliteration(first_geoname)
    second = transliteration(second_geoname)
    f = data.query("ascii_name == @first").sort_values('population')
    if f.shape[0] > 0:
        f = f.iloc[-1]
    else:
        return "first geoname error"
    s = data.query("ascii_name == @second").sort_values('population')
    if s.shape[0] > 0:
        s = s.iloc[-1]
    else:
        return "second geoname error"
    answer = pd.DataFrame([f.to_list(), s.to_list()], columns=data.columns).rename(index={0: 'Первый', 1: 'Второй'})
    timezone = 'Same timezone'
    if f.timezone != s.timezone:
        tf = timezonefinder.TimezoneFinder()
        first_timezone = pytz.timezone(tf.certain_timezone_at(lat=f.latitude, lng=f.longitude))
        second_timezone = pytz.timezone(tf.certain_timezone_at(lat=s.latitude, lng=s.longitude))
        dt = datetime.datetime.utcnow()
        dif = int(abs((first_timezone.utcoffset(dt) - second_timezone.utcoffset(dt)).total_seconds() // 3600))
        timezone = ' '.join(['Timezone difference on ', str(dif), 'hours' if dif > 1 else 'hour'])
    return build_html_for_answer('Third Method',
                                 pretty_html_table.build_table(answer, 'blue_light'),
                                 str(first_geoname if f.latitude < s.latitude else second_geoname),
                                 str(timezone))


uvicorn.run(app, host="127.0.0.1", port=8000)
