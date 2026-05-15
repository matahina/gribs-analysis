#! /usr/bin/python3

import os,glob
from datetime import date, timedelta
current_a = (date.today()- timedelta(days=0)).strftime("%Y%m%d")
current_b = (date.today()- timedelta(days=1)).strftime("%Y%m%d")
subs = [current_a, current_b]

os.chdir("../../data/gefs/")

sfiles = glob.glob('./*.grb2')
to_keep = list(filter(lambda x: any(y in x for y in subs), sfiles))
matching = list(set(sfiles) - set(to_keep))

for anciens in matching:
    os.remove(anciens.replace("./",""))

sfiles = glob.glob('./filter*')
for junk in sfiles:
    os.remove(junk.replace("./",""))

os.chdir("../gem/")

sfiles = glob.glob('./*.grb2')
to_keep = list(filter(lambda x: any(y in x for y in subs), sfiles))
matching = list(set(sfiles) - set(to_keep))

for anciens in matching:
    os.remove(anciens.replace("./",""))
sfiles = glob.glob('./filter*')
for junk in sfiles:
    os.remove(junk.replace("./",""))


os.chdir("../fnmoc/")

sfiles = glob.glob('./*.grb2')
to_keep = list(filter(lambda x: any(y in x for y in subs), sfiles))
matching = list(set(sfiles) - set(to_keep))

for anciens in matching:
    os.remove(anciens.replace("./",""))
sfiles = glob.glob('./filter*')
for junk in sfiles:
    os.remove(junk.replace("./",""))


os.chdir("../ecmwf/")

sfiles = glob.glob('./*.grib2')
to_keep = list(filter(lambda x: any(y in x for y in subs), sfiles))
matching = list(set(sfiles) - set(to_keep))

for anciens in matching:
    os.remove(anciens.replace("./",""))
sfiles = glob.glob('./filter*')
for junk in sfiles:
    os.remove(junk.replace("./",""))
    

os.chdir("../cfs")
sfiles = glob.glob('./*.grb2')
merge_matching = []
for i in range(15):
    lastmonth = (date.today()- timedelta(days=i)).strftime("%Y%m%d")
    matching = [s for s in sfiles if lastmonth in s]
    merge_matching = merge_matching + matching
anciens = [x for x in sfiles if x not in merge_matching]
for elem in anciens:
    os.remove(elem.replace("./",""))
sfiles = glob.glob('./filter*')
for junk in sfiles:
    os.remove(junk.replace("./",""))
