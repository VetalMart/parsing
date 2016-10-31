"""
Модуль parser с переделанной логикой.
"""

from config.base_config import *
from config.local_config import *
from config.user_agent import USER_AGENT

def work_cursor(data):
    """Функция выполняющая работу курсора с базой."""
    try:
        db = msq.connect(host='localhost', user=USER,
                        passwd=PASSWD, db=DB,
                        charset='utf8')
        cursor = db.cursor()
        cursor.execute(data)
        db.commit()
        return cursor
    finally:
        db.close()

def reset_proxy_table():
    """
    Установка значения в любую таблицу.
    d - данные которые необходимо установить.
    """
    a = work_cursor(""" select max(id) from proxy_list;""").fetchall()[0][0]
    reset_dict = {
        COLM_USER_AGENT: '',
        COLM_STATE: 0,
        COLM_TIME_USING: 0 ,
        COLM_USES_COUNT: 0,
        COLM_SPEED: 0,
        COLM_DATE_ACTUAL: 'NULL',
        COLM_ACTIVE: 1,
        COLM_ERROR_CODE: 0,
        COLM_ERROR_MESSAGE: 'NULL',
        COLM_ERROR_NUM_CHECK: 0,
    }
    # Очистка необходимых колонок в таблице, при помощи словаря.
    for i in range(1, a+1):
        for j in reset_dict:
            work_cursor("""update proxy_list set {0}="{1}"
                where id={2}""".format(
                j, reset_dict[j], i
            ))
