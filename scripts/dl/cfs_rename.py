#! /usr/bin/python3

import glob, os
import subprocess

os.chdir("../../data/cfs/")

with open('dl.txt') as my_file:
    orig_names = my_file.readlines()

gonnaloop = True

for dlfile in orig_names:
    os.system("wget --limit-rate=500k -c '"+dlfile.replace("\n","")+"'")

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
        os.system("cat dl2.txt | xargs -n 1 -P 1 wget --limit-rate=500k ")

if os.path.exists("dl2.txt"):
    os.remove("dl2.txt")
