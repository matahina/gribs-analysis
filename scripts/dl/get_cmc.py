#!/usr/bin/python3

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

model_date = str(sys.argv[1])
model_run = str(sys.argv[2])

os.chdir("../../data/gem/")

n_pert = 21


for param in ["HGT_ISBL_0500", "TMP_ISBL_0850", "TMP_TGL_2m", "APCP_SFC_0"]:
    for ech in list(range(0,193,3)) + list(range(198,385,6)):

        full_url = "https://dd.weather.gc.ca/"+model_date+"/WXO-DD/ensemble/geps/grib2/raw/"+model_run+"/"+"{:03d}".format(ech)+"/CMC_geps-raw_"+param+"_latlon0p5x0p5_"+model_date+model_run+"_P"+"{:03d}".format(ech)+"_allmbrs.grib2"

        file_name = param+"."+"{:03d}".format(ech)+"."+model_date+""+model_run+".daily.grb2"
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
