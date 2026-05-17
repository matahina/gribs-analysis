#! /usr/bin/python3

import os,sys
import time


model_date = str(sys.argv[1])
model_run = str(sys.argv[2])

from ecmwf.opendata import Client

client = Client(source="azure")

os.chdir("../../data/ecmwf/")

for retries in range(1,50):
    try:
        resume
        break
    except:
        try:
            resume = client.retrieve(
                date=model_date,
                time=model_run,
                step=list(range(0,144,3))+list(range(144,366,6)),
                stream="enfo",
                type="pf",
                param=["gh"],
                levelist=[500],
                target=str(sys.argv[1])+str(sys.argv[2])+"data_hgt.grib2",
            )
        except Exception as error:
            with open('../logs/'+model_date+'.log', 'a') as errlog:
                errlog.write('ERROR: '+error)
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
            resume = client.retrieve(
                date=model_date,
                time=model_run,
                step=list(range(0,144,3))+list(range(144,366,6)),
                stream="enfo",
                type="pf",
                param=["t"],
                levelist=[850],
                target=str(sys.argv[1])+str(sys.argv[2])+"data_talt.grib2",
            )
        except Exception as error:
            with open('../logs/'+model_date+'.log', 'a') as errlog:
                errlog.write('ERROR: '+error)
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
            resume = client.retrieve(
                date=model_date,
                time=model_run,
                step=list(range(0,144,3))+list(range(144,366,6)),
                stream="enfo",
                type="pf",
                param=["2t", "tp"],
                target=str(sys.argv[1])+str(sys.argv[2])+"data_tsolpp.grib2",
            )
        except Exception as error:
            with open('../logs/'+model_date+'.log', 'a') as errlog:
                errlog.write('ERROR: '+error)
                errlog.write('\n')
            time.sleep(100)








