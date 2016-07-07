from concurrent.futures import Future, ProcessPoolExecutor
from timer import Timer
import csv
import urllib.request
from bs4 import BeautifulSoup
import sys
import random

BASE_URL = 'http://ek.ua'
INPUT_FILE = sys.argv[1]
LIST_PROXY = [['5.34.183.29', '8080', 'budim_oleg:fesupaly'], ['5.34.183.151', '8080', 'budim_oleg:fesupaly'], ['5.34.183.179', '8080', 'budim_oleg:fesupaly'], ['5.34.183.193', '8080', 'budim_oleg:fesupaly'], ['91.207.60.51', '8080', 'budim_oleg:fesupaly'], ['91.207.60.87', '8080', 'budim_oleg:fesupaly'], ['91.207.60.166', '8080', 'budim_oleg:fesupaly'], ['91.207.60.220', '8080', 'budim_oleg:fesupaly'], ['91.207.60.231', '8080', 'budim_oleg:fesupaly'], ['91.207.61.51', '8080', 'budim_oleg:fesupaly'], ['91.207.61.87', '8080', 'budim_oleg:fesupaly'], ['91.207.61.166', '8080', 'budim_oleg:fesupaly'], ['91.207.61.220', '8080', 'budim_oleg:fesupaly'], ['91.207.61.231', '8080', 'budim_oleg:fesupaly'], ['91.217.90.19', '8080', 'budim_oleg:fesupaly'], ['91.217.90.78', '8080', 'budim_oleg:fesupaly'], ['91.217.91.19', '8080', 'budim_oleg:fesupaly'], ['91.217.91.78', '8080', 'budim_oleg:fesupaly'], ['91.226.212.24', '8080', 'budim_oleg:fesupaly'], ['91.226.212.114', '8080', 'budim_oleg:fesupaly'], ['91.226.212.249', '8080', 'budim_oleg:fesupaly'], ['91.226.213.24', '8080', 'budim_oleg:fesupaly'], ['91.226.213.114', '8080', 'budim_oleg:fesupaly'], ['91.226.213.249', '8080', 'budim_oleg:fesupaly'], ['176.103.48.14', '8080', 'budim_oleg:fesupaly'], ['176.103.48.71', '8080', 'budim_oleg:fesupaly'], ['176.103.48.249', '8080', 'budim_oleg:fesupaly'], ['176.103.49.14', '8080', 'budim_oleg:fesupaly'], ['176.103.49.71', '8080', 'budim_oleg:fesupaly'], ['176.103.49.249', '8080', 'budim_oleg:fesupaly'], ['176.103.50.232', '8080', 'budim_oleg:fesupaly'], ['176.103.50.235', '8080', 'budim_oleg:fesupaly'], ['176.103.51.232', '8080', 'budim_oleg:fesupaly'], ['176.103.51.235', '8080', 'budim_oleg:fesupaly'], ['176.103.52.90', '8080', 'budim_oleg:fesupaly'], ['176.103.52.135', '8080', 'budim_oleg:fesupaly'], ['176.103.52.222', '8080', 'budim_oleg:fesupaly'], ['176.103.53.90', '8080', 'budim_oleg:fesupaly'], ['176.103.53.135', '8080', 'budim_oleg:fesupaly'], ['176.103.53.222', '8080', 'budim_oleg:fesupaly'], ['176.103.54.42', '8080', 'budim_oleg:fesupaly'], ['176.103.54.75', '8080', 'budim_oleg:fesupaly'], ['176.103.54.80', '8080', 'budim_oleg:fesupaly'], ['176.103.54.187', '8080', 'budim_oleg:fesupaly'], ['176.103.55.42', '8080', 'budim_oleg:fesupaly'], ['176.103.55.75', '8080', 'budim_oleg:fesupaly'], ['176.103.55.80', '8080', 'budim_oleg:fesupaly'], ['176.103.55.187', '8080', 'budim_oleg:fesupaly'], ['193.169.86.38', '8080', 'budim_oleg:fesupaly'], ['193.169.86.120', '8080', 'budim_oleg:fesupaly'], ['193.169.86.133', '8080', 'budim_oleg:fesupaly'], ['193.169.86.148', '8080', 'budim_oleg:fesupaly'], ['193.169.86.154', '8080', 'budim_oleg:fesupaly'], ['193.169.86.161', '8080', 'budim_oleg:fesupaly'], ['193.169.86.215', '8080', 'budim_oleg:fesupaly'], ['193.169.86.250', '8080', 'budim_oleg:fesupaly'], ['193.169.87.38', '8080', 'budim_oleg:fesupaly'], ['193.169.87.120', '8080', 'budim_oleg:fesupaly'], ['193.169.87.133', '8080', 'budim_oleg:fesupaly'], ['193.169.87.148', '8080', 'budim_oleg:fesupaly'], ['193.169.87.154', '8080', 'budim_oleg:fesupaly'], ['193.169.87.161', '8080', 'budim_oleg:fesupaly'], ['193.169.87.215', '8080', 'budim_oleg:fesupaly'], ['193.169.87.250', '8080', 'budim_oleg:fesupaly'], ['193.203.48.21', '8080', 'budim_oleg:fesupaly'], ['193.203.49.21', '8080', 'budim_oleg:fesupaly'], ['193.203.50.43', '8080', 'budim_oleg:fesupaly'], ['193.203.51.43', '8080', 'budim_oleg:fesupaly'], ['217.12.199.179', '8080', 'budim_oleg:fesupaly'], ['217.12.199.192', '8080', 'budim_oleg:fesupaly'], ['217.12.210.50', '8080', 'budim_oleg:fesupaly'], ['217.12.210.209', '8080', 'budim_oleg:fesupaly'], ['217.12.223.4', '8080', 'budim_oleg:fesupaly'], ['217.12.223.11', '8080', 'budim_oleg:fesupaly'], ['217.12.210.141', '8080', '8ax7EnCnX:Pwpl9bCJU'], ['217.12.210.142', '8080', '8ax7EnCnX:Pwpl9bCJU'], ['217.12.210.143', '8080', '8ax7EnCnX:Pwpl9bCJU'], ['5.34.183.224', '8080', '8ax7EnCnX:Pwpl9bCJU'], ['5.34.183.68', '8080', '8ax7EnCnX:Pwpl9bCJU'], ['176.103.48.231', '8080', '8ax7EnCnX:Pwpl9bCJU'], ['176.103.48.232', '8080', '8ax7EnCnX:Pwpl9bCJU'], ['176.103.48.233', '8080', '8ax7EnCnX:Pwpl9bCJU'], ['176.103.48.235', '8080', '8ax7EnCnX:Pwpl9bCJU'], ['176.103.49.231', '8080', '8ax7EnCnX:Pwpl9bCJU'], ['176.103.49.232', '8080', '8ax7EnCnX:Pwpl9bCJU'], ['176.103.49.233', '8080', '8ax7EnCnX:Pwpl9bCJU'], ['176.103.49.235', '8080', '8ax7EnCnX:Pwpl9bCJU'], ['176.103.50.230', '8080', '8ax7EnCnX:Pwpl9bCJU'], ['176.103.50.233', '8080', '8ax7EnCnX:Pwpl9bCJU'], ['176.103.50.234', '8080', '8ax7EnCnX:Pwpl9bCJU'], ['176.103.51.230', '8080', '8ax7EnCnX:Pwpl9bCJU'], ['176.103.51.231', '8080', '8ax7EnCnX:Pwpl9bCJU'], ['176.103.51.233', '8080', '8ax7EnCnX:Pwpl9bCJU'], ['176.103.51.234', '8080', '8ax7EnCnX:Pwpl9bCJU'], ['176.103.48.236', '8080', '8ax7EnCnX:Pwpl9bCJU'], ['176.103.49.236', '8080', '8ax7EnCnX:Pwpl9bCJU'], ['217.12.210.144', '8080', '8ax7EnCnX:Pwpl9bCJU'], ['217.12.210.145', '8080', '8ax7EnCnX:Pwpl9bCJU'], ['217.12.210.146', '8080', '8ax7EnCnX:Pwpl9bCJU'], ['217.12.210.147', '8080', '8ax7EnCnX:Pwpl9bCJU'], ['217.12.210.149', '8080', '8ax7EnCnX:Pwpl9bCJU'], ['217.12.210.152', '8080', '8ax7EnCnX:Pwpl9bCJU'], ['217.12.210.153', '8080', '8ax7EnCnX:Pwpl9bCJU'], ['46.148.21.41', '8080', '8ax7EnCnX:Pwpl9bCJU'], ['46.148.21.42', '8080', '8ax7EnCnX:Pwpl9bCJU'], ['46.148.21.43', '8080', '8ax7EnCnX:Pwpl9bCJU'], ['46.148.21.44', '8080', '8ax7EnCnX:Pwpl9bCJU'], ['46.148.21.45', '8080', '8ax7EnCnX:Pwpl9bCJU'], ['46.148.21.46', '8080', '8ax7EnCnX:Pwpl9bCJU'], ['46.148.21.47', '8080', '8ax7EnCnX:Pwpl9bCJU'], ['46.148.21.48', '8080', '8ax7EnCnX:Pwpl9bCJU'], ['5.34.183.24', '8080', '8ax7EnCnX:Pwpl9bCJU']]
AMOUNT_THREADS = 100
AMOUNT_PROCESS = 5

