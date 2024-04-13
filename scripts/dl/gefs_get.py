#! /usr/bin/python3

import glob, os, sys
import subprocess

model_date = str(sys.argv[1])
model_run = str(sys.argv[2])

os.chdir("../../data/gefs/")

if os.path.exists("dl.txt"):
    os.remove("dl.txt")

if os.path.exists("name.txt"):
    os.remove("name.txt")

f = open("dl.txt","w+")
ff = open("dl.txt","w+")

for sc in range(1,31):
    for ech in range(0,385,6):
        f.write("https://nomads.ncep.noaa.gov/cgi-bin/filter_gefs_atmos_0p50a.pl?dir=%2Fgefs."+model_date+"%2F"+model_run+"%2Fatmos%2Fpgrb2ap5&file=gep"+"{:03d}".format(sc)+".t"+model_run+"z.pgrb2a.0p50.f"+"{:03d}".format(ech)+"&lev_2_m_above_ground=on&lev_500_mb=on&lev_850_mb=on&lev_surface=on&var_APCP=on&var_HGT=on&var_TMP=on&subregion=&toplat=50&leftlon=5&rightlon=7&bottomlat=48"+"\n")
        ff.write(model_date+"_"+model_run+"_"+"{:03d}".format(sc)+"_"+"{:03d}".format(ech)+".grb2\n")

f.close()
ff.close()


with open('dl.txt') as my_file:
    orig_names = my_file.readlines()

with open('name.txt') as my_file:
    new_names = my_file.readlines()


os.system("cat dl.txt | xargs -n 1 -P 10 torsocks curl --connect-timeout 5 --max-time 10 --retry 10 --retry-delay 0 --retry-max-time 40 --retry-all-errors -O -J -L")


gonnaloop = True

while gonnaloop:
    gonnaloop = False
    if os.path.exists("dl2.txt"):
        os.remove("dl2.txt")
    f = open("dl2.txt","w+")
    for dlfile in orig_names:

        origname = dlfile.replace("\n","").replace("https://nomads.ncep.noaa.gov/cgi-bin/filter_gefs_atmos_0p50a.pl?dir=%2Fgefs."+model_date+"%2F"+model_run+"%2Fatmos%2Fpgrb2ap5&file=","").replace("&lev_2_m_above_ground=on&lev_500_mb=on&lev_850_mb=on&lev_surface=on&var_APCP=on&var_HGT=on&var_TMP=on&subregion=&toplat=50&leftlon=5&rightlon=7&bottomlat=48","")
        if os.path.isfile(origname) and os.stat(origname).st_size > 0 :
            try:
                output = subprocess.check_output( '/usr/bin/wgrib2 "'+origname+'"', shell=True)
            except:
                f.write("https://nomads.ncep.noaa.gov/cgi-bin/filter_gefs_atmos_0p50a.pl?dir=%2Fgefs."+model_date+"%2F"+model_run+"%2Fatmos%2Fpgrb2ap5&file="+origname+"&lev_2_m_above_ground=on&lev_500_mb=on&lev_850_mb=on&lev_surface=on&var_APCP=on&var_HGT=on&var_TMP=on&subregion=&toplat=50&leftlon=5&rightlon=7&bottomlat=48"+"\n")
                os.remove(origname)
                gonnaloop = True
        else:
            f.write("https://nomads.ncep.noaa.gov/cgi-bin/filter_gefs_atmos_0p50a.pl?dir=%2Fgefs."+model_date+"%2F"+model_run+"%2Fatmos%2Fpgrb2ap5&file="+origname+"&lev_2_m_above_ground=on&lev_500_mb=on&lev_850_mb=on&lev_surface=on&var_APCP=on&var_HGT=on&var_TMP=on&subregion=&toplat=50&leftlon=5&rightlon=7&bottomlat=48"+"\n")
            gonnaloop = True
            if os.path.isfile(origname):
                os.remove(origname)

    f.close()
    if gonnaloop:
        with open("dl2.txt") as file:
            for item in file:
                print(item)
                result = os.popen("torsocks curl "+'-w "%{filename_effective}"'+" --connect-timeout 5 --max-time 10 --retry 10 --retry-delay 0 --retry-max-time 40 --retry-all-errors -O -J -L "+'"'+item.replace("\n","")+'"').read()
                print(result)
                if result == "filter_gefs_atmos_0p50a.pl" and os.path.isfile(result):
                    if 'Data file is not present' in open(result).read():
                        linenumber = -1
                        with open("dl.txt") as myFile:
                            for num, line in enumerate(myFile, 1):
                                if item.replace("\n","") in line:
                                    linenumber = num -1

                        if linenumber > -1:
                            a_file = open("dl.txt", "r")
                            lines = a_file.readlines()
                            a_file.close()
                            del lines[linenumber]
                            new_file = open("dl.txt", "w+")
                            for line in lines:
                                new_file.write(line)
                            new_file.close()
                            a_file = open("name.txt", "r")
                            lines = a_file.readlines()
                            a_file.close()
                            del lines[linenumber]
                            new_file = open("name.txt", "w+")
                            for line in lines:
                                new_file.write(line)
                            new_file.close()

                            with open('dl.txt') as my_file:
                                orig_names = my_file.readlines()

                            with open('name.txt') as my_file:
                                new_names = my_file.readlines()
                    os.remove(result)


for i in range(0,len(orig_names)):
    origname = orig_names[i].replace("\n","").replace("https://nomads.ncep.noaa.gov/cgi-bin/filter_gefs_atmos_0p50a.pl?dir=%2Fgefs."+model_date+"%2F"+model_run+"%2Fatmos%2Fpgrb2ap5&file=","").replace("&lev_2_m_above_ground=on&lev_500_mb=on&lev_850_mb=on&lev_surface=on&var_APCP=on&var_HGT=on&var_TMP=on&subregion=&toplat=50&leftlon=5&rightlon=7&bottomlat=48","")
    newname = new_names[i].replace("\n","")
    if os.path.exists(origname):
        os.rename(origname, newname)

if os.path.exists("dl2.txt"):
    os.remove("dl2.txt")

if os.path.exists("dl.txt"):
    os.remove("dl.txt")

if os.path.exists("name.txt"):
    os.remove("name.txt")
