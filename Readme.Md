# Gribs-Analysis

**Version 24.05**

> This program is designed to work on Linux, on a server.
>
> You need Python and Cron.

## What it does

It retrieves grib files from 4 different weather prediction models from NOAA and CMC (GEFS, FNMOC, GEM and CFS).

GEFS, FNMOC and GEM are ensemblist models. The different scenarios are downloaded, not the deterministic nor the control ones. Data is extracted into csv files. Grib files from n-2 day are removed everyday.

CFS is long-term model. Time grib data is downloaded. Every 10th of the month, grib files from n-1 month are removed.

For ensemblist models, a dashboard is computed with basic time series clustering of the scenarios from the previous day forecasts (up to 200 scenarios).

For long-term model, a dashboard is computed with probabilities to see above/below long-term means for different variables from the previous forecasts of the 28 last days.

Only few parameters are analyzed: geopotential (z500), temperature (t850 and t2m), precipitation (ACPC or PRATE).

It also uses data from [NCEP Reanalysis](https://psl.noaa.gov/data/gridded/data.ncep.reanalysis2.html) to compare with long-term data means.

Downloads and Dashboard generating are logged if you need to catch errors.

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
sudo pacman -S r gcc-fortran gdal pandoc-cli python-urllib3 python-requests arrow netcdf curl wget
```

```bash
yay -S --aur wgrib wgrib2 udunits
```

### Ubuntu:

```bash
sudo apt install build-essential libaec-dev zlib1g-dev libcurl4-openssl-dev libboost-dev curl wget zip unzip bzip2 gfortran gcc g++ cmake libnetcdf-dev netcdf-bin gdal-bin pandoc python3-urllib3 python3-requests r-base libgdal-dev libudunits2-0 libudunits2-dev
```
Some of them are required for compiling [wgrib2](https://gist.github.com/wxguy/945d18af773c2208a33a5e0429a4b813) in the next steps.


For [arrow](https://arrow.apache.org/install/):
```bash
sudo apt update
sudo apt install -y -V ca-certificates lsb-release wget
wget https://apache.jfrog.io/artifactory/arrow/$(lsb_release --id --short | tr 'A-Z' 'a-z')/apache-arrow-apt-source-latest-$(lsb_release --codename --short).deb
sudo apt install -y -V ./apache-arrow-apt-source-latest-$(lsb_release --codename --short).deb
sudo apt update
sudo apt install -y -V libarrow-dev # For C++
sudo apt install -y -V libarrow-glib-dev # For GLib (C)
sudo apt install -y -V libarrow-dataset-dev # For Apache Arrow Dataset C++
sudo apt install -y -V libarrow-dataset-glib-dev # For Apache Arrow Dataset GLib (C)
sudo apt install -y -V libarrow-acero-dev # For Apache Arrow Acero
sudo apt install -y -V libarrow-flight-dev # For Apache Arrow Flight C++
sudo apt install -y -V libarrow-flight-glib-dev # For Apache Arrow Flight GLib (C)
sudo apt install -y -V libgandiva-dev # For Gandiva C++
sudo apt install -y -V libgandiva-glib-dev # For Gandiva GLib (C)
sudo apt install -y -V libparquet-dev # For Apache Parquet C++
sudo apt install -y -V libparquet-glib-dev # For Apache Parquet GLib (C)
```

For [wgrib](https://www.cpc.ncep.noaa.gov/products/wesley/wgrib.html):
```bash
wget https://ftp.cpc.ncep.noaa.gov/wd51we/wgrib/wgrib.tar
mkdir wgrib
tar -xvf wgrib.tar -C wgrib
cd wgrib
make
sudo cp wgrib /usr/bin/
```

For [wgrib2](https://github.com/NOAA-EMC/wgrib2):
```bash
# We first need JasPer and the easiest way is from old repositories
sudo add-apt-repository "deb http://security.ubuntu.com/ubuntu xenial-security main"
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 3B4FE6ACC0B21F32
sudo apt update
sudo apt install libjasper1 libjasper-dev

cd ../
wget -O wgrib2.zip https://github.com/NOAA-EMC/wgrib2/archive/refs/tags/v2.0.8-cmake-v6.zip
unzip wgrib2.zip
cd wgrib2-2.0.8-cmake-v6/
mkdir build && cd build
cmake .. -DCMAKE_INSTALL_PREFIX=install
make
make install
cd install/bin/
sudo cp wgrib2 /usr/bin/
```

Clean everything:
```bash
cd ../../../../
rm wgrib.tar wgrib2.zip
rm apache-arrow-apt-* # Unless you want to keep the deb package
rm -R wgri* # Unless you wan want to keep the build directories

# If you want to remove wgrib and wgrib2 later, just do:
# sudo rm /usr/bin/wgri*
```

### R Packages:

```R
install.packages(c("flexdashboard", "lubridate", "DescTools", "spatstat.utils", "scales", "ggplot2", "TSrepr", "data.table", "cluster", "clusterCrit", "zoo", "RColorBrewer", "stringr", "reshape", "ggpubr", "gridExtra", "attempt", "dplyr", "viridis", "rNOMADS", "assertthat", "ini", "collapse", "ncdf4", "raster"), force=FALSE)
```

It might take a while. Do it again if anything wrong happened. The option `force=FALSE` ensures you won't reinstall everything.


## Set up (1)

### Data directory

Run the following commands:

```bash
mkdir data
cd data
mkdir cfs
mkdir fnmoc
mkdir gefs
mkdir gem
mkdir logs
```

## Set up (2): Profiles

### Config file

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
5 9 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/noaa_dl.sh "gefs" "00" "0"
5 15 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/noaa_dl.sh "gefs" "06" "0"
5 21 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/noaa_dl.sh "gefs" "12" "0"
5 3 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/noaa_dl.sh "gefs" "18" "1"
## GEM
10 9 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/noaa_dl.sh "gem" "00" "0"
10 21 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/noaa_dl.sh "gem" "12" "0"
## FNMOC
15 9 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/noaa_dl.sh "fnmoc" "00" "0"
15 2 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/noaa_dl.sh "fnmoc" "12" "1"
## CFS
20 14 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/noaa_dl.sh "cfs" "00" "0"
20 20 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/noaa_dl.sh "cfs" "06" "0"
20 2 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/noaa_dl.sh "cfs" "12" "1"
20 8 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/noaa_dl.sh "cfs" "18" "1"
## STATS
30 3 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/noaa_stats.sh "ens" "1" "Profile_1"
31 3 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/noaa_stats.sh "ens" "1" "Profile_2"
32 3 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/noaa_stats.sh "ens" "1" "Profile_3"
33 3 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/noaa_stats.sh "ens" "1" "Profile_4"
30 8 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/noaa_stats.sh "cfs" "1" "Profile_1"
31 8 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/noaa_stats.sh "cfs" "1" "Profile_2"
32 8 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/noaa_stats.sh "cfs" "1" "Profile_3"
33 8 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/noaa_stats.sh "cfs" "1" "Profile_4"
```

Two scripts can't run at the same time. A lock file prevents another script to start. It will wait until the lock is removed.

It is recommended to play with minutes to not start everything at the same time.

### Command args

```
./noaa_dl.sh [MODEL_NAME] [MODEL_RUN] [DAY_AGO]
```

`[MODEL_NAME]` is one of the 4 models considered previously : `gefs` `gem` `fnmoc` `cfs`.

`[MODEL_RUN]` is the run of the model (00Z, 12Z...) : `00` `06` `12` `18`. Leading zero is important. GEM and FNMOC only runs at 00Z and 12Z.

`[DAY_AGO]` is for the day of the run. If you want to download a run from 4 days ago, set `4`. If you download a run the same day it has been done, set `0`. If you download a run that was done the day before, it can be because it takes a while to be available or because you're in a different time zone, set `1`.

### Availability of runs

Availability is when forecast until h+360 is done for a run. This table with examples for 2 time zones will help you:

| **GEFS** | **Available in UTC time at** | **Available in tz Europe/Paris** | **Available in tz Hongkong** |
|---|---|---|---|
| 00Z       | 07:00                        | 09:00                            | 15:00                        |
| 06Z       | 13:00                        | 15:00                            | 21:00                        |
| 12Z       | 19:00                        | 21:00                            | 03:00 (day+1)                |
| 18Z       | 01:00 (day+1)                | 03:00 (day+1)                    | 09:00 (day+1)                |

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

