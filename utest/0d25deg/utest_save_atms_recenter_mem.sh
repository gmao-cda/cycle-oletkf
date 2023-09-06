
RECENTER_DIR="tmp/"
CYCLE_LETKF_SRCS="/discover/nobackup/cda/develop_space/cycle-oletkf"
nbv=3

ibv=1
while [ $ibv -le $nbv ]; do
    cibv=$(printf "%4.4d" $ibv)
    ANAL_DIR="save/anal/$cibv"
    cmd="
    ${CYCLE_LETKF_SRCS}/save_atms_recenter_mem.py ${RECENTER_DIR} \
    --saveDir ${ANAL_DIR} \
    --member ${ibv} \
    --analPrefixTpl "anal{:04d}"
    "
    echo $cmd 
    $cmd

    ((ibv+=1))

done
