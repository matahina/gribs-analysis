## R

```bash
sudo pacman -S r gcc-fortran gdal pandoc-cli python-urllib3 python-requests arrow netcdf

yay -S --aur wgrib wgrib2
```

```R
install.packages(c("flexdashboard", "lubridate", "DescTools", "spatstat.utils", "scales", "ggplot2", "TSrepr", "data.table", "cluster", "clusterCrit", "zoo", "RColorBrewer", "stringr", "reshape", "ggpubr", "gridExtra", "attempt", "dplyr", "viridis", "rNOMADS", "assertthat", "ini", "collapse", "ncdf4", "raster"))
```

Install locally for a specific user

## Bash

Use bash not zsh

## Python3

## CURL

## Wget

## Crontab

Make a crontab !
Run for a specific user (same as the one who installed R libs)

## Torsocks

```bash
sudo pacman -S torsocks
sudo systemctl enable tor.service
sudo systemctl start tor.service
```

## MKDIR DATA

```bash
mkdir data
cd data
mkdir cfs
mkdir fnmoc
mkdir gefs
mkdir gem
mkdir logs
```
