#!/bin/bash

C4MEM="0001"
CYCLE_DATE="20170101T00"

CYCLE_LETKF_SRCS="/discover/nobackup/cda/develop_space/cycle-oletkf"
SHARED_TMP_DIR="/discover/nobackup/cda/projects2/tmp_0d25"
EXP_DIR="/discover/nobackup/cda/projects2/odas3_0d25"
FCST_HRS=6
FWD_EXEC="/discover/nobackup/projects/gmao/scda_iesa/cda/GEOSgcm_08Nov2022/install/bin/GEOSgcm.x"

 echo "prep_geos_fcst ${C4MEM} $CYCLE_DATE"

 echo "${CYCLE_LETKF_SRCS}/prep_geos_fcst.py ${SHARED_TMP_DIR}/${CYCLE_DATE}_fcst${C4MEM} \
 --expTplDir ${CYCLE_LETKF_SRCS}/exp_template/exp_template_0d25deg  \
 --cycleBkgdDir ${EXP_DIR}/bkgd/${C4MEM}/${CYCLE_DATE} \
 --cycleAnalDir ${EXP_DIR}/anal/${C4MEM}/${CYCLE_DATE} \
 --fwdExec ${FWD_EXEC} \
 --fcstStartDate ${CYCLE_DATE} \
 --fcstHrs ${FCST_HRS}"


 ${CYCLE_LETKF_SRCS}/prep_geos_fcst.py ${SHARED_TMP_DIR}/${CYCLE_DATE}_fcst${C4MEM} \
 --expTplDir ${CYCLE_LETKF_SRCS}/exp_template/exp_template_0d25deg  \
 --cycleBkgdDir ${EXP_DIR}/bkgd/${C4MEM}/${CYCLE_DATE} \
 --cycleAnalDir ${EXP_DIR}/anal/${C4MEM}/${CYCLE_DATE} \
 --fwdExec ${FWD_EXEC} \
 --fcstStartDate ${CYCLE_DATE} \
 --fcstHrs ${FCST_HRS}


