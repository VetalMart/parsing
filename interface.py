from parser import Parse_ek, MySQL, Parse_hotline, Browser_manipulation, Proxy
from config.local_config import *
from config.base_config import *

def check_link(link):
    """
    Проверка ссилок на валидность. Какой у нее респонс, и сущесвтует ли.
    """
    try:
        r = requests.get(link).status_code
        if r == 200:
            return link
        else:
            return None
    except:
            return None

if argv[1]=='ek.ua':
    def ek_to_mysql(tuple_data: 0):
        """
        для работы с сайтом ek.ua
        функция предназначена для двух целей:
            1. Сохраняет список ссылок на товары в базу MySQL
            2. Возращает ?герератор списка ссылок для парсинга товаров
        """
        ek_to_mysql.__annotations__['tuple_data'] += 1
        link = check_link(tuple_data[3].replace('\n', ''))
        if link != None:
            prs_obj_ek = Parse_ek(link)
            prs_obj_ek.get_wares_from_url()
            print(prs_obj_ek.full_wares_list)
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

            MySQL().post_wares_to_EuropHotlineLinks_prices_list(dict_data)
            MySQL().update_date_wares(tuple_data[2])
        else:
            pass

elif argv[1]=='hotline.ua':
    def hotline_to_mysql(tuple_data: 0):
        """
        для работы с сайтом hotline.ua
        функция предназначена для двух целей:
            1. Сохраняет список ссылок на товары в базу MySQL
            2. Возращает списoк ссылок для парсинга товаров
        """
        # Это для получения номерации ссылок.
        hotline_to_mysql.__annotations__['tuple_data'] += 1
        link = check_link(tuple_data[3].replace('\n', '') + 'prices/')
        if link != None:
            r = Browser_manipulation(link)
            html_doc = r.get_html()
            prs_obj_hot = Parse_hotline(html_doc)
            # Этот цикл, срабатывает в случае выдачи плохого html фантомом.
            while prs_obj_hot.bad_html:
                r = Browser_manipulation(link)
                html_doc = r.get_html()
                prs_obj_hot = Parse_hotline(html_doc)
            # Этa управляющая конструкция отрабатывает ситуацию, если мы
            # попались на капчу.
            if prs_obj_hot.captcha == []:
                print("no cap", prs_obj_hot.captcha)
                dict_data = {tuple_data: prs_obj_hot.wares}

                a = [i[2] for i in prs_obj_hot.wares]
                b = set()
                for i in a:
                    b.add(i)

                print(
                        hotline_to_mysql.__annotations__['tuple_data'],
                        'м', prs_obj_hot.city,
                        link,
                        'уник.магаз', len(b),
                )

                MySQL().post_wares_to_EuropHotlineLinks_prices_list(dict_data)
                MySQL().update_date_wares(tuple_data[2])
            else:
                print("Поздравляю, вы попались на капчу.")
else:
    print("Вы не ввели хост, в аргументе: holine или ek.ua")


def main():
    try:
        # Приводит в порядок кодировку базы данных.
        MySQL().work_cursor('SET CHARACTER SET utf8;')

        i = input("Обновить базу прокси? (y/n) \n>")
        if i == 'y':
            Proxy(EK_BASE_URL, EK_BASE_URL).reset_info(PROXY_LIST)

        tuple_list = MySQL().get_id_name_link()
        """
        if argv[1] == 'ek.ua':
            with Pool(AMOUNT_THREADS) as pool:
                pool.map(ek_to_mysql, tuple_list)
        elif argv[1] == 'hotline.ua':
            with Pool(AMOUNT_PROCESS) as pool:
                pool.map(hotline_to_mysql, tuple_list)
        else:
            pass
        """
        for tuple_ in tuple_list:
            hotline_to_mysql(tuple_)
    except IndexError:
        print("Либо капча, либо все ссилки актуальны")

if __name__ == '__main__':
    main()

