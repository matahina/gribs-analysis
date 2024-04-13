#! /usr/bin/python3

import os,glob
from datetime import date, timedelta
old = (date.today()- timedelta(days=2)).strftime("%Y%m%d")

os.chdir("../../data/gefs/")

files = glob.glob('./*.grb2')
matching = [s for s in files if old in s]

for anciens in matching:
    os.remove(anciens.replace("./",""))
files = glob.glob('./filter*')
for junk in files:
    os.remove(junk.replace("./",""))

os.chdir("../gem/")

files = glob.glob('./*.grb2')
matching = [s for s in files if old in s]

for anciens in matching:
    os.remove(anciens.replace("./",""))
files = glob.glob('./filter*')
for junk in files:
    os.remove(junk.replace("./",""))


os.chdir("../fnmoc/")

files = glob.glob('./*.grb2')
matching = [s for s in files if old in s]

for anciens in matching:
    os.remove(anciens.replace("./",""))
files = glob.glob('./filter*')
for junk in files:
    os.remove(junk.replace("./",""))
    

if date.today().strftime("%d") == "10":
    os.chdir("../cfs")
    files = glob.glob('./*.grb2')
    lastmonth = (date.today()- timedelta(days=16)).strftime("%Y%m")
    matching = [s for s in files if lastmonth in s]
    for anciens in matching:
        os.remove(anciens.replace("./",""))
    files = glob.glob('./filter*')
    for junk in files:
        os.remove(junk.replace("./",""))