#!/bin/bash

C4MEM="0001"
CYCLE_DATE="20170101T00"
NEXT_CYCLE_DATE="20170101T06"

CYCLE_LETKF_SRCS="/discover/nobackup/cda/develop_space/cycle-oletkf"
SHARED_TMP_DIR="/discover/nobackup/cda/projects2/tmp_0d25"
EXP_DIR="/discover/nobackup/cda/projects2/odas3_0d25"
FCST_HRS=6
FWD_EXEC="/discover/nobackup/projects/gmao/scda_iesa/cda/GEOSgcm_08Nov2022/install/bin/GEOSgcm.x"
SITE="NCCS"
GEOS_DIR="/discover/nobackup/projects/gmao/scda_iesa/cda/GEOSgcm_08Nov2022/install"

 echo "PYTHONPATH=${CYCLE_LETKF_SRCS} ${CYCLE_LETKF_SRCS}/gcm_run_lib_v2.py ${SHARED_TMP_DIR}/${CYCLE_DATE}_fcst${C4MEM} \
 --flowDir ${CYCLE_LETKF_SRCS} \
 --geosDir ${GEOS_DIR} \
 --site ${SITE} \
 --ncpus 1215 \
 --ncpusPerNode 45 \
 --bkgdSaveDir ${EXP_DIR}/bkgd/${C4MEM}/${NEXT_CYCLE_DATE}"

