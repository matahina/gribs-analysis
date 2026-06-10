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
model_name = "aigefs"

os.chdir("../../data/"+model_name+"/")


n_pert = 3

ech_range = list(range(0,385,6))
# ech_range = list(range(0,15,6))

for ech in ech_range:
    print(ech, "out of",ech_range[-1])
    thread_list = []
    for sc in range(1,n_pert):
        for level in ["pres","sfc"]:


            full_url = 'https://nomads.ncep.noaa.gov/pub/data/nccf/com/aigefs/prod/aigefs.'+model_date+'/'+model_run+'/mem'+"{:03d}".format(sc)+'/model/atmos/grib2/aigefs.t'+model_run+'z.'+level+'.f'+"{:03d}".format(ech)+".grib2"


            file_name = model_date+"_"+model_run+"_"+level+"_"+"{:03d}".format(sc)+"_"+"{:03d}".format(ech)+".grib2"


            thread = threading.Thread(target=common.get_ens, args=(full_url,file_name,model_date,model_name))
            thread_list.append(thread)

    for thread in thread_list:
        thread.start()
    for thread in thread_list:
        thread.join()
    time.sleep(0.1)


the_range = list(range(6,385,6))


donneesrun = pd.DataFrame({'runs': [], 'dates': [], 'profile': [], 'geop': [], 'tempalt': [], 'tempsol': [], 'precs': []})

first_try = True

for sc in range(1, 31, 1):
    print("sc: "+str(sc))
    for ech in the_range:
        donneesrun = pd.DataFrame({'runs': [], 'dates': [], 'profile': [], 'geop': [], 'tempalt': [], 'geop': [], 'tempalt': []})
        grbfile_a = "%s_%s_pres_%03d_%03d.grib2" % (
                            model_date,
                            model_run,
                            sc,
                            ech)
        grbfile_b = "%s_%s_sfc_%03d_%03d.grib2" % (
                            model_date,
                            model_run,
                            sc,
                            ech)


        if Path(grbfile_a).is_file() and Path(grbfile_b).is_file():
            if os.path.getsize(grbfile_a) > 0 and os.path.getsize(grbfile_b) > 0 :
                try:
                    ds_grib_a = xr.merge(cfgrib.open_datasets(grbfile_a), combine_attrs='override', compat='override', join='outer')
                    ds_grib_b = xr.merge(cfgrib.open_datasets(grbfile_b), combine_attrs='override', compat='override', join='outer')
                    for prof_name, location in profiles.items():
                        try:
                            var_hgt = float(ds_grib_a.gh.sel(longitude=location[1], latitude=location[0], isobaricInhPa=500, method='nearest').data) /10
                        except:
                            var_hgt = None
                        try:
                            var_talt = float(ds_grib_a.t.sel(longitude=location[1], latitude=location[0], isobaricInhPa=850, method='nearest').data) - 273.15
                        except:
                            var_talt = None
                        try:
                            var_tsol = float(ds_grib_b.t2m.sel(longitude=location[1], latitude=location[0], method='nearest').data) - 273.15
                        except:
                            var_tsol = None
                        try:
                            var_pp = float(ds_grib_b.tp.sel(longitude=location[1], latitude=location[0], method='nearest').data)
                        except:
                            var_pp = None
                        try:
                            var_date_a = pd.to_datetime(ds_grib_a.sel(longitude=location[1], latitude=location[0], method='nearest').coords['valid_time'].data, format='%Y-%m-%d %H:%M:%s')
                        except:
                            var_date_a = None
                        try:
                            var_date_b = pd.to_datetime(ds_grib_b.sel(longitude=location[1], latitude=location[0], method='nearest').coords['valid_time'].data, format='%Y-%m-%d %H:%M:%s')
                        except:
                            var_date_b = None
                        try:
                            var_run_a = str(pd.to_datetime(ds_grib_a.sel(longitude=location[1], latitude=location[0], method='nearest').coords['time'].data, format='%Y-%m-%d %H:%M:%s'))+ " sc%02d" % (sc)
                        except:
                            var_run_a = None
                        try:
                            var_run_b = str(pd.to_datetime(ds_grib_a.sel(longitude=location[1], latitude=location[0], method='nearest').coords['time'].data, format='%Y-%m-%d %H:%M:%s'))+ " sc%02d" % (sc)
                        except:
                            var_run_b = None

                        try:
                            newdata_a = pd.DataFrame({'runs': [var_run_a], 'dates': [var_date_a], 'profile': [prof_name], 'geop': [var_hgt], 'tempalt': [var_talt]})

                            newdata_b = pd.DataFrame({'runs': [var_run_b], 'dates': [var_date_b], 'profile': [prof_name], 'tempsol': [var_tsol], 'precs': [var_pp]})

                            newdata = pd.merge(newdata_a, newdata_b, on=["runs", "dates", "profile"], how = 'outer')
                        except:
                            newdata = pd.DataFrame({'runs': [], 'dates': [], 'profile': [], 'geop': [], 'tempalt': [], 'tempsol': [], 'precs': []})

                        frames = [donneesrun,newdata]
                        try:
                            new_donneesrun = pd.concat([df for df in frames if not df.empty], ignore_index=True)
                            donneesrun = new_donneesrun
                        except:
                            pass
                except:
                    pass
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

liste = os.listdir(os.curdir)

for item in liste:
    if item.endswith(".idx") or item.endswith(".grib2"):
        os.remove(os.path.join(os.curdir, item))