class Proxy():
    """
    Класс который работает с прокси.
    Экземпляр класса свободный и валидный прокси с базы данных, и возв-
    ращает данные по прокси. Имеются дополнительные функции, такие как
    собрать информацию по этому прокси, записать изменненные данные,по-
    чистить данные в базе данных прокси,записать информацию по ошибках
    которые произошли по этим прокси.
    """
    def __init__(self, host_resource, user_agent):
        """
        host_resource - нужен для того, что бы записывался в бд.
        """
        # Проверка, если ли рабочие прокси. Если нет, то выходим с прог-
        # рамы.
        self.get_random_proxy_and_its_info()
        if not self.reset_constructor:
            # Здесь мы получаем рандомный прокси следующей функцией.
            # Будем получать с классов convertor-ов.
            self.user_agent = user_agent
            """
            Если прокси не забанен, и если он не используется сейчас,
            мы его используем.
            """
            # К финальному прокси дойдет только когда респонс будет.
            self.final_proxy = self.get_final_proxy()
            self.final_proxy_access = self.proxy_access
            self.final_proxy_ip = self.proxy_ip
            self.final_proxy_port = self.proxy_port
            self.uses_count += 1
            self.time_set = time()
            self.date_actual = time()
            dict_changes = {
                COLM_RESOURCES: host_resource,
                COLM_USER_AGENT: self.user_agent,
                COLM_STATE: 1,
                COLM_TIME_USING: self.time_set ,
                COLM_USES_COUNT: self.uses_count,
                COLM_DATE_ACTUAL: self.date_actual
            }
            self.set_info(dict_changes)

    def amount_rows(self):
        """
        Вспомагательная функция.
        Определяем количество строк в таблице.
        Выдает случайное число в диапазоне количества строк в таблице,с
        прокси адресами. Минус 1, потому что в MySQL отсчет идет с  0 и
        хоть там и 112 значений, [0, 111] or [0, 112)
        """
        a = work_cursor(""" select max(id) from proxy_list;""").fetchall()[0][0]
        # Случайное число строки в таблице. +1 из-за свойств randrange.
        r = randrange(1, a+1)
        # a-количество прокси в таблице, r-номер случайного прокси.
        return(a, r)

    def get_random_proxy_and_its_info(self):
        """Получает всю информацию по прокси."""
        # Выбираем одно случайное поле с таблици.
        r = work_cursor("""
                    select * from proxy_list where state = 0 and active = 1
                    and error_code <= 5 and error_num_check <= 10
                    order by rand() limit 1;""").fetchall()
        #print(r)
        if bool(r):
            # Флаг перегрузки конструктора.
            self.reset_constructor = False
            r_proxy = r[0]
            # Заполнение свойств экземпляра объекта.
            # Id для прокси.
            self.proxy_id = r_proxy[0]
            # ip прокси.
            self.proxy_ip = r_proxy[2]
            # Порт прокси.
            self.proxy_port = r_proxy[3]
            # Доступ к приватным прокси(логин:пароль)
            self.proxy_access = r_proxy[4]
            # Количество использований за последнюю сессию.
            self.uses_count = int(r_proxy[10])
            # Флаг актвности: 1 - активен, 0 - не активен.
            self.state = r_proxy[11]
            # Флаг пригодности: 1 - рабочий, 0 - не рабочий.
            self.active = r_proxy[12]
            # Ошибки прокси
            self.error_code = r_proxy[13]
        else:
            self.reset_constructor = True

    def get_final_proxy(self):
        """
        Функция которая выдает прокси.
        """
        return {'http': 'http://{0}@{1}:{2}'.format(
            self.proxy_access,
            self.proxy_ip,
            self.proxy_port
            )
        }

    def set_info(self, d):
        """
        Установка значения в любую таблицу.
        d - словарь где:
            ключ - 'колонка в таблице',
            значение - собственно значение
        """
        for i in d:
            work_cursor(
                """update proxy_list set {0}="{1}" where id={2}""".format(
                    i, d[i], self.proxy_id
                )
            )

    def deactivate_proxy(self):
        """
        Функция для деактивации прокси, после окончания его
        использования.
        """
        work_cursor("""
            update proxy_list set {0}={1} where id={2}""".format(
                COLM_STATE, 0, self.proxy_id
            )
        )

    def set_proxy_error(self, error_message):
        """
        Для начала проверим если у этого прокси были ошибки
        больше 5 раз, то ставим его в разряд не рабочих для
        этой сессии.
        И только тогда будем выполнять код самой функции.
        Установка ошибки прокси, если он вылетает по какой
        либо причине.
        Приплюсовывает значение в колонке ошибок к этому прокси.
        """
        if self.error_code >= 5:
            # Установка флага не рабочего прокси.
            d = {COLM_ACTIVE: 0, COLM_ERROR_CODE: 0}
            self.set_info(d)
        else:
            self.error_code += 1
            d = {
                    COLM_ERROR_CODE: self.error_code,
                    COLM_ERROR_MESSAGE: error_message
            }
            self.set_info(d)

