import http
import os
from multiprocessing import Pool, Lock
from sys import argv, exit
from random import choice, randint, randrange
from time import time, sleep
from functools import reduce

from selenium import webdriver
from selenium.common.exceptions import TimeoutException as SeleniumTimeout
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import requests
import lxml.html as lh
import pymysql as msq

DB = 'parsing'
#URL_FILE = sys.argv[1]
#PROXY_FILE = sys.argv[2]
# список таблиц в базе mysql
FULLURL = 'fullurl'
MAINURL = 'mainurls'
PROXYLIST = 'proxylist'
PROXY_LIST = 'proxy_list'
# Id для прокси.
COLM_ID = 'id'
# ip прокси.
COLM_PROXY_IP = 'proxy_ip'
# Порт прокси.
COLM_PROXY_PORT = 'proxy_port'
# Доступ к приватным прокси(логин:пароль)
COLM_PROXY_ACCESS = 'proxy_access'
# Время загрузки страници при тестировании.
COLM_SPEED = 'speed'
# Дата проверки прокси
COLM_DATE_ACTUAL = 'date_actual'
# Время начала использования прокси.
COLM_TIME_USING = 'time_using'
# Версия браузера.
COLM_USER_AGENT = 'user_agent'
# Количество использований за последнюю сессию.
COLM_USES_COUNT = 'uses_count'
# Флаг работы: 1 - сейчас работет, 0 - нет.
COLM_STATE = 'state'
# Флаг пригодности прокси: 1 - рабочий, 0 - нет.
COLM_ACTIVE = 'active'
# Установка ошибки прокси
COLM_ERROR_CODE = 'error_code'
# Описание ошибки.
COLM_ERROR_MESSAGE = 'error_message'
# Количество попадания на капчу с данного прокси.
COLM_ERROR_NUM_CHECK = 'error_num_check'

COLM_RESOURCES = 'resources'

FREE_PROXYLIST = 'freeproxy'
WARES = 'wares'
COLM_FULLULR = 'furl'
COLM_MAINURL = 'url'
COLM_WARES_NAME = 'name'
COLM_WARES_MARKET = 'market'
COLM_WARES_PRICE = 'price'
# Время ответа прокси
PROXY_RESPONCE = 0.5
# Время обновления данных.
UPDATE_TIME = 10

# количество процессов и потоков
AMOUNT_PROCESS = 2
AMOUNT_THREADS = 10
# для работы основного модуля
EK_BASE_URL = 'http://ek.ua'
HOTLINE_BASE_URL = 'http://hotline.ua'

COOKIE_KIEV = requests.cookies.RequestsCookieJar()
COOKIE_KIEV.set('PHPSESSID', 'qm7lfihcsbog9ij0mtd7ip1kf0')
COOKIE_KIEV.set('n_session_id_cookie', 'eb6ad6d63f7650c06ba6f5c3f531ad20')
COOKIE_KHAR = requests.cookies.RequestsCookieJar()
COOKIE_KHAR.set('PHPSESSID', 'p99c664br8k7q3f09aspfu63p4')
COOKIE_KHAR.set('n_session_id_cookie', 'eb6ad6d63f7650c06ba6f5c3f531ad20')

'==========================================='
PLATFORM = ['AmigaOS 4', 'FreeBSD', 'NetBSD', 'OpenBSD', 'Linux', 'Windows', 'macOS',]
BROWSER_VERSION = {'Chrome':['40.0.2214', '41.0.2272', '42.0.2311', '43.0.2357',
                             '44.0.2403', '45.0.2454', '46.0.2490', '47.0.2526',
                             '48.0.2564', '49.0.2623', '50.0.2661', '51.0.2704',
                             '52.0.2743', '53.0.2785', '54.0.2840', '55.0'],
                   'Safari':['9.1.3', '10.0', '6.2.8', '5.1.7'],
                   'Firefox':['49.0.1', '45.4.0', '50.0', '51.0', '52.0',
                              '44.0.1', '45.0', '46.0', '47.0', '48.0', '49.0'],
                   'Opera':['30', '31', '32', '33', '34', '35', '36', '37'],
                   'Edge':['38.14393.0.0'],
                   }
