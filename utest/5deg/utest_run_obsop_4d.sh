#!/bin/bash -xe

EXPDIR="/discover/nobackup/cda/projects2/test_obsop4d/tmp_4d"
x_obsop="/discover/nobackup/cda/develop_space/develop_ocean_letkf/Ocean-LETKF-v5/cbuild_esma/src/OCN.obsOp_mom6.sss.x"
rstFile="/discover/nobackup/cda/projects2/test_obsop4d/MOM.res.nc"
staticFile="/discover/nobackup/cda/projects2/test_obsop4d/scratch/ocean_static.nc"
topoFile="/discover/nobackup/cda/projects2/test_obsop4d/scratch/INPUT/ocean_topog_Edited.nc"
nmlFile="/discover/nobackup/cda/develop_space/cycle-oletkf/cylc/cpld_odas/etc/input.nml.obsop.5deg"
bkgdFile="/discover/nobackup/cda/projects2/test_obsop4d/scratch/ocean_hourly_%Y_%m_%d_%H.nc"
obsFile="/discover/nobackup/cda/projects2/test_obsop4d/obs4d/%Y%m%dT%H.sss.h5"
#bkgdFile="/discover/nobackup/cda/projects2/test_obsop4d/scratch/ocean_hourly_2017_01_01_06.nc"
#obsFile="/discover/nobackup/cda/projects2/test_obsop4d/obs4d/20170101T06.sss.h5"
hxFile="/discover/nobackup/cda/projects2/test_obsop4d/savedir/hx_sss.dat"
startDate="20170101T01"
endDate="20170101T06"
rinc="1"
otherArgs="-olevel 2"

echo "./run_obsop_4d.py ${EXPDIR} \
--obsopExec ${x_obsop} \
--rstFile   ${rstFile} \
--staticFile ${staticFile} \
--topoFile  ${topoFile} \
--nml       ${nmlFile} \
--bkgdFile  ${bkgdFile} \
--obsFile   ${obsFile} \
--hxFile    ${hxFile} \
--startDate ${startDate} \
--endDate   ${endDate} \
--rinc      ${rinc} \
--otherArgs ${otherArgs}
"

./run_obsop_4d.py ${EXPDIR} \
--obsopExec ${x_obsop} \
--rstFile   ${rstFile} \
--staticFile ${staticFile} \
--topoFile  ${topoFile} \
--nml       ${nmlFile} \
--bkgdFile  ${bkgdFile} \
--obsFile   ${obsFile} \
--hxFile    ${hxFile} \
--startDate ${startDate} \
--endDate   ${endDate} \
--rinc      ${rinc} \
--otherArgs "${otherArgs}"

