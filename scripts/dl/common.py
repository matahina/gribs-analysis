#!/usr/bin/python3

import urllib.request
import urllib.parse
import time
from ecmwf.opendata import Client

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
