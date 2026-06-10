#!/usr/bin/python3

import common

import configparser

import glob, os, sys
import subprocess
import time

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
model_name = "gem"

os.chdir("../../data/"+model_name+"/")



ech_range = list(list(range(0,193,3)) + list(range(198,385,6)))


for ech in ech_range:
    print(ech, "out of",ech_range[-1])
    thread_list = []
    for param in ["HGT_ISBL_0500", "TMP_ISBL_0850", "TMP_TGL_2m", "APCP_SFC_0"]:


        full_url = "https://dd.weather.gc.ca/"+model_date+"/WXO-DD/ensemble/geps/grib2/raw/"+model_run+"/"+"{:03d}".format(ech)+"/CMC_geps-raw_"+param+"_latlon0p5x0p5_"+model_date+model_run+"_P"+"{:03d}".format(ech)+"_allmbrs.grib2"

        file_name = param+"."+"{:03d}".format(ech)+"."+model_date+model_run+".grib2"


        thread = threading.Thread(target=common.get_ens, args=(full_url,file_name,model_date,model_name))
        thread_list.append(thread)

    for thread in thread_list:
        thread.start()
    for thread in thread_list:
        thread.join()
    time.sleep(0.1)

donneesrun = pd.DataFrame({'runs': [], 'dates': [], 'profile': [], 'geop': [], 'tempalt': [], 'tempsol': [], 'precs': []})

the_range = list(range(3, 193, 3)) + list(range(198, 385, 6))



first_try = True


for ech in the_range:
    print("ech: "+str(ech))
    grbfile = "HGT_ISBL_0500.%03d.%s%s.grib2" % (ech, model_date, model_run)
    extract_a = pd.DataFrame({'runs': [], 'dates': [], 'profile': [], 'geop': []})


    if Path(grbfile).is_file():
        if os.path.getsize(grbfile) > 0:
            try:
                ds_grib = xr.open_dataset(grbfile, engine="cfgrib", backend_kwargs={'filter_by_keys': {'dataType': 'pf'}}, decode_timedelta=False)
                for prof_name, location in profiles.items():
                    # print("prof_name: "+str(prof_name))
                    the_df_a = ds_grib.sel(longitude=location[1], latitude=location[0], method='nearest').to_dataframe()
                    for the_pert in range(1,21,1):
                        # print("sc: "+str(the_pert))
                        try:
                            df_a = the_df_a.iloc[the_df_a.index.get_level_values('number') == the_pert]
                            df_a["runs"] = str(df_a["time"].iloc[0]) + " sc%02d" % (the_pert)
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

    grbfile = "TMP_ISBL_0850.%03d.%s%s.grib2" % (ech, model_date, model_run)
    extract_b = pd.DataFrame({'runs': [], 'dates': [], 'profile': [], 'tempalt': []})

    if Path(grbfile).is_file():
        if os.path.getsize(grbfile) > 0:
            try:
                ds_grib = xr.open_dataset(grbfile, engine="cfgrib", backend_kwargs={'filter_by_keys': {'dataType': 'pf'}}, decode_timedelta=False)
                for prof_name, location in profiles.items():
                    # print("prof_name: "+str(prof_name))
                    the_df_b = ds_grib.sel(longitude=location[1], latitude=location[0], method='nearest').to_dataframe()
                    for the_pert in range(1,21,1):
                        # print("sc: "+str(the_pert))
                        try:
                            df_b = the_df_b.iloc[the_df_b.index.get_level_values('number') == the_pert]
                            df_b["runs"] = str(df_b["time"].iloc[0]) + " sc%02d" % (the_pert)
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


    grbfile = "TMP_TGL_2m.%03d.%s%s.grib2" % (ech, model_date, model_run)
    extract_c = pd.DataFrame({'runs': [], 'dates': [], 'profile': [], 'tempsol': []})

    if Path(grbfile).is_file():
        if os.path.getsize(grbfile) > 0:
            try:
                ds_grib = xr.open_dataset(grbfile, engine="cfgrib", backend_kwargs={'filter_by_keys': {'dataType': 'pf'}}, decode_timedelta=False)
                for prof_name, location in profiles.items():
                    # print("prof_name: "+str(prof_name))
                    the_df_c = ds_grib.sel(longitude=location[1], latitude=location[0], method='nearest').to_dataframe()
                    for the_pert in range(1,21,1):
                        # print("sc: "+str(the_pert))
                        try:
                            df_c = the_df_c.iloc[the_df_c.index.get_level_values('number') == the_pert]
                            df_c["runs"] = str(df_c["time"].iloc[0]) + " sc%02d" % (the_pert)
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


    grbfile = "APCP_SFC_0.%03d.%s%s.grib2" % (ech, model_date, model_run)
    extract_d = pd.DataFrame({'runs': [], 'dates': [], 'profile': [], 'precs': []})

    if Path(grbfile).is_file():
        if os.path.getsize(grbfile) > 0:
            try:
                ds_grib = xr.open_dataset(grbfile, engine="cfgrib", backend_kwargs={'filter_by_keys': {'dataType': 'pf'}}, decode_timedelta=False)
                for prof_name, location in profiles.items():
                    # print("prof_name: "+str(prof_name))
                    the_df_d = ds_grib.sel(longitude=location[1], latitude=location[0], method='nearest').to_dataframe()
                    for the_pert in range(1,21,1):
                        # print("sc: "+str(the_pert))
                        try:
                            df_d = the_df_d.iloc[the_df_d.index.get_level_values('number') == the_pert]
                            df_d["runs"] = str(df_d["time"].iloc[0]) + " sc%02d" % (the_pert)
                            df_d["dates"] = df_d["valid_time"]
                            df_d["profile"] = prof_name
                            df_d["precs"] = df_d["unknown"]
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
        predonneesjour = donneesrun
        first_try = False
    else:
        frames = [predonneesjour, donneesrun]
        try:
            new_donneesjour = pd.concat([df for df in frames if not df.empty], ignore_index=True)
            predonneesjour = new_donneesjour
        except:
            pass

first_try = True


for prof_name, location in profiles.items():
    print("prof_name: "+str(prof_name))
    for sc in range(1,21,1):
        subdata = predonneesjour.loc[predonneesjour["runs"].str.contains("%s:00:00 sc%02d" % (model_run, sc)) & predonneesjour["profile"].str.contains(prof_name)]
        subdata['precs'] = subdata['precs'].diff().fillna(subdata['precs'].iloc[0])
        if first_try:
            donneesjour = subdata
            first_try = False
        else:
            frames = [donneesjour, subdata]
            try:
                new_donneesjour = pd.concat([df for df in frames if not df.empty], ignore_index=True)
                donneesjour = new_donneesjour
            except:
                pass




hdr = False  if os.path.isfile("%s-%s.csv" % (model_name, model_date)) else True

donneesjour.to_csv("%s-%s.csv" % (model_name, model_date), index=False,header=hdr,mode='a')

liste = os.listdir(os.curdir)

for item in liste:
    if item.endswith(".idx") or item.endswith(".grib2"):
        os.remove(os.path.join(os.curdir, item))




