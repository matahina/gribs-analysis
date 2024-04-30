#! /usr/bin/python3

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

config = configparser.ConfigParser()
config.read('magic_config.ini')

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
        return result_west
    if we == "e":
        return result_east

model_date = str(sys.argv[1])
model_run = str(sys.argv[2])
model_name = str(sys.argv[3])

os.chdir("../../data/"+model_name+"/")

if model_name == "gefs":
    n_pert = 31
else:
    n_pert = 21

if model_name != "cfs":

    for sc in range(1,n_pert):
        for ech in list(range(0,193,3)) + list(range(198,385,6)):
            for prof_name, location in profiles.items():

                if model_name == "fnmoc":
                    url = 'https://nomads.ncep.noaa.gov/cgi-bin/filter_fens.pl'
                    body_dir = '/fens.'+model_date+'/'+model_run+'/pgrb2ap5'
                    body_file = 'ENSEMBLE.halfDegree.MET.fcst_et'+"{:03d}".format(sc)+'.'+"{:03d}".format(ech)+'.'+model_date+model_run

                if model_name == "gefs":
                    url = 'https://nomads.ncep.noaa.gov/cgi-bin/filter_gefs_atmos_0p50a.pl'
                    body_dir = '/gefs.'+model_date+'/'+model_run+'/atmos/pgrb2ap5'
                    body_file = 'gep'+'{:02d}'.format(sc)+'.t'+model_run+'z.pgrb2a.0p50.f'+'{:03d}'.format(ech)

                if model_name == "gem":
                    url = 'https://nomads.ncep.noaa.gov/cgi-bin/filter_cmcens.pl'
                    body_dir = '/cmce.'+model_date+'/'+model_run+'/pgrb2ap5'
                    body_file = 'cmc_gep'+'{:02d}'.format(sc)+'.t'+model_run+'z.pgrb2a.0p50.f'+'{:03d}'.format(ech)

                ## Set the request's body.
                post_body = {
                    'dir' : body_dir,
                    'file' : body_file,
                    'lev_2_m_above_ground' : 'on',
                    'lev_500_mb' : 'on',
                    'lev_850_mb' : 'on',
                    'lev_surface' : 'on',
                    'var_APCP' : 'on',
                    'var_HGT' : 'on',
                    'var_TMP' : 'on',
                    'subregion' : '',
                    'toplat' : north(location[0]),
                    'leftlon' : west_east(location[1],"w"),
                    'rightlon' : west_east(location[1],"e"),
                    'bottomlat' : south(location[0]),
                        }

                postfields = urllib.parse.urlencode(post_body)

                full_url = url + '?' + postfields

                file_name = model_date+"_"+model_run+"_"+"{:03d}".format(sc)+"_"+"{:03d}".format(ech)+"_"+prof_name+".grb2"

                print(file_name)
                print(full_url)

                i = 0
                do_loop = True
                while do_loop:
                    i = i + 1
                    do_loop = False
                    try:
                        response = urllib.request.urlretrieve(
                            full_url,
                            file_name)
                    except urllib.error.HTTPError as e:
                        with open('../logs/'+model_date+'.log', 'a') as errlog:
                            errlog.write(model_name+"   "+file_name+' Error code: '+str(e.code)+'\n')
                        print('Error code: ', e.code)
                    except urllib.error.URLError as e:
                        with open('../logs/'+model_date+'.log', 'a') as errlog:
                            errlog.write(model_name+"   "+file_name+' Reason: '+ str(e.reason)+'\n')
                        print('Reason: ', e.reason)
                    except http.client.RemoteDisconnected as e:
                        with open('../logs/'+model_date+'.log', 'a') as errlog:
                            errlog.write(model_name+"   "+file_name+' Reason: '+ str(e.reason)+'\n')
                            errlog.write(model_name+"   "+file_name+' Will retry'+'\n')
                        print('Reason: ', e.reason)
                        print(" Will retry")
                        do_loop = True
                    if i > 100:
                        break

else:
    for sc in range(1,5):
        for param in ["z500", "t850", "prate", "tmp2m"]:

            full_url = "https://nomads.ncep.noaa.gov/pub/data/nccf/com/cfs/prod/cfs."+model_date+"/"+model_run+"/time_grib_"+"{:02d}".format(sc)+"/"+param+"."+"{:02d}".format(sc)+"."+model_date+""+model_run+".daily.grb2"

            file_name = param+"."+"{:02d}".format(sc)+"."+model_date+""+model_run+".daily.grb2"
            print(file_name)

            i = 0
            do_loop = True
            while do_loop:
                i = i +1
                try:
                    server_size = requests.head(full_url).headers.get('content-length')

                    dl_size = 0

                    j = 0

                    if server_size == "0":
                        with open('../logs/'+model_date+'.log', 'a') as errlog:
                            errlog.write(model_name+"   "+file_name+'   Server size is null so file might not exist or access forbidden!\n')
                        print('Server size is null so file might not exist or access forbidden!')
                    while str(dl_size) != server_size:
                        response = urllib.request.urlretrieve(
                        full_url,
                        file_name)

                        dl_size = os.stat(file_name).st_size

                        print(dl_size)
                        print(server_size)

                        j = j +1
                        if j >1:
                            with open('../logs/'+model_date+'.log', 'a') as errlog:
                                errlog.write(model_name+"   "+file_name+' Expected: '+server_size+' Retrieved: '+str(dl_size)+'\n')
                                errlog.write(model_name+"   "+file_name+' Will retry'+'\n')
                            print(' Expected: '+server_size+' Retrieved: '+str(dl_size))
                            print(" Will retry")
                            do_loop = True
                            break
                        if j >100:
                            with open('../logs/'+model_date+'.log', 'a') as errlog:
                                errlog.write(model_name+"   "+file_name+' Expected: '+server_size+' Retrieved: '+str(dl_size)+'\n')
                                errlog.write(model_name+"   "+file_name+" WON'T RETRY!!\n")
                            print(' Expected: '+server_size+' Retrieved: '+str(dl_size))
                            print(" WON'T RETRY!!")
                            do_loop = False
                            break
                    if j < 100:
                        do_loop = False
                except urllib.error.HTTPError as e:
                    with open('../logs/'+model_date+'.log', 'a') as errlog:
                        errlog.write(model_name+"   "+file_name+' Error code: '+str(e.code)+'\n')
                    print('Error code: ', e.code)
                    do_loop = False
                except urllib.error.URLError as e:
                    with open('../logs/'+model_date+'.log', 'a') as errlog:
                        errlog.write(model_name+"   "+file_name+' Reason: '+ str(e.reason)+'\n')
                    print('Reason: ', e.reason)
                    if ("incomplete" in e.reason) or ("timed out" in e.reason):
                        with open('../logs/'+model_date+'.log', 'a') as errlog:
                            errlog.write(model_name+"   "+file_name+' Will retry'+'\n')
                        print(' Will retry')
                        do_loop = True
                    else:
                        do_loop = False
                except http.client.RemoteDisconnected as e:
                    with open('../logs/'+model_date+'.log', 'a') as errlog:
                        errlog.write(model_name+"   "+file_name+' Reason: '+ str(e)+'\n')
                        errlog.write(model_name+"   "+file_name+' Will retry'+'\n')
                    print('Reason: ', e)
                    print(" Will retry")
                    do_loop = True
                if i > 100:
                    do_loop = False
