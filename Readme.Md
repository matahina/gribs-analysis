# Gribs-Analysis

**Experimental ECMWF branch**

> [!NOTE] 
> This program is designed to work on Linux, on a server.
>
> You need Python, Bash, R and Cron.


## What it does

It retrieves grib files from 4 different weather prediction models from NOAA and CMC (GEFS, FNMOC, GEM and CFS).

GEFS, FNMOC and GEM are ensemblist models. The different scenarios are downloaded, not the deterministic nor the control ones. Data is extracted into csv files. Grib files from n-2 day are removed everyday.

CFS is long-term model. Time grib data is downloaded. Every 10th of the month, grib files from n-1 month are removed.

For ensemblist models, a dashboard is computed with basic time series clustering of the scenarios from the previous day forecasts (up to 200 scenarios).

For long-term model, a dashboard is computed with probabilities to see above/below long-term means for different variables from the previous forecasts of the 28 last days.

Only few parameters are analyzed: geopotential (z500), temperature (t850 and t2m), precipitation (ACPC or PRATE).

It also uses data from [NCEP Reanalysis](https://psl.noaa.gov/data/gridded/data.ncep.reanalysis2.html) to compare with long-term data means.

Both downloads and dashboard generation are logged for error-catching purposes.

When everything is set up and running, generated dashboards are available in root directory of the program. Some dashboard examples are available online :

| **Ensemblists**          | **Long-Term**            |
|---|---|
| [Metz](https://matahina.ddns.net/weather/ens_dashboard_Profile_1.html)              |  [Metz](https://matahina.ddns.net/weather/cfs_dashboard_Profile_1.html)            |
| [Abidjan](https://matahina.ddns.net/weather/ens_dashboard_Profile_2.html)           |  [Abidjan](https://matahina.ddns.net/weather/cfs_dashboard_Profile_2.html)         |
| [Johannesburg](https://matahina.ddns.net/weather/ens_dashboard_Profile_3.html)      |  [Johannesburg](https://matahina.ddns.net/weather/cfs_dashboard_Profile_3.html)    |
| [Cape Town](https://matahina.ddns.net/weather/ens_dashboard_Profile_4.html)         |  [Cape Town](https://matahina.ddns.net/weather/cfs_dashboard_Profile_4.html)       |


## Requirements

### Arch/Manjaro:

```bash
sudo pacman -S r gcc-fortran gdal pandoc-cli python-urllib3 python-requests arrow netcdf curl wget podofo
```

```bash
yay -S --aur wgrib wgrib2 udunits
```

### Ubuntu 24.04.3 LTS server (minimal):

```bash
sudo apt install build-essential cmake r-base curl libssl-dev libgdal-dev libudunits2-dev python3-venv pandoc
```

For [wgrib](https://www.cpc.ncep.noaa.gov/products/wesley/wgrib.html):
```bash
wget https://ftp.cpc.ncep.noaa.gov/wd51we/wgrib/wgrib.tar
mkdir wgrib
tar -xvf wgrib.tar -C wgrib
rm wgrib.tar
cd wgrib
make
sudo cp wgrib /usr/local/bin/
```

For [wgrib2](https://github.com/NOAA-EMC/wgrib2):
    
First, up-to-date version of `libg2c`
```bash
wget https://github.com/NOAA-EMC/NCEPLIBS-g2c/archive/refs/tags/v2.2.0.zip
unzip v2.2.0.zip 
rm v2.2.0.zip 
cd NCEPLIBS-g2c-2.2.0/
mkdir build
cd build
cmake .. -DUSE_OpenJPEG=ON -DUSE_Jasper=OFF -DCMAKE_INSTALL_PREFIX="/usr/local/"
cmake --build ./ --parallel 4
sudo cmake --install ./
```
Then `wgrib2`
```bash
wget https://github.com/NOAA-EMC/wgrib2/archive/refs/tags/v3.7.0.zip
unzip v3.7.0.zip
rm v3.7.0.zip
cd wgrib2-3.7.0/
mkdir build && cd build
cmake .. -DUSE_AEC=on -DUSE_G2CLIB_HIGH=on -DUSE_G2CLIB_LOW=on -DCMAKE_INSTALL_PREFIX="/usr/local"
make
sudo make install
```

### R Packages (all distros):

```R
required.packages <- c("arrow", "flexdashboard", "lubridate", "DescTools", "spatstat.utils", "scales", "ggplot2", "TSrepr", "data.table", "cluster", "clusterCrit", "zoo", "RColorBrewer", "stringr", "reshape", "ggpubr", "gridExtra", "attempt", "dplyr", "viridis", "assertthat", "ini", "collapse", "ncdf4", "raster", "rvest", "fields", "GEOmap", "MBA", "XML", "uuid")
new.packages <- required.packages[!(required.packages %in% installed.packages()[,"Package"])]
if(length(new.packages)) install.packages(new.packages)
```

It might take a while. **Do it again if anything wrong happened.** Then
```R
install.packages("https://cran.r-project.org/src/contrib/Archive/rNOMADS/rNOMADS_2.5.3.tar.gz",
                 repos=NULL, method="libcurl")
```
## Set up (0)

### Set up python3 virtual env

You need to be at the root of `gribs-analysis` directory.

```bash
python3 -m venv ecmwf_env
source ecmwf_env/bin/activate
pip install ecmwf-opendata
deactivate
```

## Set up (1)

### Data directory

You need to be at the root of `gribs-analysis` directory.

```bash
mkdir data
cd data
mkdir cfs
mkdir fnmoc
mkdir gefs
mkdir gem
mkdir logs
mkdir ecmwf
```

## Set up (2): Profiles

### Config file

You need to be at the root of `gribs-analysis` directory.

You can run this program for different locations. Grib files are downloaded according to a subset area for each location based on given coordinates.

Edit the file `magic_config.ini`. The original one is explicit enough to understand it. You can remove profiles, add some, or leave only one. Choose the cities you want and fill it with the appropriate values. If you set `use_it = no`, data from this location won't be downloaded nor extracted.

If you have more than 2 profiles, you must set `area = yes` in *\[General\]* section. Otherwise, you can set in to `area = no`.

When the setting `area = yes` in enabled, it tells the scripts to download one grib of this subset area instead of several gribs from different locations. NOAA might block your IP if you download too much grib files for individual locations.

### Get NCEP reanalysis long-term data means

Check if [NOAA service](https://psl.noaa.gov/thredds/catalog.html) is available before...

Then run:

```bash
./scripts/dl/norms_dl.sh "Profile_1"
```

Repeat for each profile. Change the profile name given as argument according to the names in `magic_config.ini`.

## Set up (3): Crontab

The same user who runs this program has installed R packages and will edit crontab with `crontab -e`.

### Example

This is for a server in Europe/Paris tz zone:

```
## GEFS
5 9 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/gribs_launch.sh "gefs" "00" "0" "dl" "noaa"
5 15 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/gribs_launch.sh "gefs" "06" "0" "dl" "noaa"
5 21 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/gribs_launch.sh "gefs" "12" "0" "dl" "noaa"
5 3 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/gribs_launch.sh "gefs" "18" "1" "dl" "noaa"
## ECMWF
5 12 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/gribs_launch.sh "ecmwf" "00" "0" "dl" "ecmwf"
5 23 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/gribs_launch.sh "ecmwf" "12" "0" "dl" "ecmwf"
## GEM
10 9 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/gribs_launch.sh "gem" "00" "0" "dl" "noaa"
10 21 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/gribs_launch.sh "gem" "12" "0" "dl" "noaa"
## FNMOC
15 9 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/gribs_launch.sh "fnmoc" "00" "0" "dl" "noaa"
15 2 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/gribs_launch.sh "fnmoc" "12" "1" "dl" "noaa"
## CFS
20 14 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/gribs_launch.sh "cfs" "00" "0" "dl" "noaa"
20 20 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/gribs_launch.sh "cfs" "06" "0" "dl" "noaa"
20 2 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/gribs_launch.sh "cfs" "12" "1" "dl" "noaa"
20 8 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/gribs_launch.sh "cfs" "18" "1" "dl" "noaa"
## STATS
30 3 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/gribs_launch.sh "ens" "1" "Profile_1" "stats" "noaa"
31 3 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/gribs_launch.sh "ens" "1" "Profile_2" "stats" "noaa"
32 3 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/gribs_launch.sh "ens" "1" "Profile_3" "stats" "noaa"
33 3 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/gribs_launch.sh "ens" "1" "Profile_4" "stats" "noaa"
30 8 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/gribs_launch.sh "cfs" "1" "Profile_1" "stats" "noaa"
31 8 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/gribs_launch.sh "cfs" "1" "Profile_2" "stats" "noaa"
32 8 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/gribs_launch.sh "cfs" "1" "Profile_3" "stats" "noaa"
33 8 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/gribs_launch.sh "cfs" "1" "Profile_4" "stats" "noaa"
```

Two scripts can't run at the same time. Calling `gribs_launch.sh` prevents another script to start by being queued.

### Command args


```
./gribs_launch.sh [ARG1] [ARG2] [ARG3] [ARG4] [ARG5]
```

`[ARG1]` depends on ARG4, see below.

`[ARG2]` depends on ARG4, see below.

`[ARG3]` depends on ARG4, see below.

`[ARG4]` is either `dl` or `stats`, and will run and/or queue noaa_dl.sh or noaa_stats.sh with their own args, see below.

`[ARG5]` is either `noaa` or `ecmwf`, and will run and/or queue noaa_dl.sh or noaa_stats.sh with their own args, see below.


```
./noaa_dl.sh [MODEL_NAME] [MODEL_RUN] [DAY_AGO]
```

`[MODEL_NAME]` is one of the 4 models considered previously : `gefs` `gem` `fnmoc` `cfs`.

`[MODEL_RUN]` is the run of the model (00Z, 12Z...) : `00` `06` `12` `18`. Leading zero is important. GEM and FNMOC only runs at 00Z and 12Z.

`[DAY_AGO]` is for the day of the run. If you want to download a run from 4 days ago, set `4`. If you download a run the same day it has been done, set `0`. If you download a run that was done the day before, it can be because it takes a while to be available or because you're in a different time zone, set `1`.


```
./noaa_stats.sh [SET] [DAY_AGO] [PROFILE]
```

`[SET]` is either `ens` (gem+gefs+fnmoc) or `cfs`.

`[DAY_AGO]` is for the day of the runs. You should set `1` to get dashboard of all runs of previous day.

`[PROFILE]` is one of the profiles you set in ini file, by example `Profile_1`.

### Availability of runs

Availability is when forecast until h+360 is done for a run. This table with examples for 2 time zones will help you:

| **GEFS** | **Available in UTC time at** | **Available in tz Europe/Paris** | **Available in tz Hongkong** |
|---|---|---|---|
| 00Z       | 07:00                        | 09:00                            | 15:00                        |
| 06Z       | 13:00                        | 15:00                            | 21:00                        |
| 12Z       | 19:00                        | 21:00                            | 03:00 (day+1)                |
| 18Z       | 01:00 (day+1)                | 03:00 (day+1)                    | 09:00 (day+1)                |

| **ECMWF** | **Available in UTC time at** | **Available in tz Europe/Paris** | **Available in tz Hongkong** |
|---|---|---|---|
| 00Z       | 08:45                        | 10:45                            | 16:45                        |
| 12Z       | 20:45                        | 22:45                            | 04:45 (day+1)                |

| **GEM** | **Available in UTC time at** | **Available in tz Europe/Paris** | **Available in tz Hongkong** |
|---|---|---|---|
| 00Z       | 07:00                        | 09:00                            | 15:00                        |
| 12Z       | 19:00                        | 21:00                            | 03:00 (day+1)                |

| **FNMOC** | **Available in UTC time at** | **Available in tz Europe/Paris** | **Available in tz Hongkong** |
|---|---|---|---|
| 00Z       | 07:00                        | 09:00                            | 15:00                        |
| 12Z       | 00:00 (day+1)                | 02:00 (day+1)                    | 08:00 (day+1)                |

| **CFS** | **Available in UTC time at** | **Available in tz Europe/Paris** | **Available in tz Hongkong** |
|---|---|---|---|
| 00Z       | 12:00                        | 14:00                            | 20:00                        |
| 06Z       | 18:00                        | 20:00                            | 02:00 (day+1)                |
| 12Z       | 00:00 (day+1)                | 02:00 (day+1)                    | 08:00 (day+1)                |
| 18Z       | 06:00 (day+1)                | 08:00 (day+1)                    | 14:00 (day+1)                |

For Europe/Paris, DST time is considered. You can do -1h during winter but you will have to edit your crontab twice a year.

FNMOC 12z is often available much later than expected (last grib files for h+360 can appear at 23:45UTC on NOAA servers).

## Set up (4): Bonus files

You can create two other files to fit your needs :

- `[YOUR PATH!!]/gribs-analysis/scripts/libs/notify_ssh.sh` If it exists, it will be called when `noaa_dl.sh` and `noaa_stats.sh` start and end. By example, to send via ssh a notify-osd message to your computer to see your server is running this program.

- `[YOUR PATH!!]/gribs-analysis/scripts/libs/publish_dashboards.sh` If it exists, it will be called when `noaa_stats.sh` ends. By example, to move your dashboard in */var/www/* if your server is also hosting a website (or to move them via ssh-ftp to another server).

## License
This bunch of crap code lines is GPL, free, public domain, have fun with it!!!

## Project status
Active.

