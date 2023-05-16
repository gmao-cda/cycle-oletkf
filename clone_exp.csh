#!/bin/tcsh -f


set CLONEDIR = "/discover/nobackup/cda/projects/5deg_can"
set EXPID = "new_deg5_v3"
set EXPDSC = "describe_new_5deg"
#where gcm_setup is (including gcm_setup)
set GCMSETUP = "/discover/nobackup/projects/gmao/scda_iesa/cda/GEOSgcm_08Nov2022/install/bin/gcm_setup"



set BINDIR   = `dirname $GCMSETUP`
set GEOSDEF  = `dirname $BINDIR`


echo "GCMSETUP=$GCMSETUP"
echo "BINDIR=$BINDIR"
echo "GEOSDEF=$GEOSDEF"

#exit 


# ------------------------------------------------------
# Below work
#
OLDEXP:

if ( $CLONEDIR == "") then
   goto OLDEXP
else if ( ! -d $CLONEDIR ) then
   echo
   echo "Could not find ${CLONEDIR}"
   goto OLDEXP
endif

# ------------------------------------------------------
# To setup the clone, we need to look in a couple files,
# so make sure they are readable
# ------------------------------------------------------

if ( ! -r $CLONEDIR/gcm_run.j ) then
   echo
   echo "$CLONEDIR/gcm_run.j is not readable. Please check permissions."
   exit 1
endif

if ( ! -r $CLONEDIR/HISTORY.rc ) then
   echo
   echo "$CLONEDIR/HISTORY.rc is not readable. Please check permissions."
   exit 1
endif

# -----------------------------------------
# Grab the old EXPID, and other information
# -----------------------------------------

set  OLDEXPID=`awk '/^EXPID/ {print $2}' $CLONEDIR/HISTORY.rc`
set OLDHOMDIR=`awk '/^setenv +HOMDIR/ {print $3}' $CLONEDIR/gcm_run.j`
set OLDEXPDIR=`awk '/^setenv +EXPDIR/ {print $3}' $CLONEDIR/gcm_run.j`
set   OLDUSER=`/bin/ls -l $CLONEDIR/gcm_run.j | awk '{print $3}'`

setenv ARCH      `uname`
setenv GEOSDIR  /`grep "setenv GEOSDIR" $CLONEDIR/gcm_run.j | cut -d'/' -f2-`
setenv GEOSSRC  ${GEOSDIR}
setenv GEOSBIN  ${GEOSDIR}/bin
setenv GEOSETC  ${GEOSDIR}/etc
setenv GEOSUTIL ${GEOSDIR}
setenv GCMVER   `cat ${GEOSETC}/.AGCM_VERSION`

echo "CDA: GEOSDIR=$GEOSDIR" # CDA

# -------------------------------------------------
# Figure out how this person usually runs the model
# -------------------------------------------------

if ( ! -e $HOME/.HOMDIRroot || ! -e $HOME/.EXPDIRroot ) then
   if ( -e $HOME/.HOMDIRroot && ! -e $HOME/.EXPDIRroot ) then
      echo "$HOME/.EXPDIRroot was not found."
      echo "Please run gcm_setup in non-clone mode at least once to use this script."
      exit 1
   else if ( ! -e $HOME/.HOMDIRroot && -e $HOME/.EXPDIRroot ) then
      echo "$HOME/.HOMDIRroot was not found."
      echo "Please run gcm_setup in non-clone mode at least once to use this script."
      exit 1
   else
      echo "$HOME/.HOMDIRroot and $HOME/.EXPDIRroot were not found."
      echo "Please run gcm_setup in non-clone mode at least once to use this script."
      exit 1
   endif
endif

# MAT There are two thoughts here. You can either place the clone in
# the .HOMDIRroot/.EXPDIRroot, but that is only nice if you have one
# single place you put all your experiments. What if you have lots of
# directories? Instead, let us default to the directory root of the
# cloned experiment if the cloned experiment is yours. If it isn't your
# experiment you are cloning, then default to the values in the dotfile

if ( $OLDUSER == $LOGNAME) then
   set HOMDIRroot=`dirname $OLDHOMDIR`
   set EXPDIRroot=`dirname $OLDEXPDIR`
else
   set HOMDIRroot=`cat $HOME/.HOMDIRroot`
   set EXPDIRroot=`cat $HOME/.EXPDIRroot`
endif

echo "Setting HOMDIR to $HOMDIRroot"
echo "Setting EXPDIR to $EXPDIRroot"

