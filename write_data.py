import argparse
from functools import partial

import pymongo
import os
import pandas as pd
import re
import base64
from bs4 import BeautifulSoup
from multiprocessing import Pool
from threading import Thread
from queue import Queue

from html_2018_parsing import html_2018_to_list_dicts

parser = argparse.ArgumentParser()
parser.add_argument('--db', dest='db', type=str, help='database name')
parser.add_argument('--erase', dest='erase', action='store_true', help='erase db')
parser.set_defaults(erase=False)

args = parser.parse_args()
db = pymongo.MongoClient(host="192.168.163.132").get_database(args.db)


failed_name = 0


def parse_table_2014(html_text):
    global failed_name
    soup = BeautifulSoup(html_text, 'html5lib')
    # with open('html/out.html', 'w', encoding='utf8') as out: out.write(soup.prettify())
    people_list = []

    univ_title = str(soup.find('div', {'id': 'title'}).find_all('a')[1].string)
    tlower = univ_title.lower()
    if 'коледж' in tlower or 'технікум' in tlower or 'училищ' in tlower:
        return []

    for tr in soup.table.tbody.find_all('tr'):
        id_, pib, summ, av_dipl, zno, univ_exams, addit_balls, pozakonkursnyi, pershochergovyi, cilyove, originals, podano_rekomendovano = tr.find_all(
            'td')

        temp = pib.string.split()[:3]
        if len(temp) < 2:
            failed_name += 1
            continue

        surname, name = temp[:2]
        given_name = ''

        if len(temp) == 3:
            given_name = temp[2]

        split_originals = originals.string.strip().split('/')

        olymp, prep = map(lambda x: float(x) if x != '—' else 0, addit_balls.string.split('/'))
        d = {
            'rank': int(id_.string),
            'surname': surname,
            'name': name,
            'given_name': given_name,
            'total_score': float(summ.string),
            'school_score': float(av_dipl.string),
            'gov_exams': {nobr['title']: float(re.search(r'\d+(\.\d+)?', nobr.string).group(0)) for nobr in
                          zno.find_all('nobr')},
            'univ_exams': sum(
                float(re.search(r'\d+(\.\d+)?', nobr.string).group(0)) for nobr in univ_exams.find_all('nobr')),
            'extra_points': {'olymp': olymp,
                             'prep': prep},
            'is_out_of_competition': True if pozakonkursnyi.string == '+' else False,
            'is_prioritized': True if pershochergovyi.string == '+' else False,
            'is_directed': True if cilyove.string == '+' else False,
            'is_original': True if (len(split_originals) and split_originals[0].strip() == '+') or originals.string.strip() == '+' else False,
            'is_enrolled': True if 'style' in id_.attrs else False,
            'num_applications': int(podano_rekomendovano.string.split('/')[0]) if podano_rekomendovano.string else None,
            'num_recommendations': int(
                podano_rekomendovano.string.split('/')[1]) if podano_rekomendovano.string else None
        }

        people_list.append(d)

    contents_h = soup.find('div', {'id': 'title'}).h2.contents
    if contents_h[0].name != 'a' or contents_h[2].name != 'br' or contents_h[3].name != 'a' or contents_h[
        5].name != 'br' or contents_h[7].name != 'br' or contents_h[9].name != 'br':
        raise ValueError
    if 'денна форма навчання' not in contents_h[-1].lower() and 'заочна форма навчання' not in contents_h[-1].lower():
        raise ValueError

    contents_licenced = soup.find('div', {'id': 'title'}).parent.find_all('div')[1].div.contents

    course = re.match(r'Спеціальність: (.*)', contents_h[-3]) \
             or re.match(r'Напрям: (.*)', contents_h[-3]) \
             or re.match(r'Спеціалізація: (.*)', contents_h[-3])

    licensed = re.match(r'Ліцензований обсяг прийому: (\d+)', contents_licenced[1])
    budget = re.match(r'Обсяг державного замовлення: (\d+)', contents_licenced[3])

    if not licensed or not budget:
        print(licensed, budget, contents_h, contents_licenced)

    head_d = {
        'univ_title': univ_title,
        'area_title': re.match(r'Галузь: (.*)', contents_h[6]).group(1),
        'course_title': course.group(1),
        'is_fulltime': ('денна форма навчання' in contents_h[-1].lower()),
        'licenced': int(licensed.group(1)) if licensed else 0,
        'budget': int(budget.group(1)) if budget else 0,
        'type': 'bachelor' if people_list[0]['gov_exams'] else 'master',
    }

    del soup

    return head_d, people_list


