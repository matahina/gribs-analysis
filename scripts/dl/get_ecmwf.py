#! /usr/bin/python3

import os,sys
import time


model_date = str(sys.argv[1])
model_run = str(sys.argv[2])

from ecmwf.opendata import Client

os.chdir("../../data/ecmwf/")

for the_step in list(range(0,144,3))+list(range(144,366,6)):
    for retries in range(1,50):
        try:
            resume
            break
        except:
            try:
                client = Client(source="aws")
                resume = client.retrieve(
                    date=model_date,
                    time=model_run,
                    step=the_step,
                    stream="enfo",
                    type="pf",
                    param=["gh"],
                    levelist=[500],
                    target=model_date+model_run+"data_hgt_%03d.grib2" % the_step,
                )
            except:
                with open('../logs/'+model_date+'.log', 'a') as errlog:
                    errlog.write("error")
                    errlog.write('\n')
                time.sleep(100)

    try:
        del resume
    except:
        pass

    for retries in range(1,50):
        try:
            resume
            break
        except:
            try:
                client = Client(source="aws")
                resume = client.retrieve(
                    date=model_date,
                    time=model_run,
                    step=the_step,
                    stream="enfo",
                    type="pf",
                    param=["t"],
                    levelist=[850],
                    target=model_date+model_run+"data_talt_%03d.grib2" % the_step,
                )
            except:
                with open('../logs/'+model_date+'.log', 'a') as errlog:
                    errlog.write("error")
                    errlog.write('\n')
                time.sleep(100)

    try:
        del resume
    except:
        pass

    for retries in range(1,50):
        try:
            resume
            break
        except:
            try:
                client = Client(source="aws")
                resume = client.retrieve(
                    date=model_date,
                    time=model_run,
                    step=the_step,
                    stream="enfo",
                    type="pf",
                    param=["tp","2t"],
                    target=model_date+model_run+"data_tsolpp_%03d.grib2" % the_step,
                )
            except:
                with open('../logs/'+model_date+'.log', 'a') as errlog:
                    errlog.write("error")
                    errlog.write('\n')
                time.sleep(100)

    try:
        del resume
    except:
        pass





