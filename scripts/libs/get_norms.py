#! /usr/bin/python3

import configparser

from datetime import date

model_date = date.today().strftime("%Y%m%d")
model_name = "Norms"

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

profile_coords = []

profile = str(sys.argv[1])

for i in config.sections():
    if profile in i:
        if float(config[i]['lon']) < 0:
            profile_coords = [config[i]['lat'], 360 + float(config[i]['lon'])]
        else:
            profile_coords = [config[i]['lat'], config[i]['lon']]

os.chdir("../../assets/norms_"+profile+"/")

def north(lat):
    result = round(float(lat)) + 3
    if result > 90:
        result = 90
    return str(result)
def south(lat):
    result = round(float(lat)) - 3
    if result < -90:
        result = -90
    return str(result)
def west_east(lon,we):
    result_west = round(float(lon)) - 3
    if result_west < 0:
        result_west = 0
    result_east = round(float(lon)) + 3
    if result_east > 360:
        result_east = 360
    if we == "w":
        return result_west
    if we == "e":
        return result_east

def get_file(da_url, da_name):
    i = 0
    do_loop = True
    while do_loop:
        i = i + 1
        try:
            response = urllib.request.urlretrieve(
                da_url,
                da_name)
            do_loop = False
        except urllib.error.HTTPError as e:
            with open('../../data/logs/'+model_date+'.log', 'a') as errlog:
                errlog.write(model_name+"   "+da_name+' Error code: '+str(e.code)+'\n')
            print('Error code: ', e.code)
            do_loop = True
        except urllib.error.URLError as e:
            with open('../../data/logs/'+model_date+'.log', 'a') as errlog:
                errlog.write(model_name+"   "+da_name+' Reason: '+ str(e.reason)+'\n')
            print('Reason: ', e.reason)
            do_loop = True
        except http.client.RemoteDisconnected as e:
            with open('../../data/logs/'+model_date+'.log', 'a') as errlog:
                errlog.write(model_name+"   "+da_name+' Reason: '+ str(e.reason)+'\n')
            print('Reason: ', e.reason)
            do_loop = True
        if i > 100:
            do_loop = False




url = 'https://psl.noaa.gov/thredds/ncss/grid/Datasets/ncep.reanalysis2/Monthlies/LTMs/gaussian_grid/prate.sfc.mon.ltm.1991-2020.nc'
post_body = {
    'var' : "prate",
    'north' : north(profile_coords[0]),
    'west' : west_east(profile_coords[1],"w"),
    'east' : west_east(profile_coords[1],"e"),
    'south' : south(profile_coords[0]),
    'horizStride' : '1',
    'time_start' : '0001-01-01T00:00:00Z',
    'time_end' : '0001-12-01T00:00:00Z',
    'accept' : 'netcdf3'
        }
postfields = urllib.parse.urlencode(post_body).replace("%3A",":")
full_url = url + '?' + postfields
file_name = "pp.nc"
print(file_name)
print(full_url)

i = 0
do_loop = True
while do_loop:
    i = i + 1
    try:
        response = urllib.request.urlretrieve(
            full_url,
            file_name)
        do_loop = False
    except urllib.error.HTTPError as e:
        with open('../../data/logs/'+model_date+'.log', 'a') as errlog:
            errlog.write(model_name+"   "+file_name+' Error code: '+str(e.code)+'\n')
        print('Error code: ', e.code)
        do_loop = True
    except urllib.error.URLError as e:
        with open('../../data/logs/'+model_date+'.log', 'a') as errlog:
            errlog.write(model_name+"   "+file_name+' Reason: '+ str(e.reason)+'\n')
        print('Reason: ', e.reason)
        do_loop = True
    except http.client.RemoteDisconnected as e:
        with open('../../data/logs/'+model_date+'.log', 'a') as errlog:
            errlog.write(model_name+"   "+file_name+' Reason: '+ str(e.reason)+'\n')
        print('Reason: ', e.reason)
        do_loop = True
    if i > 100:
        break

z500_urls = []
z500_fnames = []

t850_urls = []
t850_fnames = []

t2m_urls = []
t2m_fnames = []

for year in range(1991,2021):
    url = 'https://psl.noaa.gov/thredds/ncss/grid/Datasets/ncep.reanalysis2/pressure/hgt.'+str(year)+'.nc'
    post_body = {
        'var' : "hgt",
        'north' : north(profile_coords[0]),
        'west' : west_east(profile_coords[1],"w"),
        'east' : west_east(profile_coords[1],"e"),
        'south' : south(profile_coords[0]),
        'horizStride' : '1',
        'time_start' : str(year)+'-01-01T00:00:00Z',
        'time_end' : str(year)+'-12-31T18:00:00Z',
        'accept' : 'netcdf3',
        'vertCoord' : '500'
            }
    postfields = urllib.parse.urlencode(post_body).replace("%3A",":")
    full_url = url + '?' + postfields
    file_name = "hgt_"+str(year)+".nc"
    z500_fnames.append(file_name)
    z500_urls.append(full_url)

    url = 'https://psl.noaa.gov/thredds/ncss/grid/Datasets/ncep.reanalysis2/pressure/air.'+str(year)+'.nc'
    post_body = {
        'var' : "air",
        'north' : north(profile_coords[0]),
        'west' : west_east(profile_coords[1],"w"),
        'east' : west_east(profile_coords[1],"e"),
        'south' : south(profile_coords[0]),
        'horizStride' : '1',
        'time_start' : str(year)+'-01-01T00:00:00Z',
        'time_end' : str(year)+'-12-31T18:00:00Z',
        'accept' : 'netcdf3',
        'vertCoord' : '850'
            }
    postfields = urllib.parse.urlencode(post_body).replace("%3A",":")
    full_url = url + '?' + postfields
    file_name = "t850_"+str(year)+".nc"
    t850_fnames.append(file_name)
    t850_urls.append(full_url)

    url = 'https://psl.noaa.gov/thredds/ncss/grid/Datasets/ncep.reanalysis2/gaussian_grid/air.2m.gauss.'+str(year)+'.nc'
    post_body = {
        'var' : "air",
        'north' : north(profile_coords[0]),
        'west' : west_east(profile_coords[1],"w"),
        'east' : west_east(profile_coords[1],"e"),
        'south' : south(profile_coords[0]),
        'horizStride' : '1',
        'time_start' : str(year)+'-01-01T00:00:00Z',
        'time_end' : str(year)+'-12-31T18:00:00Z',
        'accept' : 'netcdf3'
            }
    postfields = urllib.parse.urlencode(post_body).replace("%3A",":")
    full_url = url + '?' + postfields
    file_name = "t2m_"+str(year)+".nc"

    t2m_fnames.append(file_name)
    t2m_urls.append(full_url)

for k in range(0,30):
    print(z500_urls[k])
    print(z500_fnames[k])
    print()
    print(t850_urls[k])
    print(t850_fnames[k])
    print()
    print(t2m_urls[k])
    print(t2m_fnames[k])
    print()
    thread_list = []
    thread_a = threading.Thread(target=get_file, args=(z500_urls[k],z500_fnames[k]))
    thread_list.append(thread_a)
    thread_b = threading.Thread(target=get_file, args=(t850_urls[k],t850_fnames[k]))
    thread_list.append(thread_b)
    thread_c = threading.Thread(target=get_file, args=(t2m_urls[k],t2m_fnames[k]))
    thread_list.append(thread_c)
    for thread in thread_list:
        thread.start()
    for thread in thread_list:
        thread.join()
    time.sleep(0.2)

