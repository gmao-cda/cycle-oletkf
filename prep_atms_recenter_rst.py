#!/usr/bin/env python3


import os, sys, glob, argparse, platform, datetime as dt, subprocess as sp
import shutil
from env_modules_python import module
#import yaml
#import hashlib

rstFiles = ["fvcore_internal_rst",
            "moist_internal_rst",
            "surf_import_rst"]


def run_shell_cmd(cmd, wkdir, showError=False):
    p = sp.Popen(cmd, cwd=wkdir, shell=True,stdout=sp.PIPE, stderr=sp.PIPE)
    out, err = p.communicate()
    if showError: print("ERROR_MESSAGE={}".format(err.decode()))
    return p.returncode, out.decode(), err.decode()


def create_center_dir(wkdir    = os.path.abspath("./"), \
                      sdate    = dt.datetime(2019,1,1,6,0,0), \
                      edate    = dt.datetime(2019,1,2,0,0,0), \
                      tinc     = dt.timedelta(hours=6), \
                      rstDir   = os.path.abspath("./"), \
                      rstSdate = dt.datetime(2019,1,1,6,0,0), \
                      rstEdate = dt.datetime(2019,1,2,0,0,0), \
                      rstTinc  = dt.timedelta(hours=6), \
                      dryRun   = False ):

    wkdir = os.path.abspath(wkdir)
    rstDir = os.path.abspath(rstDir)

    nDirsTo   = round( (edate-sdate)/tinc ) + 1
    nDirsFrom = round( (rstEdate-rstSdate)/rstTinc ) + 1
    if nDirsTo != nDirsFrom:
        raise RuntimeError(f"nDirsTo ({nDirsTo}) and nDirsFrom ({nDirsFrom}) of different size. exit...")
        sys.exit(1)

    dirPairs = {}
    cdate = sdate
    cRstDate = rstSdate
    while cdate <= edate:
        subDirTo = os.path.join(wkdir,"center",cdate.strftime("%Y%m%dT%H"))
        rstTarFile = os.path.join(rstDir,"restarts.{}.tar".format(cRstDate.strftime("e%Y%m%d_%Hz")))
        dirPairs[subDirTo] = rstTarFile

        if not os.path.exists(rstTarFile):
            raise RuntimeError(f"rstTarFile ({rstTarFile}) does not exist.")
            sys.exit(2)

        cdate    += tinc
        cRstDate += rstTinc
    
    for subDirTo in dirPairs:
       rstTarFile = dirPairs[subDirTo] 
       print(f"{rstTarFile} ---> {subDirTo}")

    if not dryRun:
       iDir = 0
       for subDirTo in dirPairs:
          iDir += 1
          print(f"processing time slot {iDir} of {nDirsTo} slots------------------------")
          if os.path.exists(subDirTo):
            # check if already has rstFiles there, if so, rename them
            timeStamp = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
            for f in rstFiles:
               if os.path.exists(os.path.join(subDirTo,f)):
                 fRenamed  = f"{f}_renamed_{timeStamp}"
                 subDirRenamed = f"files_renamed_{timeStamp}"
                 os.makedirs(os.path.join(subDirTo,subDirRenamed),exist_ok=True)
                 os.rename(os.path.join(subDirTo,f), os.path.join(subDirTo,subDirRenamed,fRenamed))
          else:
            os.makedirs(subDirTo, exist_ok=True)
            
          rstTarFile = dirPairs[subDirTo] 
          for f in rstFiles:
             tarCmd = f"tar -xvf {rstTarFile} --wildcards '*{f}*'"
             print(tarCmd)
             ret, out, err = run_shell_cmd(tarCmd, wkdir=subDirTo)
             if ret != 0:
               raise RuntimeError(f"failed to run cmd (tarCmd): errmsg = {err}")
               sys.exit(3)
             
             # try to catch the full name of untared file (e.g., atmM2_relaxSST_relaxSSS.fvcore_internal_rst.e20190922_21z.GEOSgcm-v10.23.0.CF0180x6C_TM1440xTM1080_newtopo_CF0180x6C_DE0360xPE0180.nc4)
             flist = glob.glob(os.path.join(subDirTo, f"*{f}*"))
             if len(flist) > 1:
                raise RuntimeError("more than 1 file has the searched pattern",flist, len(flist))
                sys.exit(4)

             fFullName = os.path.basename(flist[0])
             print(os.path.join(subDirTo, fFullName), "--->", os.path.join(subDirTo, f))
             os.rename(os.path.join(subDirTo, fFullName), os.path.join(subDirTo, f))


def parse_cmd_line():
    parser = argparse.ArgumentParser(description=("Generate an empty oletkf output directory"))
    parser.add_argument("wkdir",       help=("directory prepared by gcm_setup"))
    parser.add_argument("--startDate", required=True,  default="201901010000", help=("yyyymmddHH"))
    parser.add_argument("--endDate",   required=False, default=None, help=("yyyymmddHH"))
    parser.add_argument("--tinc",      required=False, default=6, type=int, help=("time interval between two day cycles (unit: hours)"))
    parser.add_argument("--rstDir",       required=True, help=())
    parser.add_argument("--rstStartDate", required=True,  default="201901010000", help=("yyyymmddHH"))
    parser.add_argument("--rstEndDate",   required=False, default=None, help=("yyyymmddHH"))
    parser.add_argument("--rstTinc",      required=False, default=6, type=int, help=("time interval between two day cycles (unit: hours)"))
    parser.add_argument("--dryRun",       required=False, action="store_true", help=())
    args = parser.parse_args()

    args.wkdir = os.path.abspath(args.wkdir)
    args.startDate = dt.datetime.strptime(args.startDate,"%Y%m%d%H")
    if args.endDate is None:
        args.endDate = args.startDate
    else:
        args.endDate = dt.datetime.strptime(args.endDate,"%Y%m%d%H")
    args.tinc = dt.timedelta(hours=args.tinc)


    args.rstDir = os.path.abspath(args.rstDir)
    args.rstStartDate = dt.datetime.strptime(args.rstStartDate,"%Y%m%d%H")
    if args.rstEndDate is None:
        args.rstEndDate = args.rstStartDate
    else:
        args.rstEndDate = dt.datetime.strptime(args.rstEndDate,"%Y%m%d%H")
    args.rstTinc = dt.timedelta(hours=args.rstTinc)


    print(args)
    return args


if __name__ == '__main__':
    args = parse_cmd_line()
    create_center_dir(args.wkdir, \
                    args.startDate, \
                    args.endDate, \
                    args.tinc, \
                    args.rstDir, \
                    args.rstStartDate, \
                    args.rstEndDate, \
                    args.rstTinc, \
                    args.dryRun)
     
