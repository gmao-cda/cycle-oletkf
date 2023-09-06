
mkdir -p tmpdir/recenter
mkdir -p tmpdir/fcst0001
mkdir -p tmpdir/fcst0002
mkdir -p tmpdir/fcst0003
mkdir -p tmpdir/fcst0004

RECENTER_DIR="tmpdir/recenter"
FCST_DIR="tmpdir/fcst{:04d}"
CYCLE_LETKF_SRCS="/discover/nobackup/cda/develop_space/cycle-oletkf"
nbv=3

#echo "
${CYCLE_LETKF_SRCS}/clean_atms_recenter_tmpdir.py \
    --recenterDir ${RECENTER_DIR} \
    --fcstDirTpl ${FCST_DIR} \
    --ensize ${nbv} \
    --no-skip
#"
