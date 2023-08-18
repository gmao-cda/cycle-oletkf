#!/bin/bash -xe

## test for L2 hdf5 SMAP SSS
#EXPDIR="/discover/nobackup/cda/projects2/test_obsop4d/tmp_4d"
#x_obsop="/discover/nobackup/cda/develop_space/develop_ocean_letkf/Ocean-LETKF-v5/cbuild_esma/src/OCN.obsOp_mom6.sss.x"
#rstFile="/discover/nobackup/cda/projects2/test_obsop4d/MOM.res.nc"
#staticFile="/discover/nobackup/cda/projects2/test_obsop4d/scratch/ocean_static.nc"
#topoFile="/discover/nobackup/cda/projects2/test_obsop4d/scratch/INPUT/ocean_topog_Edited.nc"
#nmlFile="/discover/nobackup/cda/develop_space/cycle-oletkf/cylc/cpld_odas/etc/input.nml.obsop.5deg"
#bkgdFile="/discover/nobackup/cda/projects2/test_obsop4d/scratch/ocean_hourly_%Y_%m_%d_%H.nc"
#obsFile="/discover/nobackup/cda/projects2/test_obsop4d/obs4d/%Y%m%dT%H.sss.h5"
#hxFile="/discover/nobackup/cda/projects2/test_obsop4d/savedir/hx_sss.dat"
#startDate="20170101T06"
#endDate="20170101T06"
#rinc="1"
#otherArgs="-olevel 2"

# test for binary VIIRS SST
EXPDIR="/discover/nobackup/cda/projects2/test_obsop4d/tmp_4d"
x_obsop="/discover/nobackup/cda/projects2/viirs_sst/Ocean-LETKF/cbuild/src/OCN.obsOp_mom6.sst_viirs.x"
rstFile="/discover/nobackup/cda/projects2/odas3_0d25_viirs_AtmM2_m20/anal/0001/20190901T06/RESTART/MOM.res.nc"
staticFile="/discover/nobackup/cda/projects2/tmp_0d25_m20/20190901T00_fcst0001/scratch/ocean_static.nc"
topoFile="/discover/nobackup/cda/projects2/tmp_0d25_m20/20190901T00_fcst0001/scratch/INPUT/ocean_topog.nc"
nmlFile="/discover/nobackup/cda/develop_space/cycle-oletkf/cylc/cpld_odas_0d25_viirs_AtmM2_m20/etc/input.nml.obsop.0d25deg"
bkgdFile="/discover/nobackup/cda/projects2/tmp_0d25_m20/20190901T00_fcst0001/scratch/ocean_hourly_%Y_%m_%d_%H.nc"
obsFile="/discover/nobackup/cda/projects2/test_obsop4d/obs4d_0d25_null/%Y%m%dT%H.sst.bin"
hxFile="/discover/nobackup/cda/projects2/test_obsop4d/savedir_0d25/hx_sst.dat"
startDate="20190901T01"
endDate="20190901T06"
rinc="1"
otherArgs="-binary T"



echo "./run_obsop_4d.py ${EXPDIR} \
--obsopExec ${x_obsop} \
--rstFile   ${rstFile} \
--staticFile ${staticFile} \
--topoFile  ${topoFile} \
--nml       ${nmlFile} \
--bkgdFileTpl  ${bkgdFile} \
--obsFileTpl   ${obsFile} \
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
--bkgdFileTpl  ${bkgdFile} \
--obsFileTpl   ${obsFile} \
--hxFile    ${hxFile} \
--startDate ${startDate} \
--endDate   ${endDate} \
--rinc      ${rinc} \
--otherArgs "${otherArgs}"

