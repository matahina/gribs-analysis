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

from threading import Thread

class CustomThread(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self, *args):
        Thread.join(self, *args)
        return self._return



import xarray as xr
import math
import pandas as pd
from pathlib import Path
import cfgrib
pd.options.mode.chained_assignment = None # comment to get all warnings

try:
    xr.set_options(use_new_combine_kwarg_defaults=True)
except:
    pass

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

donneesrun = pd.DataFrame({'runs': [], 'dates': [], 'profile': [], 'geop': [], 'tempalt': [], 'tempsol': [], 'precs': []})

first_try = True

n_pert = 31
ech_range = list(range(6,385,6))

for ech in ech_range:
    print(ech, "out of",ech_range[-1])
    thread_list = []
    for sc in range(1,n_pert):
        for level in ["pres","sfc"]:


            full_url = 'https://nomads.ncep.noaa.gov/pub/data/nccf/com/aigefs/prod/aigefs.'+model_date+'/'+model_run+'/mem'+"{:03d}".format(sc)+'/model/atmos/grib2/aigefs.t'+model_run+'z.'+level+'.f'+"{:03d}".format(ech)+".grib2"


            file_name = model_date+"_"+model_run+"_"+level+"_"+"{:03d}".format(sc)+"_"+"{:03d}".format(ech)+".grib2"


            thread = Thread(target=common.get_ens, args=(full_url,file_name,model_date,model_name))
            thread_list.append(thread)

    for thread in thread_list:
        thread.start()
    for thread in thread_list:
        thread.join()
    time.sleep(0.1)

    dataliste = [[]] * 30


    thread_list = []

    for sc in range(1, n_pert):

        thread = CustomThread(target=common.data_ens_ai, args=(sc,ech,model_date,model_name,model_run,profiles))
        thread_list.append(thread)

    for thread in thread_list:
        thread.start()
    i=0
    for thread in thread_list:
        dataliste[i]=thread.join()
        print(dataliste[i])
        i+=1
    time.sleep(0.1)


    if first_try:
        frames = dataliste
        first_try = False
    else:
        frames = [donneesjour] + dataliste

    try:
        new_donneesjour = pd.concat([df for df in frames if not df.empty], ignore_index=True)
        donneesjour = new_donneesjour
    except:
        pass

    print(donneesjour)

    liste = os.listdir(os.curdir)

    for item in liste:
        if item.endswith(".idx") or item.endswith(".grib2"):
            os.remove(os.path.join(os.curdir, item))










hdr = False  if os.path.isfile("%s-%s.csv" % (model_name, model_date)) else True

donneesjour.to_csv("%s-%s.csv" % (model_name, model_date), index=False,header=hdr,mode='a')






