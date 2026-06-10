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
model_name = "gefs"

os.chdir("../../data/"+model_name+"/")


n_pert = 31
ech_range = list(range(0,193,3)) + list(range(198,385,6))



for ech in ech_range:
    print(ech, "out of",ech_range[-1])
    thread_list = []
    for sc in range(1,n_pert):





        full_url = 'https://nomads.ncep.noaa.gov/pub/data/nccf/com/gens/prod/gefs.'+model_date+'/'+model_run+'/atmos/pgrb2ap5/gep'+"{:02d}".format(sc)+'.t'+model_run+'z.pgrb2a.0p50.f'+"{:03d}".format(ech)




        file_name = model_date+"_"+model_run+"_"+"{:03d}".format(sc)+"_"+"{:03d}".format(ech)+".grb2"


        thread = threading.Thread(target=common.get_ens, args=(full_url,file_name,model_date,model_name))
        thread_list.append(thread)

    for thread in thread_list:
        thread.start()
    for thread in thread_list:
        thread.join()
    time.sleep(0.1)




the_range = list(range(3, 193, 3)) + list(range(198, 385, 6))


donneesrun = pd.DataFrame({'runs': [], 'dates': [], 'profile': [], 'geop': [], 'tempalt': [], 'tempsol': [], 'precs': []})

first_try = True

for sc in range(1, 31, 1):
    print("sc: "+str(sc))
    for ech in the_range:
        donneesrun = pd.DataFrame({'runs': [], 'dates': [], 'profile': [], 'geop': [], 'tempalt': [], 'tempsol': [], 'precs': []})
        grbfile = "%s_%s_%03d_%03d.grb2" % (
                            model_date,
                            model_run,
                            sc,
                            ech)

        if Path(grbfile).is_file():
            if os.path.getsize(grbfile) > 0:
                try:
                    ds_grib = xr.merge(cfgrib.open_datasets(grbfile), combine_attrs='override', compat='override', join='outer')
                    for prof_name, location in profiles.items():
                        try:
                            var_hgt = float(ds_grib.gh.sel(longitude=location[1], latitude=location[0], isobaricInhPa=500, method='nearest').data) /10
                        except:
                            var_hgt = None
                        try:
                            var_talt = float(ds_grib.t.sel(longitude=location[1], latitude=location[0], isobaricInhPa=850, method='nearest').data) - 273.15
                        except:
                            var_talt = None
                        try:
                            var_tsol = float(ds_grib.t2m.sel(longitude=location[1], latitude=location[0], method='nearest').data) - 273.15
                        except:
                            var_tsol = None
                        try:
                            var_pp = float(ds_grib.tp.sel(longitude=location[1], latitude=location[0], method='nearest').data)
                        except:
                            var_pp = None
                        try:
                            var_date = pd.to_datetime(ds_grib.sel(longitude=location[1], latitude=location[0], method='nearest').coords['valid_time'].data, format='%Y-%m-%d %H:%M:%s')
                        except:
                            var_date = None
                        try:
                            var_run = str(pd.to_datetime(ds_grib.sel(longitude=location[1], latitude=location[0], method='nearest').coords['time'].data, format='%Y-%m-%d %H:%M:%s'))+ " sc%02d" % (sc)
                        except:
                            var_run = None

                        try:
                            newdata = pd.DataFrame({'runs': [var_run], 'dates': [var_date], 'profile': [prof_name], 'geop': [var_hgt], 'tempalt': [var_talt], 'tempsol': [var_tsol], 'precs': [var_pp]})
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
    if item.endswith(".idx") or item.endswith(".grb2"):
        os.remove(os.path.join(os.curdir, item))