class LinksGoods():
    """
    этот класс имеет функции которые:
    + сохраняет необходимую информацию по товару в базу mysql
    + при необходимости берет линки(основные) товаров с базы
    """
    def post_links_to_EuropHotlineLinks(self, url_file):
        """
        !!!Функция для меня.Для заливки ссилок в базу с текстового фай-
        ла. С ек.юа
        """
        with open(url_file, 'r') as f:
            for url in f:
                name = Parse_ek(url).get_name()
                work_cursor("""
                    insert into EuropHotlineLinks (product,
                    link_agregator, update_date, host_agregator)
                    values ("{0}", "{1}", "{2}", "{3}");""".format(
                        name, url, time(), 'ek.ua',
                    )
                )

    def get_id_name_link(self):
        """
        Функция выбирает актуальние id, name,links,product_id_c,по двум
        критериям: по host_agregator и update_date,  возвращает tuple с
        данными.
        """
        self.info_tuple = work_cursor("""
            select id, product, product_id_c, link_agregator
            from EuropHotlineLinks where host_agregator = "{host_agregator}"
            and {now}-update_date > {update_time}
            and not_found <> 1;""".format(
                host_agregator = argv[1],
                now = time(),
                update_time = UPDATE_TIME,
                )
            ).fetchall()
        return self.info_tuple

    def update_date_wares(self, prod_id):
        """
        Обновляет дату для ссылки в базе.
        """
        work_cursor("""
            update EuropHotlineLinks
            set update_date = {now}
            where host_agregator = "{host_agregator}"
            and {now}-update_date > {update_time}
            and product_id_c = {product_id};""".format(
                host_agregator = argv[1],
                now = time(),
                update_time = UPDATE_TIME,
                product_id = prod_id,
                )
            )

    def post_wares_to_EuropHotlineLinks_prices_list(self, zip_dict_data):
        """Функция добаления товаров в базу данных прайса."""
        def extract_dict_values(dict_, position='all', flag=True):
            """
            Извлечение данных с сложного словаря типа:
            {(a, b, c):[[f1],[c3],[d4],[n1]]}
            что бы можно было как с ключа,так и с значения извлечь дан-
            ные по номеру позиции.
            Если flag=True - извлекается ключ. False-значение.
            Если position не задан, или задан all -  возвращается  все
            значение.
            """
            if flag:
                for i in dict_:
                    if position=='all':
                        return i
                    else:
                        return i[position]
            else:
                for i in dict_:
                    if position=='all':
                        return dict_[i]
                    else:
                        return dict_[i][position]

        # Проверка есть ли в базе прайс листа товар с id-шником
        # с линковой базы и необходимым магазином.
        for i in extract_dict_values(zip_dict_data, flag=False):
            a = work_cursor("""
                insert into EuropHotlineLinks_prices_list
                (prag_id, product_id, shop, prop, price,
                    price_txt, update_date, presence)
                    value ("{prag_id}", "{product_id}",
                    "{shop}", "{prop}", "{price}",
                    "{price_txt}","{now}", "{presence}")

                    on duplicate key update
                    prop = "{prop}",
                    price = "{price}",
                    price_txt = "{price_txt}",
                    update_date = "{now}"

                    ;""".format(
                    prag_id = extract_dict_values(zip_dict_data, position=0),
                    product_id = extract_dict_values(zip_dict_data, position=2),
                    shop = i[2].replace('\n', ""),
                    prop = extract_dict_values(zip_dict_data, position=1).replace('\n', ""),
                    price = float(i[1]),
                    price_txt = i[1].replace('\n', "") + ' грн.',
                    now = time(),
                    presence = 0,
                    )
                )

