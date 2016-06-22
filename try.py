from grab import Grab
import logging
import sys

def correct(a):
    c = []
    for i in a:
        b = i.split()
        if b[1].isnumeric():
            b[0] = b[0]+b[1]
            c.append('{0} {1}'.format(b[0], b[2]))
        else:
            c.append('{0} {1}'.format(b[0], b[1]))
    return c

g = Grab()
g.go(sys.argv[1])

file_name = g.doc.select("//h1").text()
item_name = g.doc.select("//h3")#td[@class='where-buy-description']")
market_name = g.doc.select("//a[@class='it-shop']")
price = g.doc.select("//td[@class='where-buy-price']")

t = lambda x: x.text()

f1 = list(map(t, item_name))
m1 = list(map(t, market_name))
p1 = correct(list(map(t, price)))

#a = dict(zip(m1, p1))
a = [(i, j) for i in m1 for j in p1]
b = dict(zip(f1, a))

print(b)

f = open(file_name+'.txt', 'w')
#f.write('{0}: {1};'.format())
i = 1
for k, v in b.items():
    f.write('{0}. {1}: {2}\n'.format(i, k, v))
    i += 1
f.close()