def get_url_from_file(f)->"gen":
    """
    вытаскивает из файла все ссылки, и делает из них список
    """
    file_ = open(f, 'r').read().split()
    a = [i for i in file_]
    return a


def get_html(url:'proxy')->'html':
    """
    открывает ссылку и читает html файл
    меняет прокси, когда счетчик ссылок доходит к определенному значению
    """
    proxy  = urllib.request.ProxyHandler(get_html.__annotations__['url'])
    auth = urllib.request.HTTPBasicAuthHandler()
    opener = urllib.request.build_opener(proxy, auth, urllib.request.HTTPHandler)
    urllib.request.install_opener(opener)
    #print(proxy)

    try:
        response = opener.open(url)
        #response = urllib.request.urlopen(url)
        return response.read()
    except urllib.error.URLError:
        return get_html(url)

def get_page_count(html)->list:
    """
    если на странице товара есть вложенные страници,
    эта функция возвращает ссылки на них
    """
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
    """
    создает объект для парсинга
    парсит страници товаров по необходимым тегам
    """
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


def list_proxy(f):
    """
    дает список прокси серверов из файла
    """
    with open(f) as csvfile:
        p = csv.reader(csvfile, delimiter = ';')
        proxy_list = [row for row in p]
    return proxy_list[1:]

