import re
from pprint import pprint
from typing import List, Dict, Any

from bs4 import BeautifulSoup, Tag

def parse_table_2014(html_text: str) -> List[Dict[str, Any]]:
    soup = BeautifulSoup(html_text, 'html5lib')
    # with open('html/out.html', 'w', encoding='utf8') as out: out.write(soup.prettify())
    for tr in soup.table.tbody.find_all('tr'):
        id_, pib, summ, av_dipl, zno, blank, addit_balls, pozakonkursnyi, pershochergovyi, cilyove, originals, podano_rekomendovano = tr.find_all('td')
        surname, name, given_name = pib.string.split()
        olymp, prep = map(lambda x: float(x) if x != '—' else 0, addit_balls.string.split('/'))
        d = {
            'surname': surname,
            'name': name,
            'given_name': given_name,
            'total_score': float(summ.string),
            'school_score': float(av_dipl.string),
            'gov_exams': {nobr['title']: float(re.search(r'\d+(\.\d+)?', nobr.string).group(0)) for nobr in zno.find_all('nobr')},
            'extra_points': {'olymp': olymp,
                             'prep': prep},
            'is_out_of_competition': True if pozakonkursnyi.string == '+' else False,
            'is_prioritized': True if pershochergovyi.string == '+' else False,
            'is_directed': True if cilyove.string == '+' else False,
            'is_original': True if originals.string.split('/')[0] == '+' else False,
            'is_enrolled': True if 'style' in id_.attrs else False,
            'num_applications': int(podano_rekomendovano.string.split('/')[0]),
            'num_recommendations': int(podano_rekomendovano.string.split('/')[1])
        }

        if blank.string != '—': raise ValueError
        # pprint(d)
        return d




















