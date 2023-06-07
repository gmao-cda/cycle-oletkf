#!/usr/bin/env python3

import os, sys, glob, argparse, datetime as dt, subprocess as sp
import yaml
#---- for revising time stamp -
import numpy as np
from netCDF4 import Dataset
#------------------------------

def parse_cmd_line():
    parser = argparse.ArgumentParser(description=("Generate an empty oletkf output directory"))
    parser.add_argument("expdir", help=("directory prepared by gcm_setup"))
    parser.add_argument("--members", required=True, default=10, type=int, help=("number of members"))
    parser.add_argument("--startDate", required=True, default="201901010000", help=("yyyymmddHH"))
    parser.add_argument("--cfgFile", required=True, default="init_member_mapping.yaml", help=("yaml file including initial member mappings"))
    parser.add_argument("--dryRun", default=False, action="store_true",help=("only check the completeness of files, dirs and show the moving flow."))
    args = parser.parse_args()

    args.expdir = os.path.abspath(args.expdir)
    if args.members < 0:
        raise RuntimeError("members ({}) <0. exit...".format(members))
        sys.exit(1)
    args.startDate = dt.datetime.strptime(args.startDate,"%Y%m%d%H")

    args.cfgFile = os.path.abspath(args.cfgFile)
    
    print(args)
    return args


def get_GEOSATMres_list(wkdir):
    flist_archived = ["achem_internal_rst", "aiau_import_rst", "cabc_internal_rst", "cabr_internal_rst", "caoc_internal_rst",\
             "catch_internal_rst", "du_internal_rst", "fvcore_internal_rst", "gocart_import_rst", "gocart_internal_rst", \
             "gwd_import_rst",  "hemco_import_rst", "hemco_internal_rst", "irrad_internal_rst", "lake_internal_rst", \
             "landice_internal_rst", "moist_import_rst", "moist_internal_rst", "ni_internal_rst", "ocean_internal_rst", \
             "openwater_internal_rst", "pchem_internal_rst", "saltwater_import_rst", "seaice_import_rst", "seaice_internal_rst", \
             "seaicethermo_internal_rst", "solar_internal_rst", "ss_internal_rst", "su_internal_rst", "surf_import_rst", \
             "tr_import_rst", "tr_internal_rst", "turb_import_rst", "turb_internal_rst"]
    flist = glob.glob(os.path.join(wkdir, "*_rst"))
    print("num of GEOSAtm+chem files={}".format(len(flist)))
    if len(flist) != len(flist_archived):
        raise RuntimeError("number of GEOSAtm+chem rst files does not match predefined value")
        sys.exit(3)
    return flist


def get_MOMres_list(path):
    #flist = ["RESTART/MOM.res_1.nc", "RESTART/MOM.res_2.nc", "RESTART/MOM.res_3.nc", "RESTART/MOM.res.nc"]
    path = os.path.abspath(path)
    flist = glob.glob(os.path.join(path, "MOM*.nc"))
    print("num of MOM files=".format(len(flist)))
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


def generate_init_ensemble(expdir=None, \
                           members=10, \
                           sdate=dt.datetime(2019,1,1,0,0), \
                           cfgFile="init_member_mapping.yaml",\
                           dryRun=True):
    with open(cfgFile, "r") as f:
        cfg = yaml.safe_load(f)

    nml="initial_ensemble_mapping"
    if members != len(cfg[nml]):
        raise RuntimeError("the input ensemble size is not equal to the # of restart files in {}.".format(cfgFile))
        sys.exit(2)

    # check if the path_to and tarfile are ready for init members
    mappings={}
    for m in range(1,members+1):
        cmem="{:04d}".format(m)
        cdate=sdate.strftime("%Y%m%dT%H")

        # generate path_to  & check if it exists and empty
        memBkgdDir=os.path.join(expdir,"bkgd",cmem,cdate)  # e.g., expdir/bkgd/0001/20220101T00
        memAnalDir=os.path.join(expdir,"anal",cmem,cdate)  # e.g., expdir/anal/0001/20220101T00

        for memdir in [memBkgdDir, memAnalDir]:
            if not os.path.isdir(memdir):
                raise RuntimeError("directory to store the initial member{} ({}) does not exist".format(cmem,memdir))
                exit(3)
            else:
                if os.listdir(memdir): # not empty dir
                    print(os.listdir(memdir))
                    raise RuntimeError("directory {} is not empty. stop".format(memdir))
                    exit(4)
             
        # generate tarfile_from & check if it exists
        tarfile=cfg[nml]["member{}".format(cmem)]
        if not os.path.exists(tarfile):
            raise RuntimeError("tar file of member{} ({}) does not exist".format(cmem, tarfile))
            exit(5)

        # store the mapping for each member
        mappings[m] = [memBkgdDir, memAnalDir, tarfile]


    for m in range(1,members+1):
        memBkgdDir, memAnalDir, tarfile = mappings[m]
        print("member_{}: {}\n{} <--- {}\n".format(m, memBkgdDir, memAnalDir, tarfile))

    if not dryRun:
        for m in range(1,members+1):
            print("="*80+"\nGenerate ensemble #{:04d}\n".format(m))
            memBkgdDir, memAnalDir, tarfile = mappings[m]
            move_restart(memBkgdDir, memAnalDir, tarfile)
            revise_restart_time_nonocean(memBkgdDir, sdate)
            revise_restart_time_ocean(os.path.join(memAnalDir,"RESTART"), sdate)

    print("DONE!")

