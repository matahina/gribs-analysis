#! /usr/bin/python3

import common
import os,sys
import time

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


import configparser


import xarray as xr
import math
import pandas as pd
from pathlib import Path
import cfgrib
pd.options.mode.chained_assignment = None # comment to get all warnings

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
model_name = "ifs"

from ecmwf.opendata import Client

os.chdir("../../data/ifs/")

thread_list = []

thread_a = Thread(target=common.get_ecmwf,
                            args=("ifs","azure",model_date,model_run,list(range(0,144,3))+list(range(144,366,6)),
                                  ["gh"],[500],model_date+model_run+"data_hgt.grib2"))
thread_list.append(thread_a)

thread_b = Thread(target=common.get_ecmwf,
                            args=("ifs","azure",model_date,model_run,list(range(0,144,3))+list(range(144,366,6)),
                                  ["t"],[850],model_date+model_run+"data_talt.grib2"))
thread_list.append(thread_b)

thread_c = Thread(target=common.get_ecmwf,
                            args=("ifs","azure",model_date,model_run,list(range(0,144,3))+list(range(144,366,6)),
                                  ["tp"],[],model_date+model_run+"data_pp.grib2"))
thread_list.append(thread_c)

thread_d = Thread(target=common.get_ecmwf,
                            args=("ifs","azure",model_date,model_run,list(range(0,144,3))+list(range(144,366,6)),
                                  ["2t"],[],model_date+model_run+"data_tsol.grib2"))
thread_list.append(thread_d)

for thread in thread_list:
    thread.start()
for thread in thread_list:
    thread.join()
time.sleep(0.1)




first_try = True

donneesrun = pd.DataFrame({'runs': [], 'dates': [], 'profile': [], 'geop': [], 'tempalt': [], 'tempsol': [], 'precs': []})



def hgt_extract(the_df,pert,basepert):
    extract = pd.DataFrame({'runs': [], 'dates': [], 'profile': [], 'geop': []})
    try:
        df_a = the_df.iloc[the_df.index.get_level_values('number') == pert]
        df_a["runs"] = str(df_a["time"].iloc[0]) + " sc%02d" % (pert)
        df_a["dates"] = df_a["valid_time"]
        df_a["profile"] = prof_name
        df_a["geop"] = df_a["gh"] / 10
        extract = df_a[["runs","dates","profile","geop"]]
    except:
        pass


    try:
        frames = [extract,extract_a]
        new_extract_a = pd.concat([df for df in frames if not df.empty], ignore_index=True)
        extract_a = new_extract_a
    except:
        extract_a = extract

    return (pert#-basepert
            , extract_a)

def tempalt_extract(the_df,pert,basepert):
    extract = pd.DataFrame({'runs': [], 'dates': [], 'profile': [], 'tempalt': []})
    try:
        df_a = the_df.iloc[the_df.index.get_level_values('number') == pert]
        df_a["runs"] = str(df_a["time"].iloc[0]) + " sc%02d" % (pert)
        df_a["dates"] = df_a["valid_time"]
        df_a["profile"] = prof_name
        df_a["tempalt"] = df_a["t"] -273.15
        extract = df_a[["runs","dates","profile","tempalt"]]
    except:
        pass


    try:
        frames = [extract,extract_a]
        new_extract_a = pd.concat([df for df in frames if not df.empty], ignore_index=True)
        extract_a = new_extract_a
    except:
        extract_a = extract

    return (pert#-basepert
            , extract_a)

def tempsol_extract(the_df,pert,basepert):
    extract = pd.DataFrame({'runs': [], 'dates': [], 'profile': [], 'tempsol': []})
    try:
        df_a = the_df.iloc[the_df.index.get_level_values('number') == pert]
        df_a["runs"] = str(df_a["time"].iloc[0]) + " sc%02d" % (pert)
        df_a["dates"] = df_a["valid_time"]
        df_a["profile"] = prof_name
        df_a["tempsol"] = df_a["t2m"] -273.15
        extract = df_a[["runs","dates","profile","tempsol"]]
    except:
        pass


    try:
        frames = [extract,extract_a]
        new_extract_a = pd.concat([df for df in frames if not df.empty], ignore_index=True)
        extract_a = new_extract_a
    except:
        extract_a = extract

    return (pert#-basepert
            , extract_a)

def pp_extract(the_df,pert,basepert):
    extract = pd.DataFrame({'runs': [], 'dates': [], 'profile': [], 'precs': []})
    try:
        df_a = the_df.iloc[the_df.index.get_level_values('number') == pert]
        df_a["runs"] = str(df_a["time"].iloc[0]) + " sc%02d" % (pert)
        df_a["dates"] = df_a["valid_time"]
        df_a["profile"] = prof_name
        df_a["precs"] = df_a["tp"]
        df_a['precs'] = df_a['precs'].diff().fillna(df_a['precs'].iloc[0])
        if ds_grib.tp.units == 'm':
            df_a['precs'] = df_a['precs'] * 1000
        extract = df_a[["runs","dates","profile","precs"]]
    except:
        pass
    try:
        frames = [extract,extract_a]
        new_extract_a = pd.concat([df for df in frames if not df.empty], ignore_index=True)
        extract_a = new_extract_a
    except:
        extract_a = extract

    return (pert#-basepert
            , extract_a)


grbfile = "%s%sdata_hgt.grib2" % (model_date, model_run)
extract_a = pd.DataFrame({'runs': [], 'dates': [], 'profile': [], 'geop': []})

