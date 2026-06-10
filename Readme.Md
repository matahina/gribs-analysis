# Gribs-Analysis

**26.06**

> [!NOTE] 
> This program is designed to work on Linux, on a server.
>
> You need Python, Bash, R and Cron.
>
> It is currently known working on a VPS running Debian 13 with 4 CPU cores, 8GB RAM and 100GB disk space reserved for `data` directory.
>


## What it does

It retrieves grib files from different weather prediction models from NOAA, CMC and ECMWF (GEFS, AIGEFS, CFS; GEM; IFS, AIFS).

GEFS, IFS, their AI-based implementations and GEM are ensemblist models. The different scenarios are downloaded, except deterministic and control runs. Data is extracted into csv files. Then grib files are deleted.

CFS is long-term model. Time grib data is downloaded. Grib files from the last 5 days only kept stored.

For ensemblist models, a dashboard is computed with basic time series clustering of the scenarios from the previous day forecasts (up to xxx scenarios).

For long-term model, a dashboard is computed with probabilities to see above/below long-term means for different variables from the previous forecasts of the 28 last days.

Only few parameters are analyzed: geopotential (z500), temperature (t850 and t2m), precipitations (ACPC or PRATE).

It also uses data from [NCEP Reanalysis](https://psl.noaa.gov/data/gridded/data.ncep.reanalysis2.html) to compare with long-term data means.

Both downloads and dashboard generation are logged for error-catching purposes.

When everything is set up and running, generated dashboards are available in `publishery` directory. Some dashboard examples are available online :

| **Ensemblists**          | **Long-Term**            |
|---|---|
| [Metz](https://matahina.ovh/weather/ens_dashboard_Profile_1.html)              |  [Metz](https://matahina.ovh/weather/cfs_dashboard_Profile_1.html)            |
| [Abidjan](https://matahina.ovh/weather/ens_dashboard_Profile_2.html)           |  [Abidjan](https://matahina.ovh/weather/cfs_dashboard_Profile_2.html)         |
| [Johannesburg](https://matahina.ovh/weather/ens_dashboard_Profile_3.html)      |  [Johannesburg](https://matahina.ovh/weather/cfs_dashboard_Profile_3.html)    |
| [Cape Town](https://matahina.ovh/weather/ens_dashboard_Profile_4.html)         |  [Cape Town](https://matahina.ovh/weather/cfs_dashboard_Profile_4.html)       |


## Requirements (Distro packages)

### Arch-based

```bash
sudo pacman -S yay base-devel r gdal pandoc python-xarray
```

```bash
yay -S wgrib wgrib2 udunits
```


### Debian 13

```bash
sudo apt install libudunits2-dev cmake libssl-dev build-essential python3-venv pandoc libuv1-dev r-base curl libgdal-dev python3-xarray python3-cfgrib
```

## Requirements (R packages)

### All distros

```R
required.packages <- c("flexdashboard", "lubridate", "DescTools", "spatstat.utils", "scales", "ggplot2", "TSrepr", "data.table", "cluster", "clusterCrit", "zoo", "RColorBrewer", "stringr", "reshape", "ggpubr", "gridExtra", "attempt", "dplyr", "viridis", "assertthat", "ini", "collapse", "ncdf4", "raster", "rvest", "fields", "GEOmap", "MBA", "XML", "uuid")
new.packages <- required.packages[!(required.packages %in% installed.packages()[,"Package"])]
if(length(new.packages)) install.packages(new.packages)
```

It might take a while. **Do it again if anything wrong happened.** Then:


## Set up

```bash
cd gribs-analysis
# Stay inside directory
```

### Set up python3 virtual env

```bash
python3 -m venv py_env --system-site-packages
source py_env/bin/activate
pip install ecmwf-opendata
deactivate

### For arch users only
source py_env/bin/activate
pip install cfgrib
python -m cfgrib selfcheck
# Check output:
## Found: ecCodes v2.20.0.
## Your system is ready.
deactivate
```

### Set up data directory

```bash
mkdir publishery
mkdir data
cd data
mkdir aifs
mkdir aigefs
mkdir cfs
mkdir gefs
mkdir gem
mkdir ifs
mkdir logs
cd ../scripts/dl
echo "FREE" > lock.txt
```

### Config file

You can run this program for different locations. Grib files are downloaded according to a subset area for each location based on given coordinates.

Edit the file `magic_config.ini`. The original one is explicit enough to understand it. You can remove profiles, add some, or leave only one. Choose the cities you want and fill it with the appropriate values. If you set `use_it = no`, data from this location won't be downloaded nor extracted.


### Get NCEP reanalysis long-term data means

Check if [NOAA service](https://psl.noaa.gov/thredds/catalog.html) is available before... Then run:

```bash
./scripts/dl/norms_dl.sh "Profile_1"
```

Repeat for each profile. Change the profile name given as argument according to the names in `magic_config.ini`.

### Crontab

The same user who runs this program and did install R packages will edit crontab with `crontab -e`.

<details>

<summary>Example for a server in Europe/Paris tz zone</summary>

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
10 9 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/gribs_launch.sh "gem" "00" "0" "dl" "cmc"
10 21 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/gribs_launch.sh "gem" "12" "0" "dl" "cmc"
## FNMOC
15 9 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/gribs_launch.sh "fnmoc" "00" "0" "dl" "noaa"
15 2 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/gribs_launch.sh "fnmoc" "12" "1" "dl" "noaa"
## CFS
20 14 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/gribs_launch.sh "cfs" "00" "0" "dl" "noaa"
20 20 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/gribs_launch.sh "cfs" "06" "0" "dl" "noaa"
20 2 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/gribs_launch.sh "cfs" "12" "1" "dl" "noaa"
20 8 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/gribs_launch.sh "cfs" "18" "1" "dl" "noaa"
## STATS
30 3 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/gribs_launch.sh "ens" "Profile_1" "1" "stats" "noaa"
31 3 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/gribs_launch.sh "ens" "Profile_2" "1" "stats" "noaa"
32 3 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/gribs_launch.sh "ens" "Profile_3" "1" "stats" "noaa"
33 3 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/gribs_launch.sh "ens" "Profile_4" "1" "stats" "noaa"
30 8 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/gribs_launch.sh "cfs" "Profile_1" "1" "stats" "noaa"
31 8 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/gribs_launch.sh "cfs" "Profile_2" "1" "stats" "noaa"
32 8 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/gribs_launch.sh "cfs" "Profile_3" "1" "stats" "noaa"
33 8 * * * [YOUR PATH!!]/gribs-analysis/scripts/dl/gribs_launch.sh "cfs" "Profile_4" "1" "stats" "noaa"
```

</details>

Two scripts can't run at the same time. Calling `gribs_launch.sh` prevents another script from start by being queued.

See below for explanations about scripts to put in crontab and when data is available.

### Bonus files

You can create two other files to fit your needs:

- `[YOUR PATH!!]/gribs-analysis/scripts/libs/notify_ssh.sh` If it exists, it will be called when `noaa_dl.sh` and `noaa_stats.sh` start and end. By example, to send via ssh a notify-osd message to your computer to see your server is running this program.

- `[YOUR PATH!!]/gribs-analysis/scripts/libs/publish_dashboards.sh` If it exists, it will be called when `noaa_stats.sh` ends. By example, to move your dashboard in */var/www/* if your server is also hosting a website (or to move them via ssh-ftp to another server).

## Understanding of scripts and data sources

### Main scripts and args

**gribs_launch.sh**

*A wrapper for main scripts `noaa_dl.sh`, `ecmwf_dl` and `noaa_stats.sh`. It will then launch `[ARG_5]_[ARG_4].sh`*

```
./gribs_launch.sh [ARG1] [ARG2] [ARG3] [ARG4] [ARG5]
```

- `[ARG1]` depends on ARG4 and ARG5, it will input the same args as `[ARG_5]_[ARG_4].sh`

- `[ARG2]` depends on ARG4 and ARG5, it will input the same args as `[ARG_5]_[ARG_4].sh`

- `[ARG3]` is for the day of either run (for downloading), or set of runs (for stats dashboard). Just use an integer: `0` for today, `1` for the day before, etc.

- `[ARG4]` is either `dl` or `stats`, and will run and/or queue noaa_dl.sh or noaa_stats.sh with their own args, see below.

- `[ARG5]` is either `noaa`, `cmc` or `ecmwf`, and will run and/or queue noaa_dl.sh, cmc_dl.sh or noaa_stats.sh or with their own args, see below.


**noaa_dl.sh**

*For downloading runs from NOAA models.*

```
./noaa_dl.sh [MODEL_NAME] [MODEL_RUN] [DATE]
```

- `[MODEL_NAME]` is one of the 4 models considered previously : `gefs` `gem` `fnmoc` `cfs`.

- `[MODEL_RUN]` is the run of the model (00Z, 12Z...) : `00` `06` `12` `18`. Leading zero is important. FNMOC only runs at 00Z and 12Z.

- `[DATE]` is for the date of the run. You need to put a date, either today or another day before (for catching an older run by example), in this format: `YYYYMMDD`.


**cmc_dl.sh**

*For downloading runs from CMC models.*

```
./cmc_dl.sh [MODEL_NAME] [MODEL_RUN] [DATE]
```

- `[MODEL_NAME]` has one choice at the moment : `gem`.

- `[MODEL_RUN]` is the run of the model (00Z, 12Z...) : `00` `12`. Leading zero is important. GEM only runs at 00Z and 12Z.

- `[DATE]` is for the date of the run. You need to put a date, either today or another day before (for catching an older run by example), in this format: `YYYYMMDD`.


**ecmwf_dl.sh**

*For downloading runs from ECMWF models.*

```
./ecmwf_dl.sh [MODEL_NAME] [MODEL_RUN] [DATE]
```

- `[MODEL_NAME]` has one choice at the moment : `ecmwf`.

- `[MODEL_RUN]` is the run of the model (00Z, 12Z...) : `00` `12`. Leading zero is important. ECMWF runs at 06Z and 18Z aren't working with this script at the moment.

- `[DATE]` is for the date of the run. You need to put a date, either today or another day before (for catching an older run by example), in this format: `YYYYMMDD`.


**noaa_stats.sh**

*For generating dashboards. Whatever data is from NOAA or ECMWF.*

```
./noaa_stats.sh [SET] [PROFILE] [DATE]
```

- `[SET]` is either `ens` (gem+gefs+fnmoc+ecmwf) or `cfs`. It will cover all runs from the specificied DATE.

- `[PROFILE]` is one of the profiles you set in ini file, by example `Profile_1`.

- `[DATE]` is for the date of the set. You need to put a date, either today or another day before (for catching an older set by example), in this format: `YYYYMMDD`.


**storage_vault.sh**

*Move old data from `data` to `vault`.*

```
./storage_vault.sh [YEAR]
```

- `[YEAR]` as `2025`, `2024`, etc.


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


## License
This bunch of crap code lines is GPL, free, public domain, have fun with it!!!

## Project status
Active.