class HotConvertor():
    """
    Класс для парсинга сайтов с большим количеством js скриптов, в на-
    шем случае, это будет хотлайн. Он запускает сессию вебдрайвера,че-
    рез который подключается фантом. Это имитация работы, браузера.
    """
    def __init__(self, link):
        """
        Задаем для вебдрайвера список с сервисными аргументами, и желаемы-
        ми возможностями. В сервисных аргументах отлючаем загрузку  карти-
        нок, подключаем прокси, можно задать и пользователя. Но я его  за-
        дал в желаемых настройках. Возможно, я удалю желаемые возможности,
        и оставлю только сервисные аргументы.Или вообще оставлю что то од-
        но. Оно в приципе выполняет одини и те же функции.
        """
        self.link = link
        self.user_agent = choice(USER_AGENT)
        self.proxy_obj = Proxy('hotline.ua', self.user_agent)
        if self.proxy_obj.reset_constructor:
            self.reset_constructor = True
            self.error_becouse_proxy_constructor = True
        else:
            self.reset_constructor = False
            self.error_becouse_proxy_constructor = False
            self.browser = webdriver.PhantomJS(
                desired_capabilities=self.options()[0],
                service_args = self.options()[1]
            )
            self.browser.set_page_load_timeout(30)
    def options(self):
        """
        Функция в которой задаются все опции для вебдрайвера.
        """
        # Берем юзер-агент с файла.
        # Строка для разделения имени пользователя прокси, и его пароль.
        # Потому что при чтении с базы, идет одной строкой, а для фантома
        # нужно раздельно.
        up = self.proxy_obj.final_proxy_access.split(':')
        # Имя эмулированного браузера.
        self.browserName = choice(list(BROWSER_VERSION.keys()))
        # Версия эмулированого браузера.
        self.version = choice(BROWSER_VERSION[self.browserName])
        self.platform = choice(PLATFORM)
        self.serv_ar = []
        self.serv_ar.append('--load-images=no')
        self.serv_ar.append('--local-to-remote-url-access=yes')
        self.serv_ar.append('--proxy-type=https')
        self.serv_ar.append('--proxy={address}:{port}'.format(
            address=self.proxy_obj.final_proxy_ip,
            port=self.proxy_obj.final_proxy_port)
        )
        self.serv_ar.append('--proxy-auth={user}:{passw}'.format(
            user=up[0], passw=up[1]))
        # Следующая строчка: при первом запуске - сохраняет в текстовый файл
        # куки, в если этот файл уже есть, то куки беруться с него.
        self.serv_ar.append('--cookies-file=cookies.txt')
        self.dcap = dict(DesiredCapabilities.PHANTOMJS)
        self.dcap["phantomjs.page.settings.userAgent"] = self.user_agent
        self.dcap["phantomjs.page.settings.platform"] = self.platform
        self.dcap["phantomjs.page.settings.browserName"] = self.browserName
        self.dcap["phantomjs.page.settings.version"] = self.version
        self.dcap["phantomjs.page.settings.nativeEvents"] = "False"
        self.dcap["phantomjs.page.settings.takesScreenshot"] = "False"
        self.dcap["phantomjs.page.settings.driverName"] = ""
        self.dcap["phantomjs.page.settings.driverVersion"] = ""
        # CSS селекторы для поиска елементов.
        self.dcap["phantomjs.page.settings.cssSelectorsEnabled"] = "True"
        self.dcap["phantomjs.page.settings.javascriptEnabled"] = "True"
        return (self.dcap, self.serv_ar)
    def reset_browser_cookies(self):
        """
        Откривает простенькую страницу, в данном случае базовую, получает
        куки, пересохраняет куки в киевские, удаляет предыдущие куки  веб-
        драйвера, присваивает хитрый список с куками(измененными) вебдрай-
        веру.
        !Пробовал перезапускать вебдрайвер,построив функцию которая берет
        куки только раз в сутки, но для новой страница, которая еще не за-
        ружалась, невозможно задать куки наперед. При новой загрузке (при
        инициализации) вебдрайвера, они загружаються новые, а сохраненные
        можно применить, только во второй загрузке. Выходит,что время заг-
        рузки уваличиваеться на одну полную загрузку страници фантомом.
        """
        def change_cookies(data):
            """
            Вспомагательная функция.
            Изменяет куки на Киевские. Входящим данными есть список  словарей,
            в которых даны куки, с проработаной небольшой страници, желательно
            этого же сайта.
            """
            for i in data:
                if i['name']=='city_id':
                    i['value'] = '187'
                if i['name']=='region_mode':
                    i['value'] = '1'
                if i['name']=='region':
                    i['value'] = '1'
                if i['name']=='region_popup':
                    i['value'] = '3'

        try:
            self.browser.get(self.link)
            #sleep(10)
            tmp_cookies = self.browser.get_cookies()
            change_cookies(tmp_cookies)
            self.kiev_cookies = tmp_cookies
            self.browser.delete_all_cookies()
            for cookie in self.kiev_cookies:
                # Тут удалил expiry - из за него был баг.
                self.browser.add_cookie({k: cookie[k] for k in (
                    'name', 'value', 'domain',
                    'path',  'secure', #'expiry',
                    'httponly',
                    ) if k in cookie
                }
            )
        except (SeleniumTimeout) as e:
            print("Загрузка страници для получения куков, завершена по таймауту")
            # Получаем класс ошибки, записываем его в бд прокси, и выкл.прокси.
            error_message = e.__class__
            self.proxy_obj.deactivate_proxy()
            self.proxy_obj.set_proxy_error(error_message)
            self.browser.quit()
            self.reset_constructor = True

    def get_html(self):
        """
        Получаем html на выходе. В начале отратываем функцию перезагрузки
        куков, и собственно загружаем необходимую нам страницу.  Перехват
        ошибки - я не в курсе, иногда срабатывает. И в конце, обязательно
        закрываем вебдрайвер. Жрет много ресурсов, и зависает в памяти.
        """
        try:
            # Проверяем есть ли файл с куками. И не старый ли он.
            # Если нет, или старый - пересоздаем.
            if (
                (not os.path.exists('cookies.txt')) or
                (time() - os.path.getctime('cookies.txt') > 86000)
            ):
                print('выполнилось куковое условие')
                self.reset_browser_cookies()

            self.browser.get(self.link)
            #sleep(10)
            data = self.browser.page_source
            self.proxy_obj.deactivate_proxy()
            self.browser.quit()
            # Строчка которая выдает результат всего класса. (html, proxy_id)
            t = (data, self.proxy_obj.proxy_id)
            return t
        except (Exception,
            http.client.HTTPException,
            http.client.BadStatusLine,
            ConnectionRefusedError,
            SeleniumTimeout,
                ) as e:
            # Получаем класс ошибки, записываем его в бд прокси, и выкл.прокси.
            error_message = e.__class__
            self.proxy_obj.deactivate_proxy()
            self.proxy_obj.set_proxy_error(error_message)
            self.browser.quit()
            print("ошибка {0} в get_html".format(e.__class__))
            self.reset_constructor = True

