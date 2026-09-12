#! /usr/bin/python3

import os,glob
from datetime import date, timedelta


os.chdir("../../data/cfs")
sfiles = glob.glob('./*.grb2')
sfiles = glob.glob('./*.idx')
merge_matching = []
for i in range(10):
    lastmonth = (date.today()- timedelta(days=i)).strftime("%Y%m%d")
    matching = [s for s in sfiles if lastmonth in s]
    merge_matching = merge_matching + matching
anciens = [x for x in sfiles if x not in merge_matching]
for elem in anciens:
    os.remove(elem.replace("./",""))
sfiles = glob.glob('./filter*')
for junk in sfiles:
    os.remove(junk.replace("./",""))
