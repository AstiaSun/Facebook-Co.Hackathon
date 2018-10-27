import argparse
import pymongo
import os
import requests
import re
import base64
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser()
parser.add_argument('--db', dest='db', type=str, help='database name')
parser.add_argument('--erase', dest='erase', action='store_true', help='erase db')
parser.set_defaults(erase=False)

args = parser.parse_args()
db = pymongo.MongoClient().get_database(args.db)

prefix = '/home/oleg/hafb/data_2014/vstup.info/2014/'
html_files_2014 = [os.path.join(prefix, x) for x in os.listdir(prefix) if os.path.isfile(os.path.join(prefix, x))
              and 'b.html' not in x
              and 'bz.html' not in x
              and 'stat.html' not in x
              and 'index' not in x
              and 'o' not in x]

prefix = '/home/oleg/hafb/data_test/vstup.info/2018/'
html_files_2018 = [os.path.join(prefix, x) for x in os.listdir(prefix) if os.path.isfile(os.path.join(prefix, x))
                   and 'index' not in x
                   and 'o' not in x]

def get_data_from_page_2014(html_page):
    soup = BeautifulSoup(html_page, 'html.parser')
    candidates = [candidate.string for candidate in soup.body.find_all("td")]
    while '\xa0' in candidates:
        candidates.remove('\xa0')
    univ_title = candidates[candidates.index("Назва ВНЗ:") + 1]
    is_state_owned = 'національний' in univ_title.lower() or 'національна' in univ_title.lower()

    res_dict = {
        'univ_title': univ_title,
        'univ_type': candidates[candidates.index('Тип ВНЗ:') + 1],
        'univ_address': candidates[candidates.index("Адреса:") + 1],
        'is_state_owned': is_state_owned
    }
    return res_dict

def get_data_from_page_2018(html_page):
    soup = BeautifulSoup(html_page, 'lxml')
    candidates = [candidate.string for candidate in soup.find('table', id='about').find_all("td")]
    address = candidates[candidates.index("Область, населений пункт:") + 1]
    is_state_owned = True
    if candidates[candidates.index("Форма власності:") + 1] == "Державна":
        is_state_owned = True
    else:  # elif candidates[candidates.index("Форма власності:") + 1] == "Приватна":
        is_state_owned = False
    res_dict = {
        'univ_title': str(candidates[candidates.index("Назва ВНЗ:") + 1]),
        'univ_type': str(candidates[candidates.index('Тип ВНЗ:') + 1]),
        'univ_address': str(address),
        'is_state_owned': is_state_owned
    }
    del soup
    return res_dict

def get_city_name_from_address(address):
    KEY="AIzaSyB5U-lB6B3ChRUsT4M10FuYoPHsZbLZ2Bs"
    GOOGLE_MAPS_API_URL = "https://maps.googleapis.com/maps/api/geocode/json?address=" + address.replace(' ', "+") + \
                          "&language=uk&sensor=false&region=uk&key=" + KEY
    req = requests.get(GOOGLE_MAPS_API_URL)
    res = req.json()
    try:
        result = res['results'][0]
        for address_component in result["address_components"]:
            if ('administrative_area_level_1' in address_component["types"]) \
                    and ('political' in address_component["types"]):
                # here our city name - however we need to tes
                return address_component['long_name']

        for address_component in result["address_components"]:
            if ('administrative_area_level_2' in address_component["types"]) \
                    and ('political' in address_component["types"]):
                # here our city name - however we need to tes
                return address_component['long_name']
    except:
        print(address)
        return ''

def get_univ_id(univ):
    return base64.b64encode(univ['univ_title'].encode('utf-8')).decode('ascii')

univs_to_insert = dict()

for univ_file in html_files_2014:
    with open(univ_file, 'rb') as f:
        q = f.read()
    univ = get_data_from_page_2014(q)

    tlower = univ['univ_title'].lower()
    if 'коледж' in tlower or 'технікум' in tlower or 'училищ' in tlower:
        continue

    univ['univ_title'] = re.sub(r'\([^)]*\)', '', univ['univ_title'].strip())
    while '  ' in univ['univ_title']:
        univ['univ_title'] = univ['univ_title'].replace('  ', ' ')

    univ['univ_location'] = get_city_name_from_address(univ['univ_address'])
    univ['univ_id'] = get_univ_id(univ)

    univs_to_insert[univ['univ_id']] = univ
    if len(univs_to_insert) % 10 == 0:
        print(len(univs_to_insert))

print('After 2014:', len(univs_to_insert))
for univ_file in html_files_2018:
    with open(univ_file, 'rb') as f:
        q = f.read()

    univ = get_data_from_page_2018(q)

    tlower = univ['univ_title'].lower()
    if 'коледж' in tlower or 'технікум' in tlower or 'училищ' in tlower:
        continue

    univ['univ_title'] = re.sub(r'\([^)]*\)', '', univ['univ_title'].strip())
    while '  ' in univ['univ_title']:
        univ['univ_title'] = univ['univ_title'].replace('  ', ' ')

    univ['univ_location'] = get_city_name_from_address(univ['univ_address'])
    univ['univ_id'] = get_univ_id(univ)

    univs_to_insert[univ['univ_id']] = univ
    if len(univs_to_insert) % 10 == 0:
        print(len(univs_to_insert))

if args.erase:
    db.univs.drop()

db.univs.insert_many(univs_to_insert.values())

print(db.univs.count())