#! /bin/bash

cd ../../


mv data/cfs/cfs-*_$1*.png vault/cfs
mv data/cfs/cfs-*_$1*.pdf vault/cfs
mv data/cfs/cfs-$1*.csv vault/cfs

mv data/gefs/ens_unif-$1*.png vault/gefs
mv data/gefs/ens_cluster_unif-$1*.pdf vault/gefs
mv data/gefs/gefs-$1*.csv vault/gefs

mv data/fnmoc/fnmoc-$1*.csv vault/fnmoc

mv data/gem/gem-$1*.csv vault/gem

mv data/ecmwf/ens_unif-$1*.pdf vault/ecmwf
mv data/ecmwf/ecmwf-$1*.csv vault/ecmwf

mv data/logs/$1*.csv vault/logs

