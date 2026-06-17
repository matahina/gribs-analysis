#!/usr/bin/python3
import configparser
import urllib.request
import urllib.parse
import time
from ecmwf.opendata import Client
import pandas as pd
from pathlib import Path
import cfgrib
pd.options.mode.chained_assignment = None # comment to get all warnings
import os
import xarray as xr
import math
def get_ens(da_url, da_name, model_date, model_name):
    i = 0
    do_loop = True
    while do_loop:
        i = i + 1
        # print("")
        # print(da_name)
        # print(da_url)
        # print(i)
        do_loop = False
        try:
            response = urllib.request.urlretrieve(
                da_url,
                da_name)
        except urllib.error.HTTPError as e:
            with open('../logs/'+model_date+'.log', 'a') as errlog:
                errlog.write(model_name+"   "+da_name+' Error code: '+str(e.code)+'\n')
                if e.code == 302:
                    errlog.write(model_name+"   "+da_name+' Will retry'+'\n')
            print('Error code: ', e.code)
            if e.code == 302:
                print(" Will retry")
                do_loop = True
                time.sleep(600)
        except urllib.error.URLError as e:
            with open('../logs/'+model_date+'.log', 'a') as errlog:
                errlog.write(model_name+"   "+da_name+' Reason: '+ str(e.reason)+'\n')
            print('Reason: ', e.reason)
        except http.client.RemoteDisconnected as e:
            with open('../logs/'+model_date+'.log', 'a') as errlog:
                errlog.write(model_name+"   "+da_name+' Reason: '+ str(e.reason)+'\n')
                errlog.write(model_name+"   "+da_name+' Will retry'+'\n')
            print('Reason: ', e.reason)
            print(" Will retry")
            do_loop = True
        if i > 100:
            if do_loop:
                errlog.write(model_name+"   "+file_name+" WON'T RETRY!!\n")
                print(" WON'T RETRY!!")
            do_loop = False
    return ""


def get_ecmwf(the_model, the_source, model_date, model_run, the_steps, the_params, the_levels, the_target):
    for retries in range(1,50):
        try:
            resume
            break
        except:
            try:
                client = Client(
                    model=the_model,
                    source=the_source
                    )
                resume = client.retrieve(
                    date=model_date,
                    time=model_run,
                    step=the_steps,
                    stream="enfo",
                    type="pf",
                    param=the_params,
                    levelist=the_levels,
                    target=the_target,
                )
            except:
                with open('../logs/'+model_date+'.log', 'a') as errlog:
                    errlog.write("error")
                    errlog.write('\n')
                time.sleep(100)

def north(lat):
    result = (round(float(lat) * 2) / 2 )
    if result > 90:
        result = 90
    return str(result)
def south(lat):
    result = (round(float(lat) * 2) / 2 )-0.5
    if result < -90:
        result = -90
    return str(result)
def west_east(lon,we):
    result_west = (round(float(lon) * 2) / 2 )-0.5
    if result_west < 0:
        result_west = 0
    result_east = (round(float(lon) * 2) / 2 )
    if result_east > 360:
        result_east = 360
    if we == "w":
        return str(result_west)
    if we == "e":
        return str(result_east)


def data_ens_ai(sc,ech,model_date,model_name,model_run,profiles):
    print("sc: "+str(sc))
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
    return (sc,donneesrun)




def data_ens(sc,ech,model_date,model_name,model_run,profiles):
    print("sc: "+str(sc))
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
    return (sc,donneesrun)
