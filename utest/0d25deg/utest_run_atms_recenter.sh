#!/bin/bash
#SBATCH -N 1
#SBATCH --ntasks=3
#SBATCH --qos=debug
#SBATCH --time=10:00
#SBATCH --account=s2647


cd /discover/nobackup/cda/projects2/dev_recenter

module use -a /home/mathomp4/modulefiles-SLES12
module load python/ChengpyD/3.10
ml

wkdir="./tmp"
MEMBERS=3
NPROCS=3
RECENTER_EXEC_DIR="/discover/nobackup/cda/develop_space/GEOSFV3-LETKF/build_discover/utils"
CYCLE_LETKF_SRCS="/discover/nobackup/cda/develop_space/cycle-oletkf"
CENTER_DIR="/discover/nobackup/cda/projects2/atms_recenter_m3/center/20190921T21"

#cmd="
PYTHONPATH=${CYCLE_LETKF_SRCS} ${CYCLE_LETKF_SRCS}/run_atms_recenter.py ${wkdir} \
 --cntrDir        ${CENTER_DIR} \
 --ensize         ${MEMBERS} \
 --recenterExec   ${RECENTER_EXEC_DIR}/recenter.x \
 --nprocs         ${NPROCS} \
 --bkgdPrefixTpl  'bkgd{:04d}' \
 --analPrefixTpl  'anal{:04d}' \
 --cntrPrefix     'center' \
 --meanPrefix     'bkgdmean' \
 --sprdPrefix     'bkgdsprd' \
 --otherArgs      '-wrtmean T -wrtsprd T -clipq T -vt T'
# "
#echo $cmd 
#$cmd
