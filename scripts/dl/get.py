#! /usr/bin/python3

import glob, os, sys
import subprocess
import time

import urllib.request
import urllib.parse

import requests

model_date = str(sys.argv[1])
model_run = str(sys.argv[2])
model_name = str(sys.argv[3])

# model_date = "20240421"
# model_run = "00"
# model_name = "cfs"

os.chdir("../../data/"+model_name+"/")
# os.chdir("/home/petite_fleur/Bureau/Test4/")

if model_name == "gefs":
    n_pert = 31
else:
    n_pert = 21

if model_name != "cfs":

    for sc in range(1,n_pert):
        for ech in list(range(0,193,3)) + list(range(198,385,6)):

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
                'leftlon' : '5',
                'rightlon' : '7',
                'toplat' : '50',
                'bottomlat' : '48'
                    }

            postfields = urllib.parse.urlencode(post_body)

            full_url = url + '?' + postfields

            file_name = model_date+"_"+model_run+"_"+"{:03d}".format(sc)+"_"+"{:03d}".format(ech)+".grb2"

            print(file_name)
            print(full_url)

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

else:
    for sc in range(1,5):
        for param in ["z500", "t850", "prate", "tmp2m"]:

            full_url = "https://nomads.ncep.noaa.gov/pub/data/nccf/com/cfs/prod/cfs."+model_date+"/"+model_run+"/time_grib_"+"{:02d}".format(sc)+"/"+param+"."+"{:02d}".format(sc)+"."+model_date+""+model_run+".daily.grb2"

            file_name = param+"."+"{:02d}".format(sc)+"."+model_date+""+model_run+".daily.grb2"
            print(file_name)

            try:
                server_size = requests.head(full_url).headers.get('content-length')

                response = urllib.request.urlretrieve(
                    full_url,
                    file_name)

                dl_size = os.stat(file_name).st_size
                while str(dl_size) != server_size:
                    print(dl_size)
                    print(server_size)
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
