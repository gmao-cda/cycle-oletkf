#!/bin/bash

wkdir="./tmp"
member=3
cmember=$(printf "%4.4d" $member)
memDir="/discover/nobackup/cda/projects2/atms_recenter_m3/bkgd/${cmember}/20190921T21/"




cmd="./prep_atms_recenter.py ${wkdir} \
      --memDir ${memDir} \
      --member ${member}
     "

echo $cmd
$cmd
     


