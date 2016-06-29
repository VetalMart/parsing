import csv
import urllib.request
from bs4 import BeautifulSoup
import sys

BASE_URL = 'http://ek.ua'
INPUT_FILE = sys.argv[1]

def get_url_from_file(f):
    file_ = open(f, 'r').read().split()
    a = [i for i in file_]
    return a

def get_html(url):
    response = urllib.request.urlopen(url)
    return response.read()

def get_page_count(html):
    soup = BeautifulSoup(html, 'lxml')
    paggination = soup.find('div', class_='ib page-num')
    list_href = []
    for i in  paggination.find_all('a', class_=['ib select', 'ib']):
        list_href.append(i.attrs['href'])
    #print(type(list_href), list_href)
    return list_href

def parse(html):
    soup = BeautifulSoup(html, 'lxml')
    table = soup.find('table', class_="where-buy-table")

    wares = []

    for raws in table.find_all('tr', class_= ['', ' tr-odd']):
        col = raws.find_all('td', class_=['where-buy-description',
                                          'where-buy-price'])
        wares.append({
            'title': col[0].h3.text.strip(),
            'market': col[0].a.text,
            'price': col[1].a.text.replace('\xa0', ' ')
        })

    return wares

def save(projects, path):
    with open(path, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(('Модель', 'Магазин', 'Цена'))

        for project in projects:
            writer.writerow((project['title'], project['market'],
                             project['price']))

def main():
    list_input_url =[i for i in get_url_from_file(INPUT_FILE)]
    #print(list_input_url)
    list_with_fold_pages = []
    for i in list_input_url:
        list_with_fold_pages.extend(get_page_count(get_html(i)))

    for i in list_with_fold_pages:
        print(i)

    page_count = len(list_with_fold_pages)

    projects = []

    for page in range(0, page_count):
        print('Парсинг %d%%' % ((page / page_count) * 100))
        url = '{0}{1}'.format(BASE_URL, list_with_fold_pages[page])
        projects.extend(parse(get_html(url)))

    save(projects, 'projects.csv')

if __name__ == '__main__':
    main()

