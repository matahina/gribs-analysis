#! /usr/bin/python3

import os,sys
import time


model_date = str(sys.argv[1])
model_run = str(sys.argv[2])

from ecmwf.opendata import Client

os.chdir("../../data/ecmwf/")

for retries in range(1,50):
    try:
        resume
        break
    except:
        try:
            client = Client(source="azure")
            resume = client.retrieve(
                date=model_date,
                time=model_run,
                step=list(range(0,144,3))+list(range(144,366,6)),
                stream="enfo",
                type="pf",
                param=["gh"],
                levelist=[500],
                target=model_date+model_run+"data_hgt.grib2",
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
            client = Client(source="azure")
            resume = client.retrieve(
                date=model_date,
                time=model_run,
                step=list(range(0,144,3))+list(range(144,366,6)),
                stream="enfo",
                type="pf",
                param=["t"],
                levelist=[850],
                target=model_date+model_run+"data_talt.grib2",
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
            client = Client(source="azure")
            resume = client.retrieve(
                date=model_date,
                time=model_run,
                step=list(range(0,144,3))+list(range(144,366,6)),
                stream="enfo",
                type="pf",
                param=["tp"],
                target=model_date+model_run+"data_pp.grib2",
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
            client = Client(source="azure")
            resume = client.retrieve(
                date=model_date,
                time=model_run,
                step=list(range(0,144,3))+list(range(144,366,6)),
                stream="enfo",
                type="pf",
                param=["2t"],
                target=model_date+model_run+"data_tsol.grib2",
            )
        except:
            with open('../logs/'+model_date+'.log', 'a') as errlog:
                errlog.write("error")
                errlog.write('\n')
            time.sleep(100)








