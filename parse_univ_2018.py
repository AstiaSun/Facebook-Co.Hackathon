from bs4 import BeautifulSoup

# http://vstup.info/2018/i2018i41.html

with open('/home/oleg/hafb/data_test/vstup.info/2018/i2018i41.html', 'rb') as f:
    q = f.read()

def parse_univ2018(html_string):
    soup = BeautifulSoup(html_string, 'html.parser')

    table = soup.find('table', id='about')

    rows = table.findAll('tr')
    print(rows)

parse_univ2018(q)