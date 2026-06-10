#!/usr/bin/python3

import common

import configparser

import glob, os, sys
import subprocess
import time


from datetime import date, timedelta

import urllib.request
import urllib.parse

import http

import socket

socket.setdefaulttimeout(60*5)

import requests

import threading


import xarray as xr
import math
import pandas as pd
from pathlib import Path
import cfgrib
pd.options.mode.chained_assignment = None # comment to get all warnings

xr.set_options(use_new_combine_kwarg_defaults=True)



config = configparser.ConfigParser()
config.read('../../magic_config.ini')

profiles = {}

for i in config.sections():
    if "Profile" in i:
        if config[i]['use_it'] == "yes":
            if float(config[i]['lon']) < 0:
                profiles[i] = [config[i]['lat'], 360 + float(config[i]['lon'])]
            else:
                profiles[i] = [config[i]['lat'], config[i]['lon']]


model_date = str(sys.argv[1])
model_run = str(sys.argv[2])
model_name = "cfs"

os.chdir("../../data/"+model_name+"/")


n_pert = 21
sc_range = list(range(1,5))

for sc in sc_range:
    print(sc, "out of",sc_range[-1])
    thread_list = []
    for param in ["z500", "t850", "prate", "tmp2m"]:


        full_url = "https://nomads.ncep.noaa.gov/pub/data/nccf/com/cfs/prod/cfs."+model_date+"/"+model_run+"/time_grib_"+"{:02d}".format(sc)+"/"+param+"."+"{:02d}".format(sc)+"."+model_date+""+model_run+".daily.grb2"

        file_name = param+"."+"{:02d}".format(sc)+"."+model_date+""+model_run+".daily.grb2"


        thread = threading.Thread(target=common.get_ens, args=(full_url,file_name,model_date,model_name))
        thread_list.append(thread)

    for thread in thread_list:
        thread.start()
    for thread in thread_list:
        thread.join()
    time.sleep(0.1)




first_try = True