if ( -e $HOME/.GROUProot ) then
   set GROUProot=`cat $HOME/.GROUProot`
   echo "Using account $GROUProot"
else
   echo "$HOME/.GROUProot not found."
   set GROUProot=`groups | awk '{print $1}'`
   echo "Based off of groups, setting account to $GROUProot"
endif

# -----------------------------------------------
# Find out if we are running the cube and/or OGCM
# -----------------------------------------------

# First we need to find out if we are running in coupled mode
# To do this, we look for "OCEAN_NAME" in AGCM.rc:

set OGCM = `grep "OCEAN_NAME" ${OLDHOMDIR}/AGCM.rc | wc -l`

if ( $OGCM == 1 ) then
   set OGCM = TRUE
   # Now we need to find out if we are running MOM or MOM6 by looking
   # at OCEAN_NAME: val and checking if it is MOM or MOM6
   set OCEAN_MODEL = `grep "OCEAN_NAME" ${OLDHOMDIR}/AGCM.rc | cut -d: -f2 | tr -d ' '`
else if ( $OGCM == 0 ) then
   set OGCM = FALSE
else
   echo "Found more than one OCEAN_NAME in ${OLDHOMDIR}/AGCM.rc"
   echo "This is not allowed. Please fix this and try again."
   exit 1
endif

# ------------------------------------------------
# Set the new EXPDIR and HOMDIR based on the roots
# ------------------------------------------------
set  NEWEXPID=$EXPID
set NEWEXPDIR=$EXPDIRroot/$NEWEXPID
set NEWHOMDIR=$HOMDIRroot/$NEWEXPID

# -----------------------------------------
# If the new EXPDIR and HOMDIR exist, exit!
# -----------------------------------------

if ( -d $NEWEXPDIR ) then
   echo "$NEWEXPDIR already exists! Exiting!"
   exit 2
endif

if ( -d $NEWHOMDIR ) then
   echo "$NEWHOMDIR already exists! Exiting!"
   exit 3
endif

# -----------------------------------
# Make all our needed temporary files
# -----------------------------------

onintr TRAP

set FILES_TO_PROCESS=`mktemp`
set OLDEXPFILES=`mktemp`
set NEWEXPFILES=`mktemp`
set COPYSCRIPT=`mktemp`
set SEDFILE=`mktemp`


# --------------------------
# Setup the files to process
# --------------------------

cat > $FILES_TO_PROCESS << EOF
EXPDIR/post/gcm_post.j
EXPDIR/plot/gcm_plot.tmpl
EXPDIR/plot/gcm_quickplot.csh
EXPDIR/plot/gcm_moveplot.j
EXPDIR/archive/gcm_archive.j
EXPDIR/regress/gcm_regress.j
EXPDIR/convert/gcm_convert.j
EXPDIR/forecasts/gcm_forecast.tmpl
EXPDIR/forecasts/gcm_forecast.setup
EXPDIR/plot/plot.rc
EXPDIR/post/post.rc
HOMDIR/CAP.rc
HOMDIR/AGCM.rc
HOMDIR/HISTORY.rc
HOMDIR/gcm_run.j
HOMDIR/gcm_emip.setup
HOMDIR/logging.yaml
EOF

if( $OGCM == TRUE ) then

# Some files are common to both MOM and MOM6
cat >> $FILES_TO_PROCESS << EOF
HOMDIR/input.nml
HOMDIR/diag_table
HOMDIR/__init__.py
EXPDIR/plot/plotocn.j
EOF

# Some files are specific to MOM
if ( $OCEAN_MODEL == "MOM" ) then
cat >> $FILES_TO_PROCESS << EOF
HOMDIR/field_table
EOF
endif

# Some files are specific to MOM6
if ( $OCEAN_MODEL == "MOM6" ) then
cat >> $FILES_TO_PROCESS << EOF
HOMDIR/MOM_override
HOMDIR/MOM_input
HOMDIR/data_table
EOF
endif

endif

cat >> $FILES_TO_PROCESS << EOF
HOMDIR/fvcore_layout.rc
EOF

# ------------------------------------------------
# Create two sets of files so we can copy from one
# directory to another.
# ------------------------------------------------

# Then alter them
# ---------------

sed -e "/^EXPDIR/ s#EXPDIR#$OLDEXPDIR#" \
    -e "/^HOMDIR/ s#HOMDIR#$OLDHOMDIR#"   $FILES_TO_PROCESS > $OLDEXPFILES

