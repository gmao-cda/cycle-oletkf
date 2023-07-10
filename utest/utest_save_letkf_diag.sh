#!/bin/bash
expdir=../hello/
#/discover/nobackup/cda/projects2/odas3/obsbkgd/mean
cycle=20170101T06

./save_letkf_diag.py ../20170101T00_letkf_copy/ \
--bkgdMeanDir ${expdir}/bkgd/mean/${cycle} \
--bkgdSprdDir ${expdir}/bkgd/sprd/${cycle} \
--analMeanDir ${expdir}/anal/mean/${cycle} \
--analSprdDir ${expdir}/anal/sprd/${cycle} \
--ombDir ${expdir}/obsbkgd/mean/${cycle}
