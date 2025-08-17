#! /usr/bin/python3

import os,sys

model_date = str(sys.argv[1])
model_run = str(sys.argv[2])

files=["hgt","talt","tsolpp"]

os.chdir("../../data/ecmwf/")

for f in files:

    os.system("wgrib2 "+str(sys.argv[1])+str(sys.argv[2])+"data_"+f+".grib2"+" > list.txt")

    for i in range(1,51):
        lines = []
        with open("list.txt") as file:
            for line in file:
                if line.find("ENS=+"+str(i)+"\n") != -1:
                    lines.append(line[0:line.find(":")])
                # line.find(":")

        os.system("wgrib2 "+str(sys.argv[1])+str(sys.argv[2])+"data_"+f+".grib2"+" -match '^("+"|".join(lines)+"):' -grib "+str(sys.argv[1])+str(sys.argv[2])+"data_"+f+str(i)+".grib2")

    os.remove(str(sys.argv[1])+str(sys.argv[2])+"data_"+f+".grib2")

    os.remove("list.txt")
