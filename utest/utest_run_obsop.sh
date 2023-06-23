#!/bin/bash -xe

./run_obsop.py /discover/nobackup/cda/projects2/tmp/test_obsop_5deg_py \
--obsopExec /discover/nobackup/cda/develop_space/develop_ocean_letkf/Ocean-LETKF-v5/cbuild_esma/src/OCN.obsOp_mom6.sss.x \
--rstFile  /discover/nobackup/cda/projects2/tmp/20170101T00_fcst0002/scratch/RESTART/MOM.res.nc \
--staticFile /discover/nobackup/cda/projects2/tmp/20170101T00_fcst0002/scratch/ocean_static.nc \
--topoFile  /discover/nobackup/cda/projects2/tmp/20170101T00_fcst0002/scratch/INPUT/ocean_topog_Edited.nc \
--nml   /discover/nobackup/cda/develop_space/cycle-oletkf/cylc/cpld_odas/etc/input.nml.5deg \
--bkgdFile  /discover/nobackup/cda/projects2/tmp/20170101T00_fcst0002/scratch/ocean_hourly_2017_01_01_06.nc \
--obsFile   /discover/nobackup/cda/projects2/tmp/test_obsop_5deg/SMAP_L2B_SSS_36950_20220101T005200_R18240_V5.0.h5 \
--hxFile   /discover/nobackup/cda/projects2/tmp/test_obsop_5deg_py/hx_sss.dat \
--otherArgs "-olevel 2"

