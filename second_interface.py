from config.base_config import *
from config.local_config import *
from second_parser import Proxy, LinksGoods, HotConvertor, work_cursor, Parse_hotline, Parse_ek, reset_proxy_table

if argv[1]=='ek.ua':
    def ek_to_mysql(tuple_data: 0):
        """
        для работы с сайтом ek.ua
        функция предназначена для двух целей:
            1. Сохраняет список ссылок на товары в базу MySQL
            2. Возращает ?герератор списка ссылок для парсинга товаров
        """
        ek_to_mysql.__annotations__['tuple_data'] += 1
        link = tuple_data[3].replace('\n', '')
        # Здесь идет проверка флагов кострукторов, если например произошла
        # ошибка где то, то объет пересоздается. Так происходит перегрузка
        # взаимосвязанных конструкторов.
        constractor_flag = True
        while constractor_flag:
            prs_obj_ek = Parse_ek(link)
            prs_obj_ek.get_wares_from_url()
            constractor_flag = prs_obj_ek.reset_constructor
            # Маленька пауза, для того, что бы дать обновиться базе прокси,
            # в конструкторе HotConvertor.
            if prs_obj_ek.error_becouse_proxy_constructor:
                print("Закончились прокси нормальные адреса, обновляем(10сек.)...")
                reset_proxy_table()
                #sleep(10)
        if prs_obj_ek.no_markets_error == False:
            # Получаем словарь где данные с таблици с линками - ключ;
            # а список товаров значение.
            dict_data = {tuple_data: prs_obj_ek.full_wares_list}
            a = [i[2] for i in prs_obj_ek.full_wares_list]
            b = set()
            for i in a:
                b.add(i)
            print(
                    ek_to_mysql.__annotations__['tuple_data'],
                    'м', prs_obj_ek.city,
                    'кц', prs_obj_ek.price_count,
                    'кт', len(prs_obj_ek.full_wares_list),
                    link,
                    'уник.магаз', len(b),
                )

            LinksGoods().post_wares_to_EuropHotlineLinks_prices_list(dict_data)
            LinksGoods().update_date_wares(tuple_data[2])
        else:
            print("Выключаем ссылку {0}".format(link))
            work_cursor("""update EuropHotlineLinks set not_found = 1
                        where id="{0}";""".format(tuple_data[0]))
elif argv[1]=='hotline.ua':
    def hotline_to_mysql(one_tuple: 0):
        """
        для работы с сайтом hotline.ua
        функция предназначена для двух целей:
            1. Сохраняет список ссылок на товары в базу MySQL
            2. Возращает списoк ссылок для парсинга товаров
        """
        # Это для получения номерации ссылок.
        hotline_to_mysql.__annotations__['one_tuple'] += 1
        link = one_tuple[3].replace('\n', '') + 'prices/'
        # Здесь идет проверка флагов кострукторов, если например произошла
        # ошибка где то, то объет пересоздается. Так происходит перегрузка
        # взаимосвязанных конструкторов.
        constractor_flag = True
        while constractor_flag:
            r = HotConvertor(link)
            html_doc = r.get_html()
            constractor_flag = r.reset_constructor
            # Маленька пауза, для того, что бы дать обновиться базе прокси,
            # в конструкторе HotConvertor.
            if r.error_becouse_proxy_constructor:
                print("Закончились прокси нормальные адреса, обновляем(10сек.)...")
                reset_proxy_table()
                sleep(10)

        prox = r.proxy_obj.final_proxy
        ug = r.user_agent
        br = r.browserName
        bv = r.version
        pl = r.platform

        prs_obj_hot = Parse_hotline(html_doc)
        if (prs_obj_hot.captcha_hard == []) and (prs_obj_hot.captcha_light == []):
            dict_data = {one_tuple: prs_obj_hot.wares}

            a = [i[2] for i in prs_obj_hot.wares]
            b = set()
            for i in a:
                b.add(i)

            print(
                    hotline_to_mysql.__annotations__['one_tuple'],
                    'м', prs_obj_hot.city,
                    link,
                    'уник.магаз', len(b),
            )

            LinksGoods().post_wares_to_EuropHotlineLinks_prices_list(dict_data)
            LinksGoods().update_date_wares(one_tuple[2])
        else:
            print("капчa. {0} {1} {2} {3} {4}".format(link, prox, br, bv, pl))
            return hotline_to_mysql(one_tuple)
else:
    print("Вы не ввели хост, в аргументе: holine или ek.ua")

def main():
    # Приводит в порядок кодировку базы данных.
    work_cursor('SET CHARACTER SET utf8;')

    i = input("Обновить базу прокси? (y/n) \n>")
    if i == 'y':
        reset_proxy_table()

    tuple_list = LinksGoods().get_id_name_link()[:2]
    if tuple_list != tuple():
        if argv[1] == 'ek.ua':
            with Pool(AMOUNT_THREADS) as pool:
                pool.map(ek_to_mysql, tuple_list)
        elif argv[1] == 'hotline.ua':
            """
            for one_tuple in tuple_list:
                hotline_to_mysql(one_tuple)
            """
            with Pool(AMOUNT_PROCESS) as pool:
                pool.map(hotline_to_mysql, tuple_list)
        else:
            pass
    else:
        print("Все ссылки актуальны.")

if __name__ == '__main__':
    main()