class Parse_hotline():
    """
    Базовый класс для парсинга хотлайна, функции маленькие, компактные.
    Построен по принципу "от центра" - сходится в конструкторе.
    """
    def __init__(self, html__r_int):
        """
        конструктор наследуется от базового класса, только  изменяется
        базовый линк в конструкторе будут приниматься аргуметы, и обра-
        батываться последующими функциями
        """
        self.base_url = HOTLINE_BASE_URL
        self.html_ = html__r_int[0]
        # Порядковый номер прокси, с которого парсил фантом.
        # Нужен в случае капчи: по этому номеру будет устанавливаться
        # счетчик капчи.
        self.proxy_id = html__r_int[1]
        # На случай ошибки формирования lxml документа, делаю перехват.
        # Флагом bad_html, если get_doc прошло - то ставлю False.
        try:
            self.lxml_doc = self.get_doc()
            self.bad_html = False
            self.captcha_hard = self.cruel_capcha(self.html_)
            self.captcha_light = self.get_captcha()
            if (not bool(self.captcha_light)) and (not bool(self.captcha_hard)):
                self.name =  self.get_name()
                self.prices = self.get_prices()
                self.markets = self.get_markets()
                self.wares = self.get_wares()
                self.city = self.get_city()
            else:
                self.reset_captcha_counter()
        except ValueError:
            print("Фантом выдал кривой html.")
            self.bad_html = True

    def space_cutter(self, some_str):
        """Функция удаления лишних пробелов с строки"""
        b = some_str.split()
        c = ''
        for i in b:
            c += i + ' '
        return c.strip()
    def pretty(self, x):
        return x.text_content().strip().replace('\xa0', ' ')

    def get_doc(self):
        return lh.document_fromstring(self.html_)

    def get_name(self,
                 selector = 'h1',
                 ):
        name = self.lxml_doc.cssselect(selector)[0].text_content()
        return self.space_cutter(name.replace('\n', ' '))

    def get_prices(self, path = '//*[@id="gotoshop-price"]'):
        return [
                self.pretty(price).replace(' ', '')[:-6]
                for price in self.lxml_doc.xpath(path)
                ]

    def get_markets(self, class_n = 'cell shop-title'):
        return [self.pretty(market) for market in self.lxml_doc.find_class(class_n)]

    def get_wares(self):
        return [[self.name, price, market] for (price, market)
                      in zip(self.prices, self.markets)]

    def get_city(self):
        return self.lxml_doc.find_class('user-city-link')[0].text_content()
    def cruel_capcha(self, data):
        fucking_shit = '<html><head></head><body></body></html>'
        if data == fucking_shit:
            print('Жесткая капча, прокси с id = {0} заблокирован'.format(self.proxy_id))
            work_cursor("""update proxy_list set
                        error_num_check = error_num_check + 10
                        where id = {0};""".format(self.proxy_id)
                )
            return [1, ]
        else:
            return []
    def get_captcha(self):
        """
        Функция для улавливания капчи.
        """
        return self.lxml_doc.find_class('g-recaptcha')
    def reset_captcha_counter(self):
        """
        Функция переустановки счетчика капчи, в базе данных прокси-серверов.
        """
        work_cursor(
            """update proxy_list set error_num_check = error_num_check + 1
               where id = {0};""".format(self.proxy_id)
            )

class Parse_ek():
    """
    Базовый класс для парсинга ссилок с ек.юа. Входним параметром, для
    конструктора есть ссилка, на любой товар с сайта ек.юа. Это  может
    быть абсолютно любая ссылка на товар, все равно она конвертируется
    в нужный для парсинга формат.
    ==================================================================
    Класс построен неплохо, по принципу "коридора",  но на мой  взгляд
    много многозадачных  функций, но работает хорошо. Все функции рабо-
    тают на одну главную функцию,  которая доступна пользователю. Ну и
    пусть :)
    """
    def __init__(self, link):
        self.link = link
        self.user_agent = {'User-Agent': choice(USER_AGENT)}
        self.proxy_obj = Proxy('ek.ua', self.user_agent)
        self.base_url = self.__check_base_url()
        self.full_wares_list = []
        self.no_markets_error = False

    def __check_base_url(self):
        """Проверка на принадлежность к нужному сайту."""
        if 'ek.ua' in self.link:
            base_url = 'http://www.ek.ua'
            return base_url
        else:
            print(self.link, "Link not refers to ek.ua")
            return False

    def __url_html_requests(self, url):
        """Открытие страници, при помощи библиотеки Requests."""
        page_doc = requests.get(
                url, cookies=COOKIE_KIEV,
                headers=self.user_agent,
                proxies=self.proxy_obj.final_proxy,
                timeout=10,
        )
        assert page_doc.status_code == 200, "url_to_html_request:site don't open"
        assert page_doc.encoding == 'utf-8', "url_to_html_request:bad encoding"
        return page_doc.text

    def __make_pretty_url(self):
        """Функция обязательного перехода на страници с ценами."""
        assert 'ek.ua' in self.link, 'Входящая ссылка не ek.ua'
        # Открывем урл, в ютф-8.
        html_str = self.__url_html_requests(self.link)
        # Закидам док для парсинга в лхмл.
        lxml_doc = lh.document_fromstring(html_str)
        # Проверка города, должен быть Киев.
        city = lxml_doc.find_class('header_action_change-city')
        self.city = city[0].text_content()
        assert self.city == 'Киев','__make_p_u:Город {0}'.format(self.city)
        # Берем ссылку на страницу с магазинами и их количество.
        table_price = lxml_doc.cssselect('div.desc-menu')[0].cssselect('a')[0]
        assert table_price != [], "make_pretty_url:пустой lxml_doc.что-то"
        # Окончание ссылки на страницу с ценами.
        price_href = table_price.get('href')
        assert price_href != [], "make_pretty_url:price_href=[]"
        # Контрольная цифра количества магазинов (проверка в конце).
        self.price_count = table_price.text_content().split()[-1]
        assert table_price != None, "make_pretty_url:price_count=None"
        # Финальная ссылка по которой непосредственно идет парсинг.
        self.price_link = self.base_url + price_href
        assert 'ek.ua/prices/' in self.price_link, 'make_pretty_url:output has no price_link'

    def __get_wares_from_one_page(self, url):
        """Функция парсинга страници с товарами."""
        # Открывем урл, в ютф-8.
        html_str = self.__url_html_requests(url)
        # Создаем док для парсинга лхмл.
        lxml_doc = lh.document_fromstring(html_str)
        # Берем ссылку на пагинации и их количество.
        css_price_table = 'table.where-buy-table'
        info_table = lxml_doc.cssselect(css_price_table)
        if info_table == list():
            self.no_markets_error = True
            assert info_table != [], 'get_w_f_page:info table empty'

        names = info_table[0].cssselect('h3')
        prices = info_table[0].find_class("where-buy-price")
        assert prices != [], 'get_w_f_page:no prices for wares'
        markets = info_table[0].find_class('it-shop')
        assert markets != [], 'get_w_f_page:no markets for wares'
        assert len(names)==len(markets)==len(prices), 'get_w_f_page:diff n/p/m'
        result_list = []
        for (i,j,k) in zip(names, prices, markets):
            result_list.append(
                [i.text_content().strip(),
                j.cssselect('a')[0].text_content().strip().replace('\xa0', '').replace('грн.', ""),
                k.text_content()
                ]
            )
        self.full_wares_list.extend(result_list)

    def __make_paggination_list(self):
        """Список ссылок пагиннаций."""
        assert 'ek.ua/prices/' in self.price_link, 'make_paggination_list:ссылка не price'
        # Открывем урл, читаем в байт.строку, конвертируем в ютф-8.
        html_str = self.__url_html_requests(self.price_link)
        # Создаем док для парсинга лхмл.
        lxml_doc = lh.document_fromstring(html_str)
        class_paggination = 'ib page-num'
        paggination_table = lxml_doc.find_class(class_paggination)
        if paggination_table != []:
            for i in paggination_table[0]:
                # В этой таблице находим страницу для парсинга, и сразу парсим
                tmp_paggination_link = self.base_url + i.get('href')
                self.__get_wares_from_one_page(tmp_paggination_link)
        else:
                self.__get_wares_from_one_page(self.price_link)

    def get_wares_from_url(self):
        """Собирает в кучу функции загрузки/поиска падингов/парсинга."""
        try:
            if self.proxy_obj.reset_constructor:
                self.reset_constructor = True
                self.error_becouse_proxy_constructor = True
            else:
                self.reset_constructor = False
                self.error_becouse_proxy_constructor = False
                # Создаем ссылку с ценами и получаем контрольное число.
                self.__make_pretty_url()
                # Создаем список ссылок паггинаций, в котором и идет создание
                # списка товаров
                self.__make_paggination_list()
                assert len(self.full_wares_list) == int(self.price_count), 'get_w_f_url:wares != control number'
                # Деактивируем прокси.
                self.proxy_obj.deactivate_proxy()
        except AssertionError:
            if self.no_markets_error:
                print("нет магазинов по ссылке, отключаем ее {0}".format(self.price_link))
                self.reset_constructor = False
        except (Exception) as e:
            error_message = e.__class__
            #print(error_message)
            self.proxy_obj.deactivate_proxy()
            self.proxy_obj.set_proxy_error(error_message)
            self.reset_constructor = True

    def get_name(self):
        """
        Функция для получения имени товара, по указаной ссылке.
        """
        try:
            page_doc = requests.get(self.link).text
            lxml_doc = lh.document_fromstring(page_doc)
            return lxml_doc.find_class('t2 no-mobile')[0].text_content()
        except ValueError:
            print('Parse_ek:get_name: error lxml bad doc')
            self.get_name(url)


#!!! Эта колонка - это время за которое прокси отработал ссылку
     #               COLM_SPEED: self.speed_test_tuple[0],
#!!! Добавить в convertor:<
# 1. установку времени отработки прокси
# 2. установку ошибки прокси, деактивация прокси, error_message,
# deactivate_proxy - короче перенести в convertor set_proxy_error()

