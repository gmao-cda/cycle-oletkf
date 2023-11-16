cylc validate -v ../cpld_odas_0d25_m20_qc60NSv2
cylc install -v --symlink-dirs='log=/discover/nobackup/projects/gmao/scda_iesa/cda/formal_exp/' ../cpld_odas_0d25_m20_qc60NSv2
cylc play cpld_odas_0d25_m20_qc60NSv2
