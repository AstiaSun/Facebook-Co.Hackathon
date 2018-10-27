import math
from pathlib import Path
import pandas as pd
from bs4 import BeautifulSoup as bs, Tag
import re


class request():
    def __init__(self):
        self.name = ""
        self.ranking = 0
        self.surname = ""
        self.given_name = ""
        self.total_score = 0
        
        self.school_score = 0
        self.gov_exams = {}
        self.univ_exams = {}
        self.extra_points = {}
        
        self.is_out_of_competition = False
        #for comp. with 2014 data
        self.is_prioritized = False
        #for comp. with 2014 data
        self.is_directed = False
        
        self.is_original = False
        self.is_enrolled = False
        self.priority = 0
        self.status = ""


# predms_f = open('predms.txt', 'w', encoding='utf8')
# types_f = open('types.txt', 'w', encoding='utf8')

# college_predms = [
#     'Українська мова',
# ]
# univ_predms = [
#     'Творчий конкурс',
#     'Фахове випробування',
#     'Творче випробування з фаху',
#     'Творчий залік',
#     'Академічний живопис; Композиція; Малюнок',
#     'Загальна фізична підготовка; Підготовленість з обраного виду спорту',
#     'Співбесіда',
#     'Інші показники конкурсного відбору',
#     'Фаховий іспит',
#     'Фахове випрбування',
#     'ЄФВВ із загальних навчальних правничих компетентностей',
#     'ЄФВВ з права',
#     'ТіМ ФКіС',
#     'Харчові технології',
#     'Додаткове вступне випробування',
# ]
#
# gov_types = [
#     'ЗНО',
# ]
# univ_types = [
#     'практичне та теоретичне',
#     'вступний іспит',
#     'англійська, німецька, французька або іспанська',
#     '(Усно)',
# ]


def parse_details(src: str):
    """
    :param src: "Українська мова та література (ЗНО): 179 Творче випробування з фаху (практичне та теоретичне): 180 Історія України (ЗНО): 169 Середній бал документа про освіту: 10.5"
    """
    gov_predms = [
        'Математика',
        'Українська мова та література',
        'Іноземна мова',
        'Фізика',
        'Хімія',
        'Біологія',
        'Географія',
        'Англійська мова',
        'Історія України',
        'Російська мова',
    ]

    extra_predms = {
        'Бал за підготовчі курси' : 'prep',
        'Бал призерам ІІІ етапу Всеукраїнських конкурсів фахової майстерності' : 'olymp',
        'Бал за особливі успіхи' : 'olymp',
        'Бал за особливі успіхи' : 'olymp',
        'Бал учасника олімпіад' : 'olymp',
    }

    rows = []
    src = src.strip()
    while src:
        if all(part.isalpha() for part in src.split()): break
        end_index = re.search(r'\d+(\.\d+)?', src).end()
        current, src = src[:end_index], src[end_index:].strip()
        rows.append(current)

    school_score, gov_exams, univ_exams, extra_points = 0, {}, {}, {}


    for row in rows:
        m = re.match(r'(.+?)(?:\((.*)\)\s*(.*?)?)?\s*:\s+(\d+(?:\.\d+)?)', row)
        predm, typ, am = m.group(1).strip() + ' ' + m.group(3).strip() if m.group(3) else m.group(1).strip(), m.group(2), float(m.group(4))
        if predm == 'Середній бал документа про освіту':
            school_score = am
        elif predm in gov_predms:
            gov_exams[predm] = am
        elif predm in extra_predms:
            extra_points[extra_predms[predm]] = am
        else:
            # if predm in univ_exams: raise ValueError
            univ_exams[predm] = am

    # if typ not in gov_types + univ_types + [None]: types_f.write(f'{typ}\n')

    return school_score, gov_exams, univ_exams, extra_points


def html_2018_to_list_dicts(src):
    soup = bs(src,'html.parser')

    tlower = soup.find('div', {'id': 'list'}).div.div.div.div.h3.string.lower()
    if 'коледж' in tlower or 'технікум' in tlower or 'училищ' in tlower:
        return {}, []

    tab=soup.find("table", {"class":"tablesaw tablesaw-stack tablesaw-sortable"})
    df = pd.read_html(str(tab), skiprows=0)[0][:-1]
    res_list_of_dicts = []
    for index, row in df.iterrows():
        r = request()
        if isinstance(row['ПІБ'], float) and math.isnan(row['ПІБ']): continue
        r.name, r.surname, r.given_name = (row['ПІБ'] + ' - - ').split(' ')[:3]
        r.total_score = row['Σ']
        r.priority = row['П']
        r.status = str(row['С'])
        r.ranking = row['#']
        r.is_enrolled = (str(row["С"])[:9] == "До наказу")
        r.is_out_of_competition = (str(row['К']) != "—")
        r.is_original = (str(row['Д']) == "+")
        try:
            r.school_score, r.gov_exams, r.univ_exams, r.extra_points = parse_details(row['Деталізація'])
        except AttributeError:
            continue
        res_list_of_dicts.append(r.__dict__)

    header: Tag = soup.find('div', {'id': 'list'}).div.div.div.div
    header_p: Tag = header.h3.find_next_sibling('p')

    # print(header)

    header_d = {
        'univ_title': header.h3.string,
        'type': 'bachelor' if header_p.b.string == 'Бакалавр' else 'j_spec' if header_p.b.string == 'Молодший спеціаліст' else 'master' if header_p.b.string == 'Магістр' else None,
        'area_title': header_p.span.find_all('b')[0].next_sibling.strip(),
        'course_title': header_p.span.find_all('b')[1].next_sibling.strip().split(None, 1)[1],
        'is_fulltime' : 'денна форма навчання' in str(header_p.span),
        'licenced' : int(re.search(r'Ліцензійний обсяг:</b>\s*(\d+)', str(header_p)).group(1)),
        'budget' : int(re.search(r'Обсяг держ замовлення:</b>\s*(\d+)', str(header_p)).group(1)) if ('Обсяг держ замовлення' in str(header_p)) else 0,
    }

    return header_d, res_list_of_dicts


if __name__ == '__main__':
    for p in Path('data_2018').glob('vstup.info/2018/*/*.html'):
        print(p)
        try:
            print(html_2018_to_list_dicts(p.open(encoding='utf8').read()))
        except AttributeError:
            pass