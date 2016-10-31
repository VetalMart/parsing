"""
                        Общая информация по модулю.

User-agent создаються в классе Proxy, и с него передаються в классы для
парсинга. Так же он сразу и используется для тестирования прокси на ско-
рость: что бы не получилась ситуация, что на сайт с одного прокси,  сна-
чала заходить один юзер, через совершенно маленький промежуток  времени
ломиться другой, и загружает всю страницу. Библиотека для  тестирования
requests, а для классов парсеров, уже какая потребуеться.  Для хотлайна,
например используеться webdriver.PhantomJS.
"""

from config.local_config import *
from config.base_config import *
from config.user_agent import USER_AGENT

class Proxy():
    """
    Класс который работает с прокси.
    Класс по сути должен выполнять следующие вещи:
        - возвращать валидный и хороший прокси
            * рандомно
        - записывать логи по использованию этого прокси
        - выбирать прокси в зависимости от данных записанных в нем.
        - отбрасывать прокси, если они не сработали больше (пусть будет
          5 раз)
        - обнулять некоторые данные в конце сессии
    """
    def __init__(self, page_testing_speed, host_resource):
        """
        Задается страница для теста, и имя ресурса.
        """
        # Проверка, если ли рабочие прокси. Если нет, то выходим с прог-
        # рамы.
        if self.avaliability_proxy('active', '<>') != 0:
            self.page_testing_speed = page_testing_speed
            self.table_name = PROXY_LIST
            self.amount_rows()
            # Здесь мы получаем рандомный прокси следующей функцией.
            self.get_info()
            self.user_agent = {'User-Agent': choice(USER_AGENT)}
            self.speed_test_tuple = self.get_speed_test_page()
            """
            Если прокси не забанен, и если он не используется сейчас, а
            так же,если у него время отклика не больше позволенного тог-
            да мы его используем.
            """
            if (self.active == 1 and self.state == 0 and
                    self.speed_test_tuple[0] <= PROXY_RESPONCE
                ):
                # К финальному прокси дойдет только когда респонс будет.
                self.final_proxy = self.speed_test_tuple[1]
                self.final_proxy_access = self.speed_test_tuple[2][0]
                self.final_proxy_ip = self.speed_test_tuple[2][1]
                self.final_proxy_port = self.speed_test_tuple[2][2]
                self.uses_count += 1
                self.time_set = time()
                self.date_actual = time()
                dict_changes = {
                    COLM_RESOURCES: host_resource,
                    COLM_USER_AGENT: self.user_agent['User-Agent'],
                    COLM_STATE: 1,
                    COLM_TIME_USING: self.time_set ,
                    COLM_USES_COUNT: self.uses_count,
                    COLM_SPEED: self.speed_test_tuple[0],
                    COLM_DATE_ACTUAL: self.date_actual
                }
                self.set_info(dict_changes)
            elif self.avaliability_proxy('state', '=') == 0:
                print("""Все доступные прокси в работе. Подождите 30
                         секунд.""")
                sleep(30)
                return self.__init__(self.page_testing_speed,
                                     host_resource)
            else:
                return self.__init__(self.page_testing_speed,
                                     host_resource)
        else:
            print('Все прокси нерабочие. Выходим с программы.')
            exit()

    def work_cursor(self, data):
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
    def amount_rows(self):
        """
        Определяем количество строк в таблице.
        Минус 1, потому что в MySQL отсчет идет с 0
        и хоть там и 112 значений, [0, 111] or [0, 112)
        """
        number_rows = self.work_cursor("""
                        select count(*) from {0};""".format(
                            self.table_name
                          )
                      ).fetchall()[0][0] - 1

        self.amount_rows_in_table = range(0, number_rows)
        # Случайное число строки в таблице.
        self.r_int = choice(self.amount_rows_in_table)

    def get_info(self):
        """Получает всю информацию по прокси."""
        # Выбираем одно случайное поле с таблици.
        r_proxy = self.work_cursor("""
                    select * from {0} limit {1}, 1;""".format(
                        self.table_name, self.r_int
                            )).fetchall()[0]
        # Заполнение свойств экземпляра объекта.
        # Id для прокси.
        self.proxy_id = r_proxy[0]
        # ip прокси.
        self.proxy_ip = r_proxy[2]
        # Порт прокси.
        self.proxy_port = r_proxy[3]
        # Доступ к приватным прокси(логин:пароль)
        self.proxy_access = r_proxy[4]
        # Время загрузки страници при тестировании.
        self.speed = r_proxy[5]
        # Дата проверки прокси
        self.data_actual = r_proxy[7]
        # Время начала использования прокси.
        self.time_using = r_proxy[8]
        # Версия браузера.
        self.user_agent = r_proxy[9]
        # Количество использований за последнюю сессию.
        self.uses_count = int(r_proxy[10])
        # Флаг актвности: 1 - активен, 0 - не активен.
        self.state = r_proxy[11]
        # Флаг пригодности: 1 - рабочий, 0 - не рабочий.
        self.active = r_proxy[12]
        # Ошибки прокси
        self.error_code = r_proxy[13]

    def get_speed_test_page(self):
        """
        Функция подсчета времени открытия базовой страници через данный
        прокси.
        """
        def except_tmp_func(a):
            """Вспомагательная для исключений."""
            self.error_message = a.__class__
            self.deactivate_proxy()
            self.set_proxy_error()
        proxy = {'http': 'http://{0}@{1}:{2}'.format(
            self.proxy_access,
            self.proxy_ip,
            self.proxy_port
            )
        }
        try:
            ping = requests.get(
                self.page_testing_speed,
                proxies=proxy,
                headers=self.user_agent,
                timeout=PROXY_RESPONCE
            ).elapsed.total_seconds()
            if ping <= PROXY_RESPONCE:
                return (ping, proxy, (
                    self.proxy_access,
                    self.proxy_ip,
                    self.proxy_port,
                    )
                )
            else:
                raise requests.exceptions.Timeout()
        except (requests.exceptions.Timeout,
                requests.exceptions.ProxyError,
                requests.exceptions.ConnectionError) as e:
            except_tmp_func(e)
            return (PROXY_RESPONCE + 1, )

    def set_info(self, d):
        """
        Установка значения в любую таблицу.
        d - словарь где:
            ключ - 'колонка в таблице',
            значение - собственно значение
        """
        for i in d:
            self.work_cursor(
                """update {0} set {1}="{2}" where id={3}""".format(
                    self.table_name, i, d[i], self.r_int
                )
            )

    def set_proxy_error(self):
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
                    COLM_ERROR_MESSAGE: self.error_message
            }
            self.set_info(d)

    def deactivate_proxy(self):
        """
        Функция для деактивации прокси, после окончания его
        использования.
        """
        self.work_cursor("""
            update {0} set {1}={2} where id={3}""".format(
                self.table_name, COLM_STATE, 0, self.r_int
            )
        )

    def reset_info(self, table):
        """
        Установка значения в любую таблицу.
        d - данные которые необходимо установить.
        """
        reset_dict = {
            COLM_USER_AGENT: '',
            COLM_STATE: 0,
            COLM_TIME_USING: 0 ,
            COLM_USES_COUNT: 0,
            COLM_SPEED: 'NULL',
            COLM_DATE_ACTUAL: 'NULL',
            COLM_ACTIVE: 1,
            COLM_ERROR_CODE: 0,
            COLM_ERROR_MESSAGE: 'NULL'
        }
        # Очистка необходимых колонок в таблице, при помощи словаря.
        for i in self.amount_rows_in_table:
            for j in reset_dict:
                self.work_cursor("""update {0} set {1}="{2}"
                    where id={3}""".format(
                    table, j, reset_dict[j], i
                ))
    def avaliability_proxy(self, name, s, n=0):
        """
        Функция проверяет доступность прокси в базе.
        name - имя таблици, s - оператор сравнения, n - цифра к которой
        нужно отталкиваться.
        """
        return self.work_cursor("""
            select count(*) from proxy_list where
            {table_name} {compare_operator} {number};""".format(
                table_name=name, compare_operator=s, number=n
            )
        ).fetchall()[0][0]

class MySQL():
    """
    этот класс имеет функции которые:
    + берет прокси с базы MySQL, в случайном порядке
    + проверяет их на валидность и время отклика
    + сохраняет необходимую информацию по товару в базу mysql
    + при необходимости очищает необходимую таблицу базы MySQL
    + при необходимости берет линки(основные) товаров с базы
    """
    def work_cursor(self, data):
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
    def random_proxy(self):
        """
        выбирает случайный прокси с базы MySQL, проверяет его на валид-
        ность и время отклика выдает его на выходе
        """

        db = msq.connect(host='localhost', user=USER,
                        passwd=PASSWD, db=DB,
                        charset='utf8')

        cursor = db.cursor()
        cursor.execute("""select count(*) from {0};""".format(PROXYLIST))
        amount_rows = cursor.fetchall()[0][0]
        def choose_proxy():
            """
            для платных прокси
            вспомагательная функция которая реально выбирает случайный прокси
            """
            r_int = randint(0, amount_rows-1)
            cursor.execute("""select * from {0} limit {1}, 1;""".format(
                        PROXYLIST, r_int))
            r_proxy = [i for i in cursor.fetchall()[0]]
            return {'http': 'http://{0}@{1}:{2}'.format(r_proxy[2],
                                                        r_proxy[0],
                                                        r_proxy[1]
                                                        )
                    }
        def is_good_proxy(pip):
            """
            проверка прокси на работоспособность
            """
            try:
                url = 'http://www.ek.ua'
                headers = {'User-Agent': choice(USER_AGENT)}
                page_doc = requests.get(
                    url, headers=headers,
                    proxies=pip, timeout=PROXY_RESPONCE
                )
            except (
                    requests.exceptions.Timeout,
                    requests.exceptions.ProxyError,
                    requests.exceptions.ConnectionError
            ):
                # вывод прокси который не сработал
                #print ("BAD PROXY: {0}".format(pip))
                return False
            return True

        def checker(a):
            """
            Для платных прокси.
            берет прокси, проверяет - если хороший - возвращает.
            плохой, берет новый
            """
            if is_good_proxy(a):
                return a
            else:
                b = choose_proxy()
                return checker(b)

        pr = choose_proxy()
        return checker(pr)

    def clear_tables(self, ms):
        """
        при необходимости очищает необходимую таблицу базы MySQL
        """
        amount_rows = self.work_cursor("""
            select count(*) from {0};""".format(
                ms
            )
        ).fetchall()[0][0]

        self.work_cursor("""
            delete from {0} limit {1};""".format(
                ms, amount_rows))
        print('delete {0} positions'.format(amount_rows))

    def post_links_to_EuropHotlineLinks(self, url_file):
        """
        !!!Функция для меня.Для заливки ссилок в базу с текстового фай-
        ла. С ек.юа
        """
        with open(url_file, 'r') as f:
            for url in f:
                name = Parse_ek(url).get_name()
                self.work_cursor("""
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
        self.info_tuple = self.work_cursor("""
            select id, product, product_id_c, link_agregator
            from EuropHotlineLinks where host_agregator = "{host_agregator}"
            and {now}-update_date > {update_time} ;""".format(
                #limit {r_int}, 1000
                host_agregator = argv[1],
                now = time(),
                update_time = UPDATE_TIME,
                #r_int = randint(0, 20000)
                )
            ).fetchall()
        return self.info_tuple

    def update_date_wares(self, prod_id):
        """
        Обновляет дату для ссылки в базе.
        """
        self.work_cursor("""
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
            a = self.work_cursor("""
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
        self.base_url = self.__check_base_url()
        self.full_wares_list = []

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
        try:
            page_doc = requests.get(
                    url, cookies=COOKIE_KIEV,
                    headers=self.proxy_obj.user_agent,
                    proxies=self.proxy_obj.final_proxy
            )
            assert page_doc.status_code == 200, "url_to_html_request:site don't open"
            assert page_doc.encoding == 'utf-8', "url_to_html_request:bad encoding"
            return page_doc.text
        except:
            self.get_wares_from_url()
        finally:
            self.proxy_obj.deactivate_proxy()

    def __make_pretty_url(self):
        """Функция обязательного перехода на страници с ценами."""
        try:
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
        except ValueError:
            print("__make_pretty_url lxml не сконвертировал в док")
            #self.get_wares_from_url()
            self.__make_pretty_url()

    def __get_wares_from_one_page(self, url):
        """Функция парсинга страници с товарами."""
        try:
            # Открывем урл, в ютф-8.
            html_str = self.__url_html_requests(url)
            # Создаем док для парсинга лхмл.
            lxml_doc = lh.document_fromstring(html_str)
            # Берем ссылку на пагинации и их количество.
            css_price_table = 'table.where-buy-table'
            info_table = lxml_doc.cssselect(css_price_table)

            names = info_table[0].cssselect('h3')
            assert names != [], 'get_w_f_page:no names for wares'
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
        except ValueError:
            print('__make_paggination_list lxml bad doc')
            #self.get_wares_from_url()
            self.__get_wares_from_one_page(url)

    def __make_paggination_list(self):
        """Список ссылок пагиннаций."""
        try:
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
        except ValueError:
            print('__make_paggination_list lxml bad doc')
            #self.get_wares_from_url()
            self.__make_paggination_list()

    def get_wares_from_url(self):
        """Собирает в кучу функции загрузки/поиска падингов/парсинга."""
        try:
            self.proxy_obj = Proxy(self.link, 'ek.ua')
            # Создаем ссылку с ценами и получаем контрольное число.
            self.__make_pretty_url()
            # Создаем список ссылок паггинаций, в котором и идет создание
            # списка товаров
            self.__make_paggination_list()
            assert len(self.full_wares_list) == int(self.price_count), 'get_w_f_url:wares != control number'
        except AssertionError:
            return self.get_wares_from_url()

    def get_name(self):
        """
        Функция для получения имени товара, по ссылке указаной в файле.
        """
        try:
            page_doc = requests.get(self.link).text
            lxml_doc = lh.document_fromstring(page_doc)
            return lxml_doc.find_class('t2 no-mobile')[0].text_content()
        except ValueError:
            print('Parse_ek:get_name: error lxml bad doc')
            self.get_name(url)

class Parse_hotline():
    """
    Базовый класс для парсинга хотлайна, функции маленькие, компактные.
    Построен по принципу "от центра" - сходится в конструкторе.
    """
    def __init__(self, html):
        """
        конструктор наследуется от базового класса, только  изменяется
        базовый линк в конструкторе будут приниматься аргуметы, и обра-
        батываться последующими функциями
        """
        self.base_url = HOTLINE_BASE_URL
        self.html = html
        # На случай ошибки формирования lxml документа, делаю перехват.
        # Флагом bad_html, если get_doc прошло - то ставлю False.
        try:
            self.lxml_doc = self.get_doc()
            self.bad_html = False
            self.captcha = self.get_captcha()
            if self.captcha == []:
                self.name =  self.get_name()
                self.prices = self.get_prices()
                self.markets = self.get_markets()
                self.wares = self.get_wares()
                self.city = self.get_city()
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
        return lh.document_fromstring(self.html)

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
    def get_captcha(self):
        """
        Функция для улавливания капчи.
        """
        print("f-n cap done")
        return self.lxml_doc.find_class('g-recaptcha')
class Browser_manipulation():
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
        self.browser = webdriver.PhantomJS(
            desired_capabilities=self.options()[0],
            service_args = self.options()[1]
        )
        self.browser.set_page_load_timeout(50)
    def options(self):
        """
        Функция в которой задаются все опции для вебдрайвера:  отключение
        картинок, (!сейчас попробую отключить загрузку css),  подключение
        прокси, задание юзер агентов.
        """
        proxy_obj = Proxy(HOTLINE_BASE_URL, 'hotline.ua')
        user_agent = proxy_obj.user_agent['User-Agent']
        up = proxy_obj.final_proxy_access.split(':')
        browserName = choice(list(BROWSER_VERSION.keys()))
        version = choice(BROWSER_VERSION[browserName])
        self.serv_ar = []
        self.serv_ar.append('--load-images=no')
        self.serv_ar.append('--local-to-remote-url-access=yes')
        self.serv_ar.append('--proxy-type=https')
        self.serv_ar.append('--proxy={address}:{port}'.format(
            address=proxy_obj.final_proxy_ip, port=proxy_obj.final_proxy_port))
        self.serv_ar.append('--proxy-auth={user}:{passw}'.format(
            user=up[0], passw=up[1]))
        self.dcap = dict(DesiredCapabilities.PHANTOMJS)
        self.dcap["phantomjs.page.settings.userAgent"] = user_agent
        self.dcap["phantomjs.page.settings.browserName"] = 'Firefox'
        self.dcap["phantomjs.page.settings.browserName"] = browserName
        self.dcap["phantomjs.page.settings.version"] = version
        self.dcap["phantomjs.page.settings.cssSelectorsEnabled"] = "False"
        #self.dcap["phantomjs.page.settings.javascriptEnabled"] = "False"
        self.dcap["phantomjs.page.settings.platform"] = choice(PLATFORM)
        self.dcap["phantomjs.page.settings.takesScreenshot"] = "False"
        #self.dcap["phantomjs.page.settings.resourceTimeout"] = 1000
        return (self.dcap, self.serv_ar)
    def change_cookies(self, data):
        """
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
        try:
            self.browser.get(HOTLINE_BASE_URL)
            tmp_cookies = self.browser.get_cookies()
            self.change_cookies(tmp_cookies)
            self.kiev_cookies = tmp_cookies
            self.browser.delete_all_cookies()
            for i in self.kiev_cookies:
                for cookie in i:
                    # Тут удалил expiry - из за него был баг.
                    self.browser.add_cookie({k: i[k] for k in (
                        'name', 'value', 'domain',
                        'path',  'secure', #'expiry',
                        'httponly',
                        )
                    }
                )
        except SeleniumTimeout:
            print("Загрузка главной страници завершена по таймауту")
            self.browser.quit()
            self.__init__(self.link)


    def get_html(self):
        """
        Получаем html на выходе. В начале отратываем функцию перезагрузки
        куков, и собственно загружаем необходимую нам страницу.  Перехват
        ошибки - я не в курсе, иногда срабатывает. И в конце, обязательно
        закрываем вебдрайвер. Жрет много ресурсов, и зависает в памяти.
        """
        try:
            self.reset_browser_cookies()
            self.browser.get(self.link)
            print(self.browser.capabilities)
            data = self.browser.page_source
            self.browser.quit()
            if isinstance(data, str):
                return data
            else:
                print('Не получили хтмл с фантома.')
                return self.__init__(self.link)

        except (
            http.client.HTTPException,
            http.client.BadStatusLine,
            ConnectionRefusedError,
            SeleniumTimeout,
                ) as e:
            if e == SeleniumTimeout:
                print('selenium.common.exceptions.TimeoutException')
            print('Ошибка непосредственно при загрузке страницы.')
            self.browser.quit()
            self.__init__(self.link)

