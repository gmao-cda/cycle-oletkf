cylc validate -v ../cpld_cylc_0d25_freerun
cylc install -v --symlink-dirs='log=/discover/nobackup/projects/gmao/scda_iesa/cda/formal_exp/' ../cpld_cylc_0d25_freerun
cylc play cpld_cylc_0d25_freerun
