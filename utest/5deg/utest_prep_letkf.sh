#!/bin/bash

mem=3
wkdir="/discover/nobackup/cda/projects2/tmp/test_letkf_5deg_py"


#-------------------------------------------------------------------------------
# create_letkf_dir

./create_letkf_dir.py $wkdir


#-------------------------------------------------------------------------------
# prep_letkf

imem=1
while [ $imem -le $mem ]; do
c4mem=`printf "%4.4d" $imem`
./prep_letkf.py $wkdir \
--bkgdFile1 /discover/nobackup/cda/projects2/tmp/20170101T00_fcst${c4mem}/scratch/RESTART/MOM.res.nc \
--bkgdFile2 /discover/nobackup/cda/projects2/tmp/20170101T00_fcst${c4mem}/scratch/RESTART/MOM.res.nc \
--obsFile /discover/nobackup/cda/projects2/odas3/obsbkgd/${c4mem}/20170101T06/hx_sss.dat \
--member $imem
((imem+=1))
done