sed -e "/^EXPDIR/ s#EXPDIR#$NEWEXPDIR#" \
    -e "/^HOMDIR/ s#HOMDIR#$NEWHOMDIR#"   $FILES_TO_PROCESS > $NEWEXPFILES

# -----------------------------------------
# Now, use paste to join these two files...
# ...add a cp in front of the lines.
# -----------------------------------------

paste $OLDEXPFILES $NEWEXPFILES | sed -e "s/.*/cp -a &/" > $COPYSCRIPT

# ------------------------
# Make the new directories
# ------------------------

foreach file (`cat $NEWEXPFILES`)
   set dir=`dirname $file`
   /bin/mkdir -p $dir
end

# -------------------
# Run the copy script
# -------------------

sh $COPYSCRIPT

# ----------------------------------------------------
# Create or copy over files that don't need processing
# ----------------------------------------------------

echo "$NEWHOMDIR" >> $NEWEXPDIR/.HOMDIR
/bin/cp $OLDEXPDIR/GEOSgcm.x $NEWEXPDIR
/bin/cp -a $OLDEXPDIR/RC $NEWEXPDIR/RC

# -----------------------------------------------------
# Now actually change the various environment variables
# -----------------------------------------------------

cat > $SEDFILE << EOF
/^setenv \+EXPDIR/ s#$OLDEXPDIR#$NEWEXPDIR#
/^setenv \+HOMDIR/ s#$OLDHOMDIR#$NEWHOMDIR#
/^setenv \+CNVDIR/ s#$OLDHOMDIR#$NEWHOMDIR#
/^setenv \+EXPID/  s#$OLDEXPID#$NEWEXPID#
/^set \+EXPDIR/ s#$OLDEXPDIR#$NEWEXPDIR#
/^set \+HOMDIR/ s#$OLDHOMDIR#$NEWHOMDIR#
/^set \+EXPID/  s#$OLDEXPID#$NEWEXPID#
/^EXPID:/  s#$OLDEXPID#$NEWEXPID#
/GEOSUTIL\/post\/gcmpost.script/ s#$OLDEXPDIR#$NEWEXPDIR#
/group_list/ s#\(group_list=\)\(.*\)#\1$GROUProot#
/^#SBATCH -A/ s#\(SBATCH -A \)\(.*\)#\1$GROUProot#
/^#SBATCH --account=/ s#\(SBATCH --account=\)\(.*\)#\1$GROUProot#
EOF

foreach file (`cat $NEWEXPFILES`)
   sed -i -f $SEDFILE $file
end

# ------------------------------------------
# Change the EXPDSC in HISTORY.rc to reflect
# the fact this experiment was cloned
# ------------------------------------------

#sed -i -e "/^EXPDSC:/ s#\(EXPDSC: \)\(.*\)#\1${NEWEXPID}_clonedfrom_${OLDEXPID}_by_${OLDUSER}#" $NEWHOMDIR/HISTORY.rc
 sed -i -e "/^EXPDSC:/ s#\(EXPDSC: \)\(.*\)#\1${EXPDSC}#" $NEWHOMDIR/HISTORY.rc
 sed -i -e "/^EXPID:/ s#\(EXPID: \)\(.*\)#\1${NEWEXPID}#" $NEWHOMDIR/HISTORY.rc

# Change OLDEXPID to NEWEXPID in __init__.py if it exists
# -------------------------------------------------------
if ( -e $NEWHOMDIR/__init__.py ) then
   sed -i -e "/$OLDEXPID/ s#$OLDEXPID#$NEWEXPID#" $NEWHOMDIR/__init__.py
endif

# -------------------------
# Construct the new job ids
# -------------------------

    set RUN_N=`echo $NEWEXPID | cut -b1-200`_RUN
   set RUN_FN=`echo $NEWEXPID | cut -b1-200`_FCST
   set POST_N=`echo $NEWEXPID | cut -b1-199`_POST
   set PLOT_N=`echo $NEWEXPID | cut -b1-200`_PLT
   set MOVE_N=`echo $NEWEXPID | cut -b1-200`_MOVE
set ARCHIVE_N=`echo $NEWEXPID | cut -b1-199`_ARCH
set REGRESS_N=`echo $NEWEXPID | cut -b1-199`_RGRS
set CONVERT_N=`echo $NEWEXPID | cut -b1-200`_CNV

sed -i -e "/^#PBS -N/ s#\(PBS -N \)\(.*\)#\1$RUN_N#"     \
       -e "/^#SBATCH --job-name=/ s#\(SBATCH --job-name=\)\(.*\)#\1$RUN_N#"     $NEWHOMDIR/gcm_run.j
