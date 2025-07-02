#! /usr/bin/python3

import os,glob
from datetime import date, timedelta
old = (date.today()- timedelta(days=2)).strftime("%Y%m%d")

os.chdir("../../data/gefs/")

sfiles = glob.glob('./*.grb2')
matching = [s for s in sfiles if old in s]

for anciens in matching:
    os.remove(anciens.replace("./",""))

sfiles = glob.glob('./filter*')
for junk in sfiles:
    os.remove(junk.replace("./",""))

os.chdir("../gem/")

sfiles = glob.glob('./*.grb2')
matching = [s for s in sfiles if old in s]

for anciens in matching:
    os.remove(anciens.replace("./",""))
sfiles = glob.glob('./filter*')
for junk in sfiles:
    os.remove(junk.replace("./",""))


os.chdir("../fnmoc/")

sfiles = glob.glob('./*.grb2')
matching = [s for s in sfiles if old in s]

for anciens in matching:
    os.remove(anciens.replace("./",""))
sfiles = glob.glob('./filter*')
for junk in sfiles:
    os.remove(junk.replace("./",""))


os.chdir("../ecmwf/")

sfiles = glob.glob('./*.grb2')
matching = [s for s in sfiles if old in s]

for anciens in matching:
    os.remove(anciens.replace("./",""))
sfiles = glob.glob('./filter*')
for junk in sfiles:
    os.remove(junk.replace("./",""))
    

if date.today().strftime("%d") == "10":
    os.chdir("../cfs")
    sfiles = glob.glob('./*.grb2')
    lastmonth = (date.today()- timedelta(days=16)).strftime("%Y%m")
    matching = [s for s in sfiles if lastmonth in s]
    for anciens in matching:
        os.remove(anciens.replace("./",""))
    sfiles = glob.glob('./filter*')
    for junk in sfiles:
        os.remove(junk.replace("./",""))