def get_some_id(univ_title):
    return base64.b64encode(univ_title.encode('utf-8')).decode('ascii')


def parse_needed_year(prefix, filename, data, areas, courses, parse_exact_year_f, year_num):
    filename = filename.strip()

    head, course_id = filename.split('p')
    course_id = int(course_id[:-5])

    _, year, univ_id = head.split('i')
    univ_id = int(univ_id)

    # with open(os.path.join(prefix, filename), 'rb') as f:
    #    result = parse_table_2014(f.read())
    try:
        head, result = parse_exact_year_f(data)
    except AttributeError:
        return []

    if not result:
        return []

    univ_title = head['univ_title']
    univ_title = re.sub(r'\([^)]*\)', '', univ_title.strip())
    while '  ' in univ_title:
        univ_title = univ_title.replace('  ', ' ')

    course_id = get_some_id(head['course_title'].strip())
    area_id_old = get_some_id(head['area_title'].strip())

    if area_id_old not in areas:
        areas[area_id_old] = {
            'area_id_old': area_id_old,
            'area_title': head['area_title'].strip()
        }
    if course_id not in courses:
        courses[(area_id_old, course_id)] = {
            'area_id_old': area_id_old,
            'area_title': head['area_title'].strip(),
            'course_id': course_id,
            'course_title': head['course_title'].strip()
        }

    for x in result:
        x["univ_id"] = get_some_id(univ_title)
        x["course_id"] = course_id
        x["area_id_old"] = area_id_old
        x["year"] = year_num

    return result


def read_files(q, mp_args):
    for prefix, filename in mp_args:
        with open(os.path.join(prefix, filename), 'rb') as f:
            q.put((prefix, filename, f.read()))


def parallel_needed_year(mp_args, parse_exact_year_f, year_num):
    db = pymongo.MongoClient(host="192.168.163.132").get_database(args.db)

    data = []

    q = Queue()

    t = Thread(target=read_files, args=(q, mp_args))
    t.start()

    areas = dict()
    courses = dict()

    for x in range(len(mp_args)):
        prefix, argument, file_data = q.get()
        z = len(data)
        data.extend(parse_needed_year(prefix, argument, file_data, areas, courses, parse_exact_year_f, year_num))
        # print(prefix, argument, len(data)-z)

    if data:
        print('Inserting ', len(data))
        db.requests.insert_many(data)
        del data

    if areas:
        print('Inserting areas ', len(areas))
        for area in areas.values():
            db.areas.find_and_modify(
                query={
                    'area_id_old': area['area_id_old']
                },
                update={
                    '$setOnInsert': area
                },
                upsert=True,
            )

    if courses:
        print('Inserting courses ', len(courses))
        for course in courses.values():
            db.courses.find_and_modify(
                query={
                    'area_id_old': course['area_id_old'],
                    'course_id': course['course_id']
                },
                update={
                    '$setOnInsert': course
                },
                upsert=True,
            )

    if failed_name:
        print(failed_name)


def main():
    global db
    if args.erase:
        db.requests.drop()

    prefix_2018 = r'C:\Users\Name\PycharmProjects\Facebook-Co.Hackathon\data_2018\vstup.info\2018\\'

    prefix_2014 = '/home/oleg/hafb/data_2014/vstup.info/2014/'

    def inputs_needed(prefix):
        result = []
        inputs = []
        total = 0

        for subdir in os.walk(prefix):
            files = subdir[-1]

            for x in files:

                if 'p' in x:
                    total += 1
                    inputs.append([subdir[0], x])

                    if len(inputs) == 200:
                        result.append(inputs)
                        inputs = []

        if inputs:
            result.append(inputs)
        print(total)

        return result

    pool = Pool(4)
    db = pymongo.MongoClient(host='192.168.163.132').get_database(args.db)
    # ar_2014 = inputs_needed(prefix_2014)
    # parallel_2014 = partial(parallel_needed_year, parse_exact_year_f=parse_table_2014, year_num=2014)
    # pool.map(parallel_2014, ar_2014)
    ar_2018 = inputs_needed(prefix_2018)
    parallel_2018 = partial(parallel_needed_year, parse_exact_year_f=html_2018_to_list_dicts, year_num=2018)
    pool.map(parallel_2018, ar_2018)
    print(db.requests.count())


if __name__ == '__main__':
    main()
