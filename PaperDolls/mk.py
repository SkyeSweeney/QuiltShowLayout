#!/usr/bin/python3

import random

fp = open("list.csv", "w")

for i in range(200):

    w = random.randrange(1,8)
    h = random.randrange(1,10)

    s = "Q-%03d,XL,%d,%d,note\n" % (i, w, h)
    fp.write(s)
    
fp.close()    
