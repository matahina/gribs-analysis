#!/usr/bin/python3



import xarray as xr
import math
import configparser
import sys, os
import pandas as pd
from pathlib import Path

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

def north(lat):
    result = (round(float(lat) * 2) / 2 )
    if result > 90:
        result = 90
    return result
def south(lat):
    result = (round(float(lat) * 2) / 2 )-0.5
    if result < -90:
        result = -90
    return result
def west_east(lon,we):
    result_west = (round(float(lon) * 2) / 2 )-0.5
    if result_west < 0:
        result_west = 0
    result_east = (round(float(lon) * 2) / 2 )
    if result_east > 360:
        result_east = 360
    if we == "w":
        return result_west
    if we == "e":
        return result_east


model_date = str(sys.argv[1])
model_name = str(sys.argv[2])


donneesrun = pd.DataFrame({'runs': [], 'dates': [], 'profile': [], 'geop': [], 'tempalt': [], 'tempsol': [], 'precs': []})


if model_name == "gefs":
    last_z = 18
    step_z = 6
    last_sc = 30
    the_range = list(range(0, 193, 3)) + list(range(198, 385, 6))

if model_name == "gem" or model_name == "fnmoc":
    last_z = 12
    step_z = 12
    last_sc = 20
    the_range = list(range(0, 193, 3)) + list(range(198, 385, 6))

if model_name == "cfs":
    last_z = 18
    step_z = 6
    last_sc = 4


if model_name == "ecmwf":
    last_z = 12
    step_z = 12
    last_sc = 50


first_try = True

