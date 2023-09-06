

if [ 0 -le 1 ]; then
mkdir -p tmpdir2/anal
mkdir -p tmpdir2/bkgd/RESTART
touch tmpdir2/bkgd/RESTART/MOM.res.nc
echo "MOM6" > tmpdir2/bkgd/RESTART/MOM.res.nc

touch tmpdir2/anal/fvcore_internal_rst
touch tmpdir2/anal/moist_internal_rst
touch tmpdir2/anal/surf_import_rst

echo "fvcore" > tmpdir2/anal/fvcore_internal_rst
echo "moist" > tmpdir2/anal/moist_internal_rst
echo "surf" > tmpdir2/anal/surf_import_rst
fi

BKGD_DIR="tmpdir2/bkgd"
ANAL_DIR="tmpdir2/anal"
CYCLE_LETKF_SRCS="/discover/nobackup/cda/develop_space/cycle-oletkf"

cmd="
${CYCLE_LETKF_SRCS}/reconcile_atms_recenter_mem.py \
--bkgdDir ${BKGD_DIR} \
--analDir ${ANAL_DIR} \
${SKIP_OPT_RECONCILE_RECENTER_MEM}
"
echo $cmd
$cmd
