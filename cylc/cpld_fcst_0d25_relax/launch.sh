cylc validate -v ../cpld_fcst_0d25_relax
cylc install -v --symlink-dirs='log=/discover/nobackup/projects/gmao/scda_iesa/cda/formal_exp/' ../cpld_fcst_0d25_relax
cylc play cpld_fcst_0d25_relax
