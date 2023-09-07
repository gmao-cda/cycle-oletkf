cylc validate -v ../atms_recenter_0d25_m20
cylc install -v --symlink-dirs='log=/discover/nobackup/projects/gmao/scda_iesa/cda/formal_exp/' ../atms_recenter_0d25_m20
cylc play atms_recenter_0d25_m20
