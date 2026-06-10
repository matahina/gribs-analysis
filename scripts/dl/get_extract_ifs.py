#! /usr/bin/python3


import common
import os,sys
import time

import threading

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

thread_a = threading.Thread(target=common.get_ecmwf,
                            args=("ifs","azure",model_date,model_run,list(range(0,144,3))+list(range(144,366,6)),
                                  ["gh"],[500],model_date+model_run+"data_hgt.grib2"))
thread_list.append(thread_a)

thread_b = threading.Thread(target=common.get_ecmwf,
                            args=("ifs","azure",model_date,model_run,list(range(0,144,3))+list(range(144,366,6)),
                                  ["t"],[850],model_date+model_run+"data_talt.grib2"))
thread_list.append(thread_b)

thread_c = threading.Thread(target=common.get_ecmwf,
                            args=("ifs","azure",model_date,model_run,list(range(0,144,3))+list(range(144,366,6)),
                                  ["tp"],[],model_date+model_run+"data_pp.grib2"))
thread_list.append(thread_c)

thread_d = threading.Thread(target=common.get_ecmwf,
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


grbfile = "%s%sdata_hgt.grib2" % (model_date, model_run)
extract_a = pd.DataFrame({'runs': [], 'dates': [], 'profile': [], 'geop': []})

if Path(grbfile).is_file():
    if os.path.getsize(grbfile) > 0:
        try:
            ds_grib = xr.open_dataset(grbfile, engine="cfgrib", decode_timedelta=False)
            for prof_name, location in profiles.items():
                print("prof_name: "+str(prof_name))
                for pert in range(1,51,10):
                    the_df_a = ds_grib.sel(longitude=location[1], latitude=location[0], method='nearest',number=range(pert,pert+10)).to_dataframe()
                    print("sc: "+str(pert))
                    for the_pert in range(pert,pert+10,1):
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

grbfile = "%s%sdata_talt.grib2" % (model_date, model_run)
extract_b = pd.DataFrame({'runs': [], 'dates': [], 'profile': [], 'tempalt': []})

if Path(grbfile).is_file():
    if os.path.getsize(grbfile) > 0:
        try:
            ds_grib = xr.open_dataset(grbfile, engine="cfgrib", decode_timedelta=False)
            for prof_name, location in profiles.items():
                print("prof_name: "+str(prof_name))
                for pert in range(1,51,10):
                    the_df_b = ds_grib.sel(longitude=location[1], latitude=location[0], method='nearest',number=range(pert,pert+10)).to_dataframe()
                    print("sc: "+str(pert))
                    for the_pert in range(pert,pert+10,1):
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


grbfile = "%s%sdata_tsol.grib2" % (model_date, model_run)
extract_c = pd.DataFrame({'runs': [], 'dates': [], 'profile': [], 'tempsol': []})

if Path(grbfile).is_file():
    if os.path.getsize(grbfile) > 0:
        try:
            ds_grib = xr.open_dataset(grbfile, engine="cfgrib", decode_timedelta=False)
            for prof_name, location in profiles.items():
                print("prof_name: "+str(prof_name))
                for pert in range(1,51,10):
                    the_df_c = ds_grib.sel(longitude=location[1], latitude=location[0], method='nearest',number=range(pert,pert+10)).to_dataframe()
                    print("sc: "+str(pert))
                    for the_pert in range(pert,pert+10,1):
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


grbfile = "%s%sdata_pp.grib2" % (model_date, model_run)
extract_d = pd.DataFrame({'runs': [], 'dates': [], 'profile': [], 'precs': []})

if Path(grbfile).is_file():
    if os.path.getsize(grbfile) > 0:
        try:
            ds_grib = xr.open_dataset(grbfile, engine="cfgrib", decode_timedelta=False)
            for prof_name, location in profiles.items():
                print("prof_name: "+str(prof_name))
                for pert in range(1,51,10):
                    the_df_d = ds_grib.sel(longitude=location[1], latitude=location[0], method='nearest',number=range(pert,pert+10)).to_dataframe()
                    print("sc: "+str(pert))
                    for the_pert in range(pert,pert+10,1):
                        try:
                            df_d = the_df_d.iloc[the_df_d.index.get_level_values('number') == the_pert]
                            df_d["runs"] = str(df_d["time"].iloc[0]) + " sc%02d" % (the_pert)
                            df_d["dates"] = df_d["valid_time"]
                            df_d["profile"] = prof_name
                            df_d["precs"] = df_d["tp"]
                            df_d['precs'] = df_d['precs'].diff().fillna(df_d['precs'].iloc[0])
                            if ds_grib.tp.units == 'm':
                                df_d['precs'] = df_d['precs'] * 1000
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


liste = os.listdir(os.curdir)

for item in liste:
    if item.endswith(".idx") or item.endswith(".grib2"):
        os.remove(os.path.join(os.curdir, item))








