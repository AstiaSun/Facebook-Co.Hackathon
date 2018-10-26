import re
from pprint import pprint
from typing import List, Dict, Any

from bs4 import BeautifulSoup, Tag


def parse_table_2014(html_text):
    soup = BeautifulSoup(html_text, 'html5lib')
    # with open('html/out.html', 'w', encoding='utf8') as out: out.write(soup.prettify())

    people_list = []
    for tr in soup.table.tbody.find_all('tr'):
        id_, pib, summ, av_dipl, zno, univ_exams, addit_balls, pozakonkursnyi, pershochergovyi, cilyove, originals, podano_rekomendovano = tr.find_all('td')

        if len(pib.string.split()) != 3:
            continue

        surname, name, given_name = pib.string.split()
        olymp, prep = map(lambda x: float(x) if x != '—' else 0, addit_balls.string.split('/'))
        d = {
            'surname': surname,
            'name': name,
            'given_name': given_name,
            'total_score': float(summ.string),
            'school_score': float(av_dipl.string),
            'gov_exams': {nobr['title']: float(re.search(r'\d+(\.\d+)?', nobr.string).group(0)) for nobr in zno.find_all('nobr')},
            'univ_exams': sum(float(re.search(r'\d+(\.\d+)?', nobr.string).group(0)) for nobr in univ_exams.find_all('nobr')),
            'extra_points': {'olymp': olymp,
                             'prep': prep},
            'is_out_of_competition': True if pozakonkursnyi.string == '+' else False,
            'is_prioritized': True if pershochergovyi.string == '+' else False,
            'is_directed': True if cilyove.string == '+' else False,
            'is_original': True if originals.string.split('/')[0] == '+' else False,
            'is_enrolled': True if 'style' in id_.attrs else False,
            'num_applications': int(podano_rekomendovano.string.split('/')[0]) if podano_rekomendovano.string else None,
            'num_recommendations': int(podano_rekomendovano.string.split('/')[1]) if podano_rekomendovano.string else None
        }

        # pprint(d)
        people_list.append(d)

    contents_h = soup.find('div', {'id':'title'}).h2.contents
    if contents_h[0].name != 'a' or contents_h[2].name != 'br' or contents_h[3].name != 'a' or contents_h[5].name != 'br' or contents_h[7].name != 'br' or contents_h[9].name != 'br': raise ValueError
    if 'денна форма навчання' not in contents_h[10].lower() or 'заочна форма навчання' not in contents_h[10].lower(): raise ValueError

    contents_licenced = soup.find('div', {'id': 'title'}).parent.find_all('div')[1].div.contents

    head_d = {
        'area_title' : re.match(r'Галузь: (.*)', contents_h[6]).group(1),
        'course_title' : re.match(r'Напрям: (.*)', contents_h[6]).group(1),
        'is_fulltime' : ('денна форма навчання' in contents_h[10].lower()),
        'licenced' : int(re.match(r'Ліцензований обсяг прийому: (\d+)', contents_licenced[1]).group(1)),
        'budget' : int(re.match(r'Обсяг державного замовлення: (\d+)', contents_licenced[3]).group(1)),
        'type' : 'bachelor' if people_list[0]['gov_exams'] else 'master',
    }

    return people_list, head_d


if __name__ == '__main__':
    parse_table_2014(open(r'html/i2014i30p148218.html').read())