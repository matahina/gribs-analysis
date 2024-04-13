#! /usr/bin/python3

import glob, os
import subprocess
import sys

model_date = str(sys.argv[1])
model_run = str(sys.argv[2])

os.chdir("../../data/cfs/")

if os.path.exists("dl.txt"):
    os.remove("dl.txt")

f = open("dl.txt","w+")

for param in ["z500", "t850", "prate", "tmp2m"]:
    for sc in range(1,5):
        f.write("https://nomads.ncep.noaa.gov/pub/data/nccf/com/cfs/prod/cfs."+model_date+"/"+model_run+"/time_grib_"+"{:02d}".format(sc)+"/"+param+"."+"{:02d}".format(sc)+"."+model_date+""+model_run+".daily.grb2"+"\n")
f.close()


with open('dl.txt') as my_file:
    orig_names = my_file.readlines()

os.system("cat dl.txt | xargs -n 1 -P 2 torsocks wget ")


gonnaloop = True

for dlfile in orig_names:
    os.system("wget --limit-rate=2500k -c '"+dlfile.replace("\n","")+"'")

while gonnaloop:
    gonnaloop = False
    if os.path.exists("dl2.txt"):
        os.remove("dl2.txt")
    f = open("dl2.txt","w+")
    for dlfile in orig_names:
        origname = dlfile[85:].replace("\n","")

        if os.path.isfile(origname) and os.stat(origname).st_size > 0 :
            try:
                output = subprocess.check_output( '/usr/bin/wgrib2 "'+origname+'"', shell=True)
            except:
                f.write(dlfile+"\n")
                os.remove(origname)
                gonnaloop = True
        else:
            f.write(dlfile+"\n")
            gonnaloop = True
    f.close()
    if gonnaloop:
        os.system("cat dl2.txt | xargs -n 1 -P 1 wget --limit-rate=2500k ")

if os.path.exists("dl2.txt"):
    os.remove("dl2.txt")

if os.path.exists("dl.txt"):
    os.remove("dl.txt")