match model_name:
    case "cfs":
        for z in range(0, last_z+1, step_z):
            print("z: "+str(z))
            for sc in range(1, last_sc+1, 1):
                print("sc: "+str(sc))
                filename = ".%02d.%s%02d.daily.grb2" % (sc, model_date, z)

                grbfile = "../../data/cfs/z500%s" % filename
                extract_a = pd.DataFrame({'runs': [], 'dates': [], 'profile': [], 'geop': []})

                if Path(grbfile).is_file():
                    if os.path.getsize(grbfile) > 0:
                        try:
                            ds_grib = xr.open_dataset(grbfile, engine="cfgrib")
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

                grbfile = "../../data/cfs/t850%s" % filename
                extract_b = pd.DataFrame({'runs': [], 'dates': [], 'profile': [], 'tempalt': []})

                if Path(grbfile).is_file():
                    if os.path.getsize(grbfile) > 0:
                        try:
                            ds_grib = xr.open_dataset(grbfile, engine="cfgrib")
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


                grbfile = "../../data/cfs/tmp2m%s" % filename
                extract_c = pd.DataFrame({'runs': [], 'dates': [], 'profile': [], 'tempsol': []})

                if Path(grbfile).is_file():
                    if os.path.getsize(grbfile) > 0:
                        try:
                            ds_grib = xr.open_dataset(grbfile, engine="cfgrib")
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


                grbfile = "../../data/cfs/prate%s" % filename
                extract_d = pd.DataFrame({'runs': [], 'dates': [], 'profile': [], 'precs': []})

                if Path(grbfile).is_file():
                    if os.path.getsize(grbfile) > 0:
                        try:
                            ds_grib = xr.open_dataset(grbfile, engine="cfgrib")
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

    case "ecmwf":
        for z in range(0, last_z+1, step_z):
            print("z: "+str(z))
            grbfile = "../../data/ecmwf/%s%02ddata_hgt.grib2" % (model_date, z)
            extract_a = pd.DataFrame({'runs': [], 'dates': [], 'profile': [], 'geop': []})

            if Path(grbfile).is_file():
                if os.path.getsize(grbfile) > 0:
                    try:
                        ds_grib = xr.open_dataset(grbfile, engine="cfgrib")
                        for prof_name, location in profiles.items():
                            print("prof_name: "+str(prof_name))
                            for pert in range(1,last_sc+1,10):
                                the_df_a = ds_grib.sel(longitude=location[1], latitude=location[0], method='nearest',number=list(range(pert,pert+10))).to_dataframe()
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

            grbfile = "../../data/ecmwf/%s%02ddata_talt.grib2" % (model_date, z)
            extract_b = pd.DataFrame({'runs': [], 'dates': [], 'profile': [], 'tempalt': []})

            if Path(grbfile).is_file():
                if os.path.getsize(grbfile) > 0:
                    try:
                        ds_grib = xr.open_dataset(grbfile, engine="cfgrib")
                        for prof_name, location in profiles.items():
                            print("prof_name: "+str(prof_name))
                            for pert in range(1,last_sc+1,10):
                                the_df_b = ds_grib.sel(longitude=location[1], latitude=location[0], method='nearest',number=list(range(pert,pert+10))).to_dataframe()
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


            grbfile = "../../data/ecmwf/%s%02ddata_tsolpp.grib2" % (model_date, z)
            extract_c = pd.DataFrame({'runs': [], 'dates': [], 'profile': [], 'tempsol': [], 'precs': []})

            if Path(grbfile).is_file():
                if os.path.getsize(grbfile) > 0:
                    try:
                        ds_grib = xr.open_dataset(grbfile, engine="cfgrib")
                        for prof_name, location in profiles.items():
                            print("prof_name: "+str(prof_name))
                            for pert in range(1,last_sc+1,10):
                                the_df_c = ds_grib.sel(longitude=location[1], latitude=location[0], method='nearest',number=list(range(pert,pert+10))).to_dataframe()
                                print("sc: "+str(pert))
                                for the_pert in range(pert,pert+10,1):
                                    try:
                                        df_c = the_df_c.iloc[the_df_c.index.get_level_values('number') == the_pert]
                                        df_c["runs"] = str(df_c["time"].iloc[0]) + " sc%02d" % (the_pert)
                                        df_c["dates"] = df_c["valid_time"]
                                        df_c["profile"] = prof_name
                                        df_c["tempsol"] = df_c["t2m"] -273.15
                                        df_c["precs"] = df_c["tp"] * 3600 * 6
                                        extract = df_c[["runs","dates","profile","tempsol","precs"]]
                                    except:
                                        extract = pd.DataFrame({'runs': [], 'dates': [], 'profile': [], 'tempsol': [], 'precs': []})

                                    frames = [extract,extract_c]
                                    try:
                                        new_extract_c = pd.concat([df for df in frames if not df.empty], ignore_index=True)
                                        extract_c = new_extract_c
                                    except:
                                        pass
                    except:
                        pass

            donneesrun_a = pd.merge(extract_a, extract_b, on=["runs", "dates", "profile"], how = 'outer')
            donneesrun = pd.merge(extract_c, donneesrun_a, on=["runs", "dates", "profile"], how = 'outer')

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



    case _:
        for z in range(0, last_z+1, step_z):
            print("z: "+str(z))
            for sc in range(1, last_sc+1, 1):
                print("sc: "+str(sc))
                for ech in the_range:
                    donneesrun = pd.DataFrame({'runs': [], 'dates': [], 'profile': [], 'geop': [], 'tempalt': [], 'tempsol': [], 'precs': []})

                    for prof_name, location in profiles.items():
                        # print("prof_name: "+str(prof_name))
                        if config['General']['area'] == 'yes':
                            filename = "%s_%02d_%03d_%03d.grb2" % (
                                                model_date,
                                                z,
                                                sc,
                                                ech)
                        else:
                            filename = "%s_%02d_%03d_%03d_%s.grb2" % (
                                                model_date,
                                                z,
                                                sc,
                                                ech,location)
                        grbfile = "../../data/%s/%s" % (model_name, filename)
                        if Path(grbfile).is_file():
                            if os.path.getsize(grbfile) > 0:
                                try:
                                    ds_grib = xr.open_dataset(grbfile, engine="cfgrib")
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

                                    newdata = pd.DataFrame({'runs': [var_run], 'dates': [var_date], 'profile': [prof_name], 'geop': [var_hgt], 'tempalt': [var_talt], 'tempsol': [var_tsol], 'precs': [var_pp]})
                                except:
                                    newdata = pd.DataFrame({'runs': [], 'dates': [], 'profile': [], 'geop': [], 'tempalt': [], 'tempsol': [], 'precs': []})

                                frames = [donneesrun,newdata]
                                try:
                                    new_donneesrun = pd.concat([df for df in frames if not df.empty], ignore_index=True)
                                    donneesrun = new_donneesrun
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


donneesjour.to_csv("../../data/%s/%s-%s.csv" % (model_name, model_name, model_date), index=False)

dir_name = "../../data/%s/" % (model_name)
liste = os.listdir(dir_name)

for item in liste:
    if item.endswith(".idx"):
        os.remove(os.path.join(dir_name, item))
