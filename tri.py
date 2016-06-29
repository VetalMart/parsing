from grab import Grab
import sys

def correct(a:'str_with_redundant_inf')->'price of item':
    c = []
    for i in a:
        b = i.split()
        if b[1].isnumeric():
            b[0] = b[0]+b[1]
            c.append('{0} {1}'.format(b[0], b[2]))
        else:
            c.append('{0} {1}'.format(b[0], b[1]))
    return c


def parse_page(a:'links')->'{"items":(market, price) from one page}':
    #print(a)
    grab_obj = Grab()
    grab_obj.go(a)

    t = lambda x: x.text() # convert atr.grab.obj to text
    # key name
    item_name = grab_obj.doc.select("//h3")
    # value
    market_name = grab_obj.doc.select("//a[@class='it-shop']")
    price = grab_obj.doc.select("//td[@class='where-buy-price']")

    #f1 = list(map(t, item_name))            # list of names
    m1 = list(map(t, market_name))          # list of markets
    p1 = correct(list(map(t, price)))       # list of prices
    b = [[m1[i], p1[i]] for i in range(len(m1))]    # tuple (market, price)
    #b = list(zip(m1, p1))                    # dict [[market, price], [] ]
    return b

# сюда заходит одна готовая ссылка с товаром,
# выходить полный словарь по этому товару


def parse_items(w):
    total_list = list()
    m_list = []
    full_dict = {}

    g = Grab()
    g.go(w)

    # key name
    item_name = g.doc.select("//h3")
    # вытаскивает магазины и цены со всех вкладок на странице товаров
    list_pages = [w]
    for i in (g.doc.select("//div[@class='ib page-num']//a[@class='ib']")):
        list_pages.append('http://ek.ua'+i.attr('href'))

    #создает полный словарь по одному данному товару
    #инфа тут со всех вкладок по нему
    for i in list_pages:
        m_list = parse_page(i)
        total_list.extend(m_list)
        m_list.clear()

    def uniform_markets(l:'whole list of markets')->'list with no uniform market':
        a = []
        c = set()
        d = {}
        for i in l:
            if i not in a:
                a.append(i)
        a.sort()
        for i in a:
            b = i[0]
            c.add(i[1])
            for j in a:
                if j[0] == b:
                    c.add(j[1])
            d[i[0]] = c
            c  = set()
        return d


    full_dict = uniform_markets(total_list)

    return full_dict


#l = uniform_markets(parse_items(create_list_of_links(sys.argv[1])))

#file_name = g.doc.select("//h1").text()
f1 = open('base.txt', 'w')
f2 = open(sys.argv[1], 'r').read().split()
#f.write('{0}: {1};'.format())

for j in f2:
    i = 1
    g = Grab()
    g.go(j)
    item_name = g.doc.select('//h3')
    f1.write('  {0}. \n'.format(item_name.text()))
    #uniform_markets(parse_items(create_list_of_links(sys.argv[1])))
    for k, v in parse_items(j).items():
        f1.write('{0}. {1}: {2}\n'.format(i, k, v))
        i += 1
f1.close()