def give_proxy(l):
    """
    дает случайный прокси из списка
    """
    r = random.Random()
    random_proxy = r.choice(l)
    l.pop(l.index(random_proxy))
    #print(random_proxy)
    return {'http': 'http://{0}@{1}:{2}'.format(random_proxy[2],
                                                random_proxy[0],
                                                random_proxy[1]
                                                )
            }


def save(projects, path):
    """
    сохраняет результаты парсинга в csv формат
    """
    with open(path, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(('Модель', 'Магазин', 'Цена'))

        for project in projects:
            writer.writerow((project['title'], project['market'],
                             project['price']))

def save_whole_links_to_txt(l):
    """
    сохраняет вложенные страници по товарам в файл
    """
    with open('save_full_list.txt', 'w') as tmp:
        for i in l:
            writer = csv.writer(tmp)
            writer.writerow(BASE_URL+i)
def open_file(f)->list:
    """
    открывает ссылки на товар "где купить"
    возвращает готовые ссылки, которые можно преобразовывать в html
    и затем парсить
    """
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

    get_html.__annotations__['url'] = give_proxy(LIST_PROXY)
    projects = []
    urls = []
    with Timer() as t:
        for page in range(0, page_count):
            urls.append('{0}{1}'.format(BASE_URL, list_with_fold_pages[page]))
        #block_of_fold_pages = divider(urls)

        #l = thread_executor(list_with_fold_pages, AMOUNT_PROCESS)
        with ProcessPoolExecutor(AMOUNT_PROCESS) as executor:
            a, b = 1, 0
            #for html in executor.map(get_html, urls): # for fold page
            for html in executor.map(get_html, list_with_fold_pages):
                print(get_html.__annotations__['url'])
                if b <= (int(page_count * 0.07 + 1)):
                    b += 1
                else:
                    b = 0
                    get_html.__annotations__['url'] = give_proxy(LIST_PROXY)
                print('Парсинг %d%%' % ((a / page_count) * 100))
                projects.extend(parse(html))
                a += 1

    print('Блок парсинга выполняется за {0} сек.'.format(t.secs))

    with Timer() as t:
        save(projects, 'projects.csv')
    print('Сохранение выполняется за {0} сек.'.format(t.secs))
if __name__ == '__main__':
    with Timer() as t:
        main()
    print('Все выполняется за {0} сек.'.format(t.secs))