for sc in range(1, 5, 1):
    print("sc: "+str(sc))
    filename = ".%02d.%s%s.daily.grb2" % (sc, model_date, model_run)

    grbfile = "z500%s" % filename
    extract_a = pd.DataFrame({'runs': [], 'dates': [], 'profile': [], 'geop': []})

    if Path(grbfile).is_file():
        if os.path.getsize(grbfile) > 0:
            try:
                ds_grib = xr.open_dataset(grbfile, engine="cfgrib", decode_timedelta=False)
                for prof_name, location in profiles.items():
                    print("prof_name: "+str(prof_name))
                    try:
                        df_a = ds_grib.gh.sel(longitude=location[1], latitude=location[0], method='nearest').to_dataframe()
                        df_a["runs"] = str(df_a["time"].iloc[0]) + " sc%02d" % (sc)
                        df_a["dates"] = df_a["valid_time"]
                        df_a["profile"] = prof_name
                        df_a["geop"] = df_a["gh"] / 10
                        extract = df_a[["runs","dates","profile","geop"]]
                    except:
                        extract = pd.DataFrame({'runs': [], 'dates': [], 'profile': [], 'geop': []})

                    frames = [extract,extract_a]
                    try:
                        new_extract_a = pd.concat([df for df in frames if not df.empty], ignore_index=True)
                        extract_a = new_extract_a
                    except:
                        pass
            except:
                pass

    print (extract_a)

    grbfile = "t850%s" % filename
    extract_b = pd.DataFrame({'runs': [], 'dates': [], 'profile': [], 'tempalt': []})

    if Path(grbfile).is_file():
        if os.path.getsize(grbfile) > 0:
            try:
                ds_grib = xr.open_dataset(grbfile, engine="cfgrib", decode_timedelta=False)
                for prof_name, location in profiles.items():
                    print("prof_name: "+str(prof_name))
                    try:
                        df_b = ds_grib.t.sel(longitude=location[1], latitude=location[0], method='nearest').to_dataframe()
                        df_b["runs"] = str(df_b["time"].iloc[0]) + " sc%02d" % (sc)
                        df_b["dates"] = df_b["valid_time"]
                        df_b["profile"] = prof_name
                        df_b["tempalt"] = df_b["t"] -273.15
                        extract = df_b[["runs","dates","profile","tempalt"]]
                    except:
                        extract = pd.DataFrame({'runs': [], 'dates': [], 'profile': [], 'tempalt': []})

                    frames = [extract,extract_b]
                    try:
                        new_extract_b = pd.concat([df for df in frames if not df.empty], ignore_index=True)
                        extract_b = new_extract_b
                    except:
                        pass
            except:
                pass


    grbfile = "tmp2m%s" % filename
    extract_c = pd.DataFrame({'runs': [], 'dates': [], 'profile': [], 'tempsol': []})

    if Path(grbfile).is_file():
        if os.path.getsize(grbfile) > 0:
            try:
                ds_grib = xr.open_dataset(grbfile, engine="cfgrib", decode_timedelta=False)
                for prof_name, location in profiles.items():
                    print("prof_name: "+str(prof_name))
                    try:
                        df_c = ds_grib.t2m.sel(longitude=location[1], latitude=location[0], method='nearest').to_dataframe()
                        df_c["runs"] = str(df_c["time"].iloc[0]) + " sc%02d" % (sc)
                        df_c["dates"] = df_c["valid_time"]
                        df_c["profile"] = prof_name
                        df_c["tempsol"] = df_c["t2m"] -273.15
                        extract = df_c[["runs","dates","profile","tempsol"]]
                    except:
                        extract = pd.DataFrame({'runs': [], 'dates': [], 'profile': [], 'tempsol': []})

                    frames = [extract,extract_c]
                    try:
                        new_extract_c = pd.concat([df for df in frames if not df.empty], ignore_index=True)
                        extract_c = new_extract_c
                    except:
                        pass
            except:
                pass


    grbfile = "prate%s" % filename
    extract_d = pd.DataFrame({'runs': [], 'dates': [], 'profile': [], 'precs': []})

    if Path(grbfile).is_file():
        if os.path.getsize(grbfile) > 0:
            try:
                ds_grib = xr.open_dataset(grbfile, engine="cfgrib", decode_timedelta=False)
                for prof_name, location in profiles.items():
                    print("prof_name: "+str(prof_name))
                    try:
                        df_d = ds_grib.prate.sel(longitude=location[1], latitude=location[0], method='nearest').to_dataframe()
                        df_d["runs"] = str(df_d["time"].iloc[0]) + " sc%02d" % (sc)
                        df_d["dates"] = df_d["valid_time"]
                        df_d["profile"] = prof_name
                        df_d["precs"] = df_d["prate"] * 3600 * 6
                        extract = df_d[["runs","dates","profile","precs"]]
                    except:
                        extract = pd.DataFrame({'runs': [], 'dates': [], 'profile': [], 'precs': []})

                    frames = [extract,extract_d]
                    try:
                        new_extract_d = pd.concat([df for df in frames if not df.empty], ignore_index=True)
                        extract_d = new_extract_d
                    except:
                        pass
            except:
                pass


    donneesrun_a = pd.merge(extract_a, extract_b, on=["runs", "dates", "profile"], how = 'outer')
    donneesrun_b = pd.merge(extract_c, extract_d, on=["runs", "dates", "profile"], how = 'outer')

    donneesrun = pd.merge(donneesrun_a, donneesrun_b, on=["runs", "dates", "profile"], how = 'outer')

    if first_try:
        donneesjour = donneesrun
        first_try = False
    else:
        frames = [donneesjour, donneesrun]
        try:
            new_donneesjour = pd.concat([df for df in frames if not df.empty], ignore_index=True)
            donneesjour = new_donneesjour
        except:
            pass




hdr = False  if os.path.isfile("%s-%s.csv" % (model_name, model_date)) else True

donneesjour.to_csv("%s-%s.csv" % (model_name, model_date), index=False,header=hdr,mode='a')


sfiles = glob.glob('./*.grb2')
merge_matching = []
for i in range(6):
    lastmonth = (date.today()- timedelta(days=i)).strftime("%Y%m%d")
    matching = [s for s in sfiles if lastmonth in s]
    merge_matching = merge_matching + matching
anciens = [x for x in sfiles if x not in merge_matching]
for elem in anciens:
    os.remove(elem.replace("./",""))
sfiles = glob.glob('./filter*')
for junk in sfiles:
    os.remove(junk.replace("./",""))
