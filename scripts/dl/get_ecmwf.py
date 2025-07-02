#! /usr/bin/python3

import os



model_date = str(sys.argv[1])
model_run = str(sys.argv[2])

from ecmwf.opendata import Client


client = Client(source="ecmwf")

os.chdir("../../data/ecmwf/")

try:
    for i in range(1,51):
        client.retrieve(
            date=model_date,
            time=model_run,
                number=i,
            step=list(range(0,144,3))+list(range(144,366,6)),
            stream="enfo",
            type="pf",
            param=["gh"],
            levelist=[500],
            target=str(sys.argv[1])+str(sys.argv[2])+"data_hgt"+str(i)+".grib2",
        )
        client.retrieve(
            date=model_date,
            time=model_run,
            step=list(range(0,144,3))+list(range(144,366,6)),
            stream="enfo",
            type="pf",
            param=["t"],
            levelist=[850],
            target=str(sys.argv[1])+str(sys.argv[2])+"data_talt"+str(i)+".grib2",
        )
        client.retrieve(
            date=model_date,
            time=model_run,
            step=list(range(0,144,3))+list(range(144,366,6)),
            stream="enfo",
            type="pf",
            param=["2t", "tp"],
            target=str(sys.argv[1])+str(sys.argv[2])+"data_tsolpp"+str(i)+".grib2",
        )
except Exception as error:
    with open('../logs/'+model_date+'.log', 'a') as errlog:
        errlog.write('Error: ',error)
        errlog.write('\n')



