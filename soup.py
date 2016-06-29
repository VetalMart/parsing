import csv
import urllib.request
from bs4 import BeautifulSoup
import sys

BASE_URL = 'http://ek.ua'
INPUT_URL = sys.argv[1]

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
        writer.writerow(('Модель', 'Цена', 'Магазин'))

        for project in projects:
            writer.writerow((project['title'], project['market'],
                             project['price']))

def main():
    url_pages = get_page_count(get_html(INPUT_URL))
    page_count = len(url_pages)
    print(url_pages, page_count)

    projects = []

    for page in range(0, page_count):
        print('Парсинг %d%%' % ((page / page_count) * 100))
        url = '{0}{1}'.format(BASE_URL, url_pages[page])
        projects.extend(parse(get_html(url)))

    for project in projects:
        print(project)

    save(projects, 'projects.csv')

if __name__ == '__main__':
    main()
