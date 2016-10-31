import json

from selenium.common.exceptions import TimeoutException as TE

from config.base_config import *
from config.user_agent import USER_AGENT
from parser import Proxy, MySQL
def print_dict(data):
    for i in data:
        print(i, ':', data[i])

def print_cookies(data):
    for i in data:
        print('')
        for j in i:
            print(j, ':',i[j] )

def change_cookies(data):
    for i in data:
        if i['name']=='city_id':
            i['value'] = '187'
        if i['name']=='region_mode':
            i['value'] = '1'
        if i['name']=='region':
            i['value'] = '1'
        if i['name']=='region_popup':
            i['value'] = '3'
    return data
def pr_cookies(data):
    for i in data:
        if i['name']=='city_id':
            print('')
            for j in i:
                print(j, ':',i[j] )
        if i['name']=='region_mode':
            print('')
            for j in i:
                print(j, ':',i[j] )
        if i['name']=='region':
            print('')
            for j in i:
                print(j, ':',i[j] )
        if i['name']=='region_popup':
            print('')
            for j in i:
                print(j, ':',i[j] )
def drive_f(driver, url):
    page_doc = driver.page_source
    lxml_doc = lh.document_fromstring(page_doc)
    name = lxml_doc.cssselect(name_class_name)[0].text_content()
    city = lxml_doc.find_class(city_class_name)[0].text_content()
    price = lxml_doc.find_class(price_selector)[0].text_content()

    print(city, name, price)

url = 'http://hotline.ua/av-3d-ochki/panasonic-ty-er3d4me/prices/'
url_404 = 'http://hotline.ua/'
url_ek = 'http://ek.ua/prices/apple-iphone-5s-16gb/'
city_class_name = 'link-dot text-16 no-adapt-768 js-city-name'
name_class_name = "h1"
price_selector = 'cell shop-title'
#with open(sys.argv[1], 'r') as f:
 #   link_list = [i.replace('\n', '') for i in f]
#proxy_obj = Proxy(url, 'hotline.ua')
serv_ar = []
serv_ar.append('--load-images=no')
#up = proxy_obj.proxy_access.split(':')
#serv_ar.append('--local-to-remote-url-access=yes')
#serv_ar.append('--proxy-type=https')
#serv_ar.append('--proxy={address}:{port}'.format(
#    address=proxy_obj.proxy_ip, port=proxy_obj.proxy_port))
#serv_ar.append('--proxy-auth={user}:{passw}'.format(
#    user=up[0], passw=up[1]))
serv_ar.append('--cookies-file=cookies.txt')

dcap = dict(DesiredCapabilities.PHANTOMJS)
#dcap["phantomjs.page.settings.userAgent"] = choice(USER_AGENT)
#dcap["phantomjs.page.settings.browserName"] = 'Firefox'
#dcap["phantomjs.page.settings.browserName"] = 'Firefox'
#dcap["phantomjs.page.settings.version"] = '48'
#dcap["phantomjs.page.settings.cssSelectorsEnabled"] = "False"
#dcap["phantomjs.page.settings.javascriptEnabled"] = "False"
#dcap["phantomjs.page.settings.platform"] = "MAC"
#dcap["phantomjs.page.settings.takesScreenshot"] = "False"


d1 = webdriver.PhantomJS(service_args=serv_ar, desired_capabilities=dcap)
if os.path.exists('cookies.txt'):
    print('cookies exist, time of creation is ')
    print('1st:', os.path.getctime('cookies.txt'))
else:
    print("file cookies doesn't exist")
try:
    d1.set_page_load_timeout(40)
    if (
        (not os.path.exists('cookies.txt')) or
        (time() - os.path.getctime('cookies.txt') > 85000)
    ):
        d1.get(url)
        print('changing cookies.....')
        c = d1.get_cookies()
        a = change_cookies(c)
        d1.delete_all_cookies()
        for cookie in a:
            d1.add_cookie({k: cookie[k] for k in ("name", "value", "domain",
                                            "path",  "secure", "httponly",) if k in cookie})
    d1.get(url)
    page_doc = d1.page_source
    lxml_doc = lh.document_fromstring(page_doc)
    drive_f(d1, url)
    d1.quit()
    print('2nd:', os.path.getctime('cookies.txt'))
except TE:
    print('boo2')
