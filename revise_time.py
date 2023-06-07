#!/usr/bin/env python3
import numpy as np
import datetime as dt
import argparse, os
from netCDF4 import Dataset
import glob

def get_rst_list():
    flist = ["achem_internal_rst", "aiau_import_rst", "cabc_internal_rst", "cabr_internal_rst", "caoc_internal_rst",\
             "catch_internal_rst", "du_internal_rst", "fvcore_internal_rst", "gocart_import_rst", "gocart_internal_rst", \
             "gwd_import_rst",  "hemco_import_rst", "hemco_internal_rst", "irrad_internal_rst", "lake_internal_rst", \
             "landice_internal_rst", "moist_import_rst", "moist_internal_rst", "ni_internal_rst", "ocean_internal_rst", \
             "openwater_internal_rst", "pchem_internal_rst", "saltwater_import_rst", "seaice_import_rst", "seaice_internal_rst", \
             "seaicethermo_internal_rst", "solar_internal_rst", "ss_internal_rst", "su_internal_rst", "surf_import_rst", \
             "tr_import_rst", "tr_internal_rst", "turb_import_rst", "turb_internal_rst"]
    return flist

def get_MOMres_list(path):
    #flist = ["RESTART/MOM.res_1.nc", "RESTART/MOM.res_2.nc", "RESTART/MOM.res_3.nc", "RESTART/MOM.res.nc"]
    path = os.path.abspath(path)
    flist = glob.glob(os.path.join(path, "MOM*.nc"))
    print("num of MOM files=", len(flist))
    for f in flist:
        print( "MOM FILE: {}".format(f))

    return flist

def get_mom6_restime(mdays):
    bdate = dt.datetime(2010,1,1,0,0,0)
    bdays = 733787.0

    ddays = mdays - bdays
    return bdate + dt.timedelta(days=ddays)

def get_mom6_mdays(mdate):
    bdate = dt.datetime(2010,1,1,0,0,0)
    bdays = 733787.0

    ddate = mdate-bdate
    return bdays + ddate.total_seconds()/(3600*24.0)

def revise_time_stamp(wkdir, start_date=dt.datetime(2010,1,1), end_date=dt.datetime(2010,1,1,6)):
    wkdir = os.path.abspath(wkdir)

    # revise cap_restart (e.g., 20100101 000000)
    print("="*80+"\n1. revise timestamp of cap_restart\n" )
    if os.path.exists(os.path.join(wkdir, "cap_restart")):
        fn_new = "cap_restart.original"
        print("file (cap_restart) already exists at {}. Rename it as cap_restart.original".format(wkdir, fn_new) )
        os.rename(os.path.join(wkdir, "cap_restart"), os.path.join(wkdir, fn_new))
     
    with open(os.path.join(wkdir, "cap_restart"),"w") as f:
        f.write(start_date.strftime("%Y%m%d %H%M%S\n") )
     
    # revise CAP.rc
    print("="*80+"\n2. revise timestamp of CAP.rc\n" )
    if os.path.exists(os.path.join(wkdir, "CAP.rc")):
        fn_new = "cap_restart.original"
        with open(os.path.join(wkdir,"CAP.rc"), "r") as f:
            lines = f.readlines()

        fn_new = "CAP.rc.original"
        print("rename CAP.rc to {} under dir: {}".format(fn_new, wkdir))
        os.rename(os.path.join(wkdir,"CAP.rc"), os.path.join(wkdir,fn_new))

        for i in range(len(lines)):
            if lines[i].find("BEG_DATE:") >= 0:
                lines[i] = lines[i][:14] + start_date.strftime("%Y%m%d %H%M%S\n")
            elif lines[i].find("END_DATE:") >= 0:
                lines[i] = lines[i][:14] + end_date.strftime("%Y%m%d %H%M%S\n")
                   
        with open(os.path.join(wkdir,"CAP.rc"), "w") as f:
            for l in lines:
                f.write(l)
 
    # revise _rst
    print("="*80+"\n3. revise timestamp of *_rst\n")
    for fn in get_rst_list():
        print("revise {}".format(os.path.join(wkdir,fn)))
        ds = Dataset(os.path.join(wkdir, fn), "r+")
        ib = ds.variables['time'].units.find("since")
        if ib>=0:
            ds.variables['time'].units = ds.variables['time'].units[:ib+6] + start_date.strftime("%Y-%m-%d %H:%M:%S")
        ds.close()

    # revise MOM6 time stamp
    print("="*80+"\n4. revise timestamp of MOM6 restart files\n")
    for fn in get_MOMres_list(os.path.join(wkdir,"RESTART")):
        print("revise {}".format(os.path.join(wkdir,"RESTART",os.path.basename(fn))))
        ds = Dataset(fn,"r+")
        mdays = ds.variables['Time'][:]
        print("original MOM6 date is", get_mom6_restime(mdays[0]))
        mdays_new = get_mom6_mdays(start_date)
        ds.variables['Time'][:] = np.array([mdays_new],dtype="f8")
        ds.close()

        ds = Dataset(fn,"r")
        mdays = ds.variables['Time'][:]
        print("the revised MOM6 date is", get_mom6_restime(mdays[0]))
        ds.close()

def parse_cmd_line():
    parser = argparse.ArgumentParser(description=("revise time stamps of all GEOS restart files"))
    parser.add_argument("wkdir", help=("directory prepared by gcm_setup"))
    parser.add_argument("start_date", help=("start date (YYYYMMDDHH)"))
    parser.add_argument("end_date",help=("end date (YYYYMMDDHH)"))
    args = parser.parse_args()

    args.start_date = dt.datetime.strptime(args.start_date,"%Y%m%d%H")
    args.end_date = dt.datetime.strptime(args.end_date,"%Y%m%d%H")

    print(args)
    return args


if __name__ == '__main__':
    args = parse_cmd_line()
    revise_time_stamp(args.wkdir, args.start_date, args.end_date)

    

