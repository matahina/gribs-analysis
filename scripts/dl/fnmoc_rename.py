#! /usr/bin/python3

import glob, os, sys
import subprocess
import time

os.chdir("../../data/fnmoc/")

with open('dl.txt') as my_file:
    orig_names = my_file.readlines()

with open('name.txt') as my_file:
    new_names = my_file.readlines()

gonnaloop = True


numlines = 100
timeout = 0
while gonnaloop:
    if numlines < 5 and timeout == 0:
        timeout = time.time() + 60*5
    if timeout > 0 and time.time() > timeout:
        break
    gonnaloop = False
    if os.path.exists("dl2.txt"):
        os.remove("dl2.txt")
    f = open("dl2.txt","w+")
    for dlfile in orig_names:
        origname = dlfile.replace("\n","").replace("https://nomads.ncep.noaa.gov/cgi-bin/filter_fens.pl?dir=%2Ffens."+sys.argv[1]+"%2F"+sys.argv[2]+"%2Fpgrb2ap5&file=","").replace("&lev_2_m_above_ground=on&lev_500_mb=on&lev_850_mb=on&lev_surface=on&var_APCP=on&var_HGT=on&var_TMP=on&subregion=&leftlon=5&rightlon=7&toplat=50&bottomlat=48","")
        # origname = dlfile.replace("\n","").replace("https://nomads.ncep.noaa.gov/pub/data/nccf/com/naefs/prod/fens."+sys.argv[1]+"/"+sys.argv[2]+"/pgrb2a/","")

        if os.path.isfile(origname) and os.stat(origname).st_size > 0 :
            try:
                output = subprocess.check_output( '/usr/bin/wgrib2 "'+origname+'"', shell=True)
            except:
                f.write("https://nomads.ncep.noaa.gov/cgi-bin/filter_fens.pl?dir=%2Ffens."+sys.argv[1]+"%2F"+sys.argv[2]+"%2Fpgrb2ap5&file="+origname+"&lev_2_m_above_ground=on&lev_500_mb=on&lev_850_mb=on&lev_surface=on&var_APCP=on&var_HGT=on&var_TMP=on&subregion=&leftlon=5&rightlon=7&toplat=50&bottomlat=48"+"\n")
                # f.write("https://nomads.ncep.noaa.gov/pub/data/nccf/com/naefs/prod/fens."+sys.argv[1]+"/"+sys.argv[2]+"/pgrb2a/"+origname+"\n")
                os.remove(origname)
                gonnaloop = True
        else:
            f.write("https://nomads.ncep.noaa.gov/cgi-bin/filter_fens.pl?dir=%2Ffens."+sys.argv[1]+"%2F"+sys.argv[2]+"%2Fpgrb2ap5&file="+origname+"&lev_2_m_above_ground=on&lev_500_mb=on&lev_850_mb=on&lev_surface=on&var_APCP=on&var_HGT=on&var_TMP=on&subregion=&leftlon=5&rightlon=7&toplat=50&bottomlat=48"+"\n")
            # f.write("https://nomads.ncep.noaa.gov/pub/data/nccf/com/naefs/prod/fens."+sys.argv[1]+"/"+sys.argv[2]+"/pgrb2a/"+origname+"\n")
            gonnaloop = True
            if os.path.isfile(origname):
                os.remove(origname)

    f.close()
    if gonnaloop:
        with open("dl2.txt") as file:
            numlines = 0
            for item in file:
                numlines = numlines + 1
                print(item)
                result = os.popen("torsocks curl "+'-w "%{filename_effective}"'+" --connect-timeout 5 --max-time 10 --retry 10 --retry-delay 0 --retry-max-time 40 --retry-all-errors -O -J -L "+'"'+item.replace("\n","")+'"').read()
                print(result)
                if result == "filter_fens.pl" and os.path.isfile(result):
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
    origname = orig_names[i].replace("\n","").replace("https://nomads.ncep.noaa.gov/cgi-bin/filter_fens.pl?dir=%2Ffens."+sys.argv[1]+"%2F"+sys.argv[2]+"%2Fpgrb2ap5&file=","").replace("&lev_2_m_above_ground=on&lev_500_mb=on&lev_850_mb=on&lev_surface=on&var_APCP=on&var_HGT=on&var_TMP=on&subregion=&leftlon=5&rightlon=7&toplat=50&bottomlat=48","")
    # origname = orig_names[i].replace("\n","").replace("https://nomads.ncep.noaa.gov/pub/data/nccf/com/naefs/prod/fens."+sys.argv[1]+"/"+sys.argv[2]+"/pgrb2a/","")
    newname = new_names[i].replace("\n","")
    #print(origname, " --> ", newname)
    if os.path.exists(origname):
        os.rename(origname, newname) 

if os.path.exists("dl2.txt"):
    os.remove("dl2.txt")
