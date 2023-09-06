
wkdir="./tmp"
MEAN_DIR="save/mean"
SPRD_DIR="save/sprd"
CYCLE_LETKF_SRCS="/discover/nobackup/cda/develop_space/cycle-oletkf"

cmd="
${CYCLE_LETKF_SRCS}/save_atms_recenter_diag.py ${wkdir} \
 --meanDir ${MEAN_DIR}
 --sprdDir ${SPRD_DIR}
 --meanPrefix     "bkgdmean" \
 --sprdPrefix     "bkgdsprd" \
"
echo $cmd 
$cmd