def revise_restart_time_ocean(wkdir, sdate=dt.datetime(2010,1,1)):
    print("-"*80+"\nrevise timestamp of MOM6 restart files\n")
    for fn in get_MOMres_list(os.path.abspath(wkdir)):
        print("revise {}".format(fn))
        ds = Dataset(fn,"r+")
        mdays = ds.variables['Time'][:]
        print("original MOM6 date is", get_mom6_restime(mdays[0]))
        mdays_new = get_mom6_mdays(sdate)
        ds.variables['Time'][:] = np.array([mdays_new],dtype="f8")
        ds.close()

        ds = Dataset(fn,"r")
        mdays = ds.variables['Time'][:]
        print("the revised MOM6 date is", get_mom6_restime(mdays[0]))
        ds.close()


def revise_restart_time_nonocean(wkdir, sdate=dt.datetime(2010,1,1)):
    print("-"*80+"\nrevise timestamp of *_rst\n")
    for fn in get_GEOSATMres_list(os.path.abspath(wkdir)):
        print("revise {}".format(os.path.join(fn)))
        ds = Dataset(fn, "r+")
        print("original date: {}".format(ds.variables['time'].units))
        ib = ds.variables['time'].units.find("since")
        if ib>=0:
            ds.variables['time'].units = ds.variables['time'].units[:ib+6] + sdate.strftime("%Y-%m-%d %H:%M:%S")
        ds.close()

        ds = Dataset(fn, "r")
        print("revised date: {}".format(ds.variables['time'].units))
        ds.close()

def move_restart(bkgdDir=None, analDir=None, tarfile=None):
    print("-"*80+"\nMove restart tar files to member dir\n")
    bkgdDir = os.path.abspath(bkgdDir)
    analDir = os.path.abspath(analDir)
    tarfile = os.path.abspath(tarfile)
    tarfileName = os.path.basename(tarfile)

    # bkgdDir: untar the restart tar file
    os.symlink(tarfile, os.path.join(bkgdDir,tarfileName))
    sp.run(["tar","-xvf", tarfileName], cwd=bkgdDir, check=True)
    os.unlink(os.path.join(bkgdDir,tarfileName))

    # bkgdDir: create cap_restart
    flist = glob.glob(os.path.join(bkgdDir,"*_rst*.nc4"))
    cRestartDate = flist[0].split(".")[2]
    restartDate = dt.datetime.strptime(cRestartDate,"e%Y%m%d_%Hz") # e.g., e20160201_00z
    with open(os.path.join(bkgdDir,"INIT_ENSEMBLE_INFO"),"w") as f:
        f.write(restartDate.strftime("%Y%m%d %H%M%S\n")) #e.g., 20160201 000000
        f.write("init_tarfile: {}\n".format(tarfile))
        f.write("init_bkgd_dir: {}\n".format(bkgdDir))
        f.write("init_anal_dir: {}\n".format(analDir))

    # bkgdDir: rename atm, chemical, seaice restart files: trim the prefix and suffix
    # 5deg.solar_internal_rst.e20160101_06z.GEOSgcm-v10.23.0.CF0012x6C_TM0072xTM0036_CF0012x6C_DE0360xPE0180.nc4 => solar_internal_rst
    [os.rename(os.path.join(bkgdDir,f), os.path.join(bkgdDir,f.split(".")[1])) for f in flist]

    # bkgdDir: rename ocean restart file dir & move it to analDir
    ocn_dirname = "RESTART.{}".format(cRestartDate)
    os.rename(os.path.join(bkgdDir,ocn_dirname), os.path.join(analDir,"RESTART"))



    print("DONE!")


if __name__ == '__main__':
    args = parse_cmd_line()
    generate_init_ensemble(args.expdir, \
                              args.members, \
                              args.startDate, \
                              args.cfgFile, \
                              args.dryRun)