sed -i -e "/^#PBS -N/ s#\(PBS -N \)\(.*\)#\1$RUN_FN#"    \
       -e "/^#SBATCH --job-name=/ s#\(SBATCH --job-name=\)\(.*\)#\1$RUN_FN#"    $NEWEXPDIR/forecasts/gcm_forecast.tmpl
sed -i -e "/^#PBS -N/ s#\(PBS -N \)\(.*\)#\1$POST_N#"    \
       -e "/^#SBATCH --job-name=/ s#\(SBATCH --job-name=\)\(.*\)#\1$POST_N#" \
       -e "/^setenv BATCHNAME/ s#\(setenv BATCHNAME *\)\(.*\)#\1 $POST_N#"      $NEWEXPDIR/post/gcm_post.j
sed -i -e "/^#PBS -N/ s#\(PBS -N \)\(.*\)#\1$PLOT_N#"    \
       -e "/^#SBATCH --job-name=/ s#\(SBATCH --job-name=\)\(.*\)#\1$PLOT_N#"    $NEWEXPDIR/plot/gcm_plot.tmpl

if ( -e $NEWEXPDIR/plot/gcm_moveplot.j ) then
   sed -i -e "/^#PBS -N/ s#\(PBS -N \)\(.*\)#\1$MOVE_N#"    \
          -e "/^#SBATCH --job-name=/ s#\(SBATCH --job-name=\)\(.*\)#\1$MOVE_N#" $NEWEXPDIR/plot/gcm_moveplot.j
endif

sed -i -e "/^#PBS -N/ s#\(PBS -N \)\(.*\)#\1$ARCHIVE_N#" \
       -e "/^#SBATCH --job-name=/ s#\(SBATCH --job-name=\)\(.*\)#\1$ARCHIVE_N#" $NEWEXPDIR/archive/gcm_archive.j
sed -i -e "/^#PBS -N/ s#\(PBS -N \)\(.*\)#\1$REGRESS_N#" \
       -e "/^#SBATCH --job-name=/ s#\(SBATCH --job-name=\)\(.*\)#\1$REGRESS_N#" $NEWEXPDIR/regress/gcm_regress.j
sed -i -e "/^#PBS -N/ s#\(PBS -N \)\(.*\)#\1$CONVERT_N#" \
       -e "/^#SBATCH --job-name=/ s#\(SBATCH --job-name=\)\(.*\)#\1$CONVERT_N#" $NEWEXPDIR/convert/gcm_convert.j

# --------------------------
# Echo Settings and Messages
# --------------------------

echo "Done with cloning!"
echo "------------------"
echo " "
echo "Original Experiment Directory: ${OLDEXPDIR}"
echo "------------------------------"
echo " "
echo "You must now copy your Initial Conditions into: "
echo "----------------------------------------------- "
echo "${NEWEXPDIR}"
echo ""
echo ""

# -------------------------
# Clean up the mktemp files
# -------------------------

/bin/rm $FILES_TO_PROCESS
/bin/rm $OLDEXPFILES
/bin/rm $NEWEXPFILES
/bin/rm $COPYSCRIPT
/bin/rm $SEDFILE

# ------------------------
# Cloned Experiment Source
# ------------------------

# NOTE: This variable is set at CMake time depending on
#       how the build was configured.
set INSTALL_TARFILE = TRUE
set TARFILE_NAME = "GEOSgcm.tar.gz"

if ( $INSTALL_TARFILE == "TRUE" ) then

   # Make a src directory under EXPDIR to hold current Experiment files
   # ------------------------------------------------------------------
   /bin/rm -rf ${NEWEXPDIR}/src
   mkdir   -p  ${NEWEXPDIR}/src

   echo "Copying Build Source Code into ${NEWEXPDIR}/src"
   # --------------------------------------------------------------
   if (-e ${GEOSDEF}/src/${TARFILE_NAME}) then
      cp ${GEOSDEF}/src/${TARFILE_NAME} ${NEWEXPDIR}/src
   else
      echo "${GEOSDEF}/src/${TARFILE_NAME} not found yet CMake was asked to make and install a tarfile."
      echo "Something went wrong."
      exit 7
   endif
   echo ""

endif

exit

# ------------------------------------------
# Set a trap to remove the tempfiles on EXIT
# ------------------------------------------
TRAP:
   echo "Interrupt received, cleaning up temporary files"
   /bin/rm $FILES_TO_PROCESS $OLDEXPFILES $NEWEXPFILES $COPYSCRIPT $SEDFILE
   exit 1

