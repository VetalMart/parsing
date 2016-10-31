import sys
from multiprocessing import Pool

from selenium import webdriver
from lxml import html as lh
import requests

def space_cutter(n):
    """Функция удаления лишних пробелов с строки"""
    b = n.split()
    c = ''
    for i in b:
        c += i + ' '
    return c.strip()

url = 'http://hotline.ua/av-3d-ochki/panasonic-ty-er3d4me/prices/'

page_doc = requests.get(url).text
lxml_doc = lh.document_fromstring(page_doc)

class_select = 'title-24 p_b-5'
name_select = 'h1'

name = lxml_doc.cssselect(name_select)[0].text_content().replace('\n', ' ')
print(f(name))