if Path(grbfile).is_file():
    if os.path.getsize(grbfile) > 0:
        try:
            ds_grib = xr.open_dataset(grbfile, engine="cfgrib", decode_timedelta=False)
            for prof_name, location in profiles.items():
                print("prof_name: "+str(prof_name))
                thread_list = []
                dataliste = [[]] * (50)
                for pert in range(1,51,10):
                    the_df_a = ds_grib.sel(longitude=location[1], latitude=location[0], method='nearest',number=range(pert,pert+10)).to_dataframe()
                    print("sc: "+str(pert))
                    for the_pert in range(pert,pert+10,1):
                        thread = CustomThread(target=hgt_extract,args=(the_df_a,the_pert,pert))
                        thread_list.append(thread)
                for thread in thread_list:
                    thread.start()
                for thread in thread_list:
                    res=thread.join()
                    if not res is None:
                        if res != "":
                            dataliste[res[0]-1] = res[1]
                time.sleep(0.1)
                frames = [extract_a] + dataliste
                new_extract_a = pd.concat([df for df in frames if not df.empty], ignore_index=True)
                extract_a = new_extract_a

        except:
            pass

print (extract_a)

grbfile = "%s%sdata_talt.grib2" % (model_date, model_run)
extract_b = pd.DataFrame({'runs': [], 'dates': [], 'profile': [], 'tempalt': []})

if Path(grbfile).is_file():
    if os.path.getsize(grbfile) > 0:
        try:
            ds_grib = xr.open_dataset(grbfile, engine="cfgrib", decode_timedelta=False)
            for prof_name, location in profiles.items():
                print("prof_name: "+str(prof_name))
                thread_list = []
                dataliste = [[]] * (50)
                for pert in range(1,51,10):
                    the_df_b = ds_grib.sel(longitude=location[1], latitude=location[0], method='nearest',number=range(pert,pert+10)).to_dataframe()
                    print("sc: "+str(pert))
                    for the_pert in range(pert,pert+10,1):
                        thread = CustomThread(target=tempalt_extract,args=(the_df_b,the_pert,pert))
                        thread_list.append(thread)
                for thread in thread_list:
                    thread.start()
                for thread in thread_list:
                    res=thread.join()
                    if not res is None:
                        if res != "":
                            dataliste[res[0]-1] = res[1]
                time.sleep(0.1)
                frames = [extract_b] + dataliste
                new_extract_b = pd.concat([df for df in frames if not df.empty], ignore_index=True)
                extract_b = new_extract_b
        except:
            pass


grbfile = "%s%sdata_tsol.grib2" % (model_date, model_run)
extract_c = pd.DataFrame({'runs': [], 'dates': [], 'profile': [], 'tempsol': []})

if Path(grbfile).is_file():
    if os.path.getsize(grbfile) > 0:
        try:
            ds_grib = xr.open_dataset(grbfile, engine="cfgrib", decode_timedelta=False)
            for prof_name, location in profiles.items():
                print("prof_name: "+str(prof_name))
                thread_list = []
                dataliste = [[]] * (50)
                for pert in range(1,51,10):
                    the_df_c = ds_grib.sel(longitude=location[1], latitude=location[0], method='nearest',number=range(pert,pert+10)).to_dataframe()
                    print("sc: "+str(pert))
                    for the_pert in range(pert,pert+10,1):
                        thread = CustomThread(target=tempsol_extract,args=(the_df_c,the_pert,pert))
                        thread_list.append(thread)
                for thread in thread_list:
                    thread.start()
                for thread in thread_list:
                    res=thread.join()
                    if not res is None:
                        if res != "":
                            dataliste[res[0]-1] = res[1]
                time.sleep(0.1)
                frames = [extract_c] + dataliste
                new_extract_c = pd.concat([df for df in frames if not df.empty], ignore_index=True)
                extract_c = new_extract_c
        except:
            pass


grbfile = "%s%sdata_pp.grib2" % (model_date, model_run)
extract_d = pd.DataFrame({'runs': [], 'dates': [], 'profile': [], 'precs': []})
thread_list = []

if Path(grbfile).is_file():
    if os.path.getsize(grbfile) > 0:
        try:
            ds_grib = xr.open_dataset(grbfile, engine="cfgrib", decode_timedelta=False)
            for prof_name, location in profiles.items():
                print("prof_name: "+str(prof_name))
                thread_list = []
                dataliste = [[]] * (50)
                for pert in range(1,51,10):
                    the_df_d = ds_grib.sel(longitude=location[1], latitude=location[0], method='nearest',number=range(pert,pert+10)).to_dataframe()
                    print("sc: "+str(pert))
                    for the_pert in range(pert,pert+10,1):
                        thread = CustomThread(target=pp_extract,args=(the_df_d,the_pert,pert))
                        thread_list.append(thread)
                for thread in thread_list:
                    thread.start()
                for thread in thread_list:
                    res=thread.join()
                    if not res is None:
                        if res != "":
                            dataliste[res[0]-1] = res[1]
                time.sleep(0.1)
                frames = [extract_d] + dataliste
                new_extract_d = pd.concat([df for df in frames if not df.empty], ignore_index=True)
                extract_d = new_extract_d
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

liste = os.listdir(os.curdir)

for item in liste:
    if item.endswith(".idx") or item.endswith(".grib2"):
        os.remove(os.path.join(os.curdir, item))


