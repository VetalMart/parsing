from concurrent.futures import ThreadPoolExecutor, Future
from timer import Timer
import csv
import urllib.request
from bs4 import BeautifulSoup
import sys
import eventlet
from task_queue import task_queue
#from eventlet.green import urllib

BASE_URL = 'http://ek.ua'
INPUT_FILE = sys.argv[1]

def get_url_from_file(f)->"gen":
    file_ = open(f, 'r').read().split()
    a = [i for i in file_]
    return a

def get_html(url)->'html':
    response = urllib.request.urlopen(url)
    return response.read()

def get_page_count(html)->list:
    try:
        soup = BeautifulSoup(html, 'lxml')
        paggination = soup.find('div', class_='ib page-num')
        list_href = []
        for i in  paggination.find_all('a', class_=['ib select', 'ib']):
            list_href.append(i.attrs['href'])
        #print(type(list_href), list_href)
        return list_href
    except AttributeError:
        return []

def parse(html)->list:
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

def save_whole_links_to_txt(l):
    f = open('save_full_list.txt', 'w')
    for i in l:
        f.write(BASE_URL+i+'\n')
    f.close()
def open_file(f)->list:
    list_with_fold_pages = []
    a = 1
    for i in get_url_from_file(f):
        list_with_fold_pages.extend(get_page_count(get_html(i)))
        print('Формирование ссылок {0}%'.format((a / len(get_url_from_file(f))) * 100))
        a += 1
    print(list_with_fold_pages)
    return list_with_fold_pages

def main():
    with Timer() as t:
        #list_with_fold_pages = open_file(INPUT_FILE)
        list_with_fold_pages = get_url_from_file(INPUT_FILE)
        #save_whole_links_to_txt(list_with_fold_pages)
    print('Блок формирования ссылок выполняется за {0} сек.'.format(t.secs))

    page_count = len(list_with_fold_pages)

    projects = []
    urls = []
    with Timer() as t:
        for page in range(0, page_count):
            urls.append('{0}{1}'.format(BASE_URL, list_with_fold_pages[page]))
        #"""
        a = 1
        with ThreadPoolExecutor(50) as executor:
            #for html in executor.map(get_html, urls): # for fold page
            for html in executor.map(get_html, list_with_fold_pages):
                print('Парсинг %d%%' % ((a / page_count) * 100))
                projects.extend(parse(html))
                a += 1
        """
        htmls = [get_html(i) for i in urls]
        print(len(htmls))
        projects.extend(task_queue(parse, htmls.iterator() , concurrency=10))
        """
    print('Блок парсинга выполняется за {0} сек.'.format(t.secs))

    with Timer() as t:
        save(projects, 'projects.csv')
    print('Сохранение выполняется за {0} сек.'.format(t.secs))

if __name__ == '__main__':
    with Timer() as t:
        main()
    print('Все выполняется за {0} сек.'.format(t.secs))

