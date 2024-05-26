# Gribs-Analysis

**Version 24.05**

> This program is designed to work on Linux, on a server.
>
> You need Python and Cron.


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

It might take a while. Do it again if anything wrong happened. The option `force=FALSE` ensures you won't reinstall packages already set and compiled.


## Set up

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

### Profiles

### Crontab

Install locally for a specific user

Make a crontab !
Run for a specific user (same as the one who installed R libs)



