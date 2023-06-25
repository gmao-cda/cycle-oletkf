#!/bin/bash

wkdir="/discover/nobackup/cda/projects2/tmp/test_letkf_5deg_py"
geos_fcst_dir="/discover/nobackup/cda/projects2/tmp/20170101T00_fcst0001"
nml_dir="/discover/nobackup/cda/develop_space/cycle-oletkf/cylc/cpld_odas/etc"
oletkf_exec_dir="/discover/nobackup/cda/develop_space/develop_ocean_letkf/Ocean-LETKF-v5/cbuild_esma/src/"

PYTHONPATH=/discover/nobackup/cda/develop_space/cycle-oletkf ./run_letkf.py ${wkdir} \
--ensize 3 \
--letkfExec ${oletkf_exec_dir}/OCN.letkf_mom6.x \
--nprocs 10 \
--rstFile    ${geos_fcst_dir}/scratch/RESTART/MOM.res.nc \
--staticFile ${geos_fcst_dir}/scratch/ocean_static.nc \
--topoFile   ${geos_fcst_dir}/scratch/INPUT/ocean_topog_Edited.nc \
--nml ${nml_dir}/input.nml.letkf.5deg \
--bkgdFile1Tpl gs01#MEMBER#.MOM.res.nc \
--bkgdFile2Tpl gs01#MEMBER#.MOM.res.nc \
--analFile1Tpl anal#MEMBER#.MOM.res.nc \
--analFile2Tpl anal#MEMBER#.MOM.res.nc \
--obsFileTpl obs01#MEMBER#.dat \
--strLength 3
