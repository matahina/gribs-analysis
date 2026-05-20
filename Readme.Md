# Gribs-Analysis

**26.05 RC2**

> [!NOTE] 
> This program is designed to work on Linux, on a server.
>
> You need Python, Bash, R and Cron.
>
> It is currently known working on a VPS running Debian 13 with 4 CPU cores, 8GB RAM and 100GB disk space reserved for `data` directory.
>
> wgrib use is now questionnable as python-xarray with cfgrib works fine ; norms only need netcdf

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
| [Metz](https://matahina.ovh/weather/ens_dashboard_Profile_1.html)              |  [Metz](https://matahina.ovh/weather/cfs_dashboard_Profile_1.html)            |
| [Abidjan](https://matahina.ovh/weather/ens_dashboard_Profile_2.html)           |  [Abidjan](https://matahina.ovh/weather/cfs_dashboard_Profile_2.html)         |
| [Johannesburg](https://matahina.ovh/weather/ens_dashboard_Profile_3.html)      |  [Johannesburg](https://matahina.ovh/weather/cfs_dashboard_Profile_3.html)    |
| [Cape Town](https://matahina.ovh/weather/ens_dashboard_Profile_4.html)         |  [Cape Town](https://matahina.ovh/weather/cfs_dashboard_Profile_4.html)       |


## Requirements (Distro packages)

### Arch-based

cfgrib (venv) and xarray (package)

```bash
sudo pacman -S yay base-devel r gdal pandoc
```

```bash
yay -S wgrib wgrib2 udunits
```


### Debian 13

```bash
sudo apt install libudunits2-dev cmake libssl-dev build-essential python3-venv pandoc libuv1-dev r-base curl libgdal-dev python3-xarray python3-cfgrib
```

<details>

<summary>wgrib2 via spack</summary>

**ECMWF gribs cannot be read with the binary shipped by spack (ERROR 42).**


```bash
cd gribs-analysis

git clone --depth=2 https://github.com/spack/spack.git

# For bash/zsh/sh
. spack/share/spack/setup-env.sh

# For tcsh/csh
source spack/share/spack/setup-env.csh

# For fish
. spack/share/spack/setup-env.fish

# not working with ecmwf, even with uncommented variant
spack install g2c +aec +png wgrib2 +aec +png +g2c_low #+netcdf
```

</details>

<details>

<summary>wgrib2 compiled locally</summary>

```bash
wget -O ip.zip `curl https://api.github.com/repos/NOAA-EMC/NCEPLIBS-ip/releases | python3 -c "import sys, json; print(json.load(sys.stdin)[0]['zipball_url'])"`
unzip ip.zip
mv NOAA-EMC-NCEPLIBS-ip* NCEPLIBS-ip
rm ip.zip
cmake -DCMAKE_INSTALL_PREFIX="~/.local" -S NCEPLIBS-ip -B NCEPLIBS-ip/build
#cmake -DCMAKE_INSTALL_PREFIX="~/.local" -DCMAKE_Fortran_FLAGS="-march=native -mtune=native -O3 -pipe -fno-plt -Wp,-D_FORTIFY_SOURCE=3 -fstack-clash-protection -fcf-protection -fno-omit-frame-pointer -mno-omit-leaf-frame-pointer" -S NCEPLIBS-ip -B NCEPLIBS-ip/build
cmake --build NCEPLIBS-ip/build --parallel 4
ctest --test-dir NCEPLIBS-ip/build --parallel 4
cmake --install NCEPLIBS-ip/build
rm -R NCEPLIBS-ip

wget -O g2c.zip `curl https://api.github.com/repos/NOAA-EMC/NCEPLIBS-g2c/releases | python3 -c "import sys, json; print(json.load(sys.stdin)[0]['zipball_url'])"`
unzip g2c.zip
mv NOAA-EMC-NCEPLIBS-g2c* NCEPLIBS-g2c
rm g2c.zip
cmake -DUSE_PNG=ON -DUSE_AEC=ON -DUSE_OpenJPEG=ON -DUSE_Jasper=OFF -DCMAKE_INSTALL_PREFIX="~/.local" -S NCEPLIBS-g2c -B NCEPLIBS-g2c/build
# cmake -DCMAKE_C_FLAGS="-march=native -mtune=native -O3 -pipe -fno-plt -fexceptions -Wp,-D_FORTIFY_SOURCE=3 -Wformat -Werror=format-security -fstack-clash-protection -fcf-protection -fno-omit-frame-pointer -mno-omit-leaf-frame-pointer" -DUSE_PNG=ON -DUSE_AEC=ON -DUSE_OpenJPEG=ON -DUSE_Jasper=OFF -DCMAKE_INSTALL_PREFIX="~/.local" -S NCEPLIBS-g2c -B NCEPLIBS-g2c/build
cmake --build NCEPLIBS-g2c/build --parallel 4
ctest --test-dir NCEPLIBS-g2c/build --parallel 4
cmake --install NCEPLIBS-g2c/build
rm -R NCEPLIBS-g2c

wget -O wgrib2.zip `curl https://api.github.com/repos/NOAA-EMC/wgrib2/releases | python3 -c "import sys, json; print(json.load(sys.stdin)[0]['zipball_url'])"`
unzip wgrib2.zip
mv NOAA-EMC-wgrib2* wgrib2
rm wgrib2.zip
cd wgrib2/
mkdir build && cd build
cmake .. -DCMAKE_PREFIX_PATH="~/.local/lib" -DUSE_NETCDF=ON -DUSE_IPOLATES=ON -DUSE_G2CLIB_HIGH=on -DUSE_G2CLIB_LOW=on -DCMAKE_INSTALL_PREFIX="~/.local"
# cmake .. -DCMAKE_PREFIX_PATH="~/.local/lib" -DCMAKE_Fortran_FLAGS="-march=native -mtune=native -O3 -pipe -fno-plt -Wp,-D_FORTIFY_SOURCE=3 -fstack-clash-protection -fcf-protection -fno-omit-frame-pointer -mno-omit-leaf-frame-pointer" -DUSE_NETCDF=ON -DUSE_IPOLATES=ON -DCMAKE_C_FLAGS="-march=native -mtune=native -O3 -pipe -fno-plt -fexceptions -Wp,-D_FORTIFY_SOURCE=3 -Wformat -Werror=format-security -fstack-clash-protection -fcf-protection -fno-omit-frame-pointer -mno-omit-leaf-frame-pointer" -DUSE_G2CLIB_HIGH=on -DUSE_G2CLIB_LOW=on -DCMAKE_INSTALL_PREFIX="~/.local"
make
make install
cd ../../
rm -R wgrib2

## bash
echo "export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:~/.local/lib/" >> ~/.bashrc
echo "export PATH=$PATH:~/.local/bin/" >> ~/.bashrc
echo "LD_LIBRARY_PATH=$LD_LIBRARY_PATH:~/.local/lib/" >> ~/.profile
echo "PATH=$PATH:~/.local/bin/" >> ~/.profile

## fish
# fish_add_path ~/.local/bin
# set -Ux LD_LIBRARY_PATH ~/.local/lib/
# echo "LD_LIBRARY_PATH=$LD_LIBRARY_PATH:~/.local/lib/" >> ~/.profile
# echo "PATH=$PATH:~/.local/bin/" >> ~/.profile
```


</details>




## Requirements (R packages)

### All distros

```R
required.packages <- c("flexdashboard", "lubridate", "DescTools", "spatstat.utils", "scales", "ggplot2", "TSrepr", "data.table", "cluster", "clusterCrit", "zoo", "RColorBrewer", "stringr", "reshape", "ggpubr", "gridExtra", "attempt", "dplyr", "viridis", "assertthat", "ini", "collapse", "ncdf4", "raster", "rvest", "fields", "GEOmap", "MBA", "XML", "uuid")
new.packages <- required.packages[!(required.packages %in% installed.packages()[,"Package"])]
if(length(new.packages)) install.packages(new.packages)
```

It might take a while. **Do it again if anything wrong happened.** Then:

```R
install.packages("http://cran.r-project.org/src/contrib/Archive/rNOMADS/rNOMADS_2.5.3.tar.gz",
                 repos=NULL, method="libcurl")
```

## Set up

```bash
cd gribs-analysis
# Stay inside directory
```

### Set up python3 virtual env

```bash
python3 -m venv ecmwf_env
source ecmwf_env/bin/activate
pip install ecmwf-opendata
deactivate
```

### Set up data directory

```bash
mkdir publishery
mkdir data
cd data
mkdir cfs
mkdir fnmoc
mkdir gefs
mkdir gem
mkdir logs
mkdir ecmwf
cd ../scripts/dl
echo "FREE" > lock.txt
```

### Config file

You can run this program for different locations. Grib files are downloaded according to a subset area for each location based on given coordinates.

Edit the file `magic_config.ini`. The original one is explicit enough to understand it. You can remove profiles, add some, or leave only one. Choose the cities you want and fill it with the appropriate values. If you set `use_it = no`, data from this location won't be downloaded nor extracted.

If you have more than 2 profiles, you must set `area = yes` in *\[General\]* section. Otherwise, you can set in to `area = no`.

When the setting `area = yes` in enabled, it tells the scripts to download one grib of this subset area instead of several gribs from different locations. NOAA might block your IP if you download too many grib files at the same time.

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

- `[ARG5]` is either `noaa` or `ecmwf`, and will run and/or queue noaa_dl.sh or noaa_stats.sh with their own args, see below.


**noaa_dl.sh**

*For downloading runs from NOAA models.*

```
./noaa_dl.sh [MODEL_NAME] [MODEL_RUN] [DATE]
```

- `[MODEL_NAME]` is one of the 4 models considered previously : `gefs` `gem` `fnmoc` `cfs`.

- `[MODEL_RUN]` is the run of the model (00Z, 12Z...) : `00` `06` `12` `18`. Leading zero is important. GEM and FNMOC only runs at 00Z and 12Z.

- `[DATE]` is for the date of the run. You need to put a date, either today or another day before (for catching an older run by example), in this format: `YYYYMMDD`.


**ecmwf_dl.sh**

*For downloading runs from ECMWF models.*

```
./ecmwf_dl.sh [MODEL_NAME] [MODEL_RUN] [DATE]
```

- `[MODEL_NAME]` has one choice at the moment : `ecmwf`.

- `[MODEL_RUN]` is the run of the model (00Z, 12Z...) : `00` `12`. Leading zero is important. ECMWF runs from 06Z and 18Z aren't working with this script at the moment.

- `[DATE]` is for the date of the run. You need to put a date, either today or another day before (for catching an older run by example), in this format: `YYYYMMDD`.


**noaa_stats.sh**

*For generating dashboards. Whatever data is from NOAA or ECMWF.*

```
./noaa_stats.sh [SET] [PROFILE] [DATE]
```

- `[SET]` is either `ens` (gem+gefs+fnmoc) or `cfs`. It will cover all runs from the specificied DATE.

- `[PROFILE]` is one of the profiles you set in ini file, by example `Profile_1`.

- `[DATE]` is for the date of the set. You need to put a date, either today or another day before (for catching an older set by example), in this format: `YYYYMMDD`.


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

