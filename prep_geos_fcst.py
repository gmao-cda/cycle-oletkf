#!/usr/bin/env python3

import os, sys, glob, argparse, datetime as dt, subprocess as sp
import shutil
import yaml
import hashlib

def run_shell_cmd(cmd, wkdir, showError=False):
    p = sp.Popen(cmd, cwd=wkdir, shell=True,stdout=sp.PIPE, stderr=sp.PIPE)
    out, err = p.communicate()
    if showError: print("ERROR_MESSAGE={}".format(err.decode()))
    return out.decode()

def parse_cmd_line():
    parser = argparse.ArgumentParser(description=("Prepare a directory to start GEOS-ESM forecast"))
    parser.add_argument("wkdir", help=("where to run fcst"))
    parser.add_argument("--expTplDir", required=True, default=None, help=("experiment template"))
    parser.add_argument("--cycleAnalDir", required=True, default=None, help=("analDir storing analyzed files "))
    parser.add_argument("--cycleBkgdDir", required=True, default=None, help=("bkgdDir storing other files to run GEOSgcm"))
    parser.add_argument("--fwdExec", required=True, default="./GEOSgcm.x", help=("path where GEOSgcm.x is"))
    parser.add_argument("--fcstStartDate", required=True, default="20200101T00", help=("cycle date"))
    parser.add_argument("--fcstHrs", required=True, default=6, type=int, help=("forecast length (hours)"))

    args = parser.parse_args()

    args.wkdir        = os.path.abspath(args.wkdir)
    args.expTplDir    = os.path.abspath(args.expTplDir)
    args.cycleAnalDir = os.path.abspath(args.cycleAnalDir)
    args.cycleBkgdDir = os.path.abspath(args.cycleBkgdDir)
    args.fwdExec      = os.path.abspath(args.fwdExec)
    args.fcstStartDate = dt.datetime.strptime(args.fcstStartDate,"%Y%m%dT%H") 
    args.fcstHrs       = dt.timedelta(hours=args.fcstHrs)
    
    
    print(args)
    return args

def prep_geos_fcst_dir(wkdir         = None, \
                       expTplDir     = None, \
                       cycleAnalDir  = None, \
                       cycleBkgdDir  = None, \
                       fwdExec       = "./GEOSgcm.x", \
                       fcstStartDate = dt.datetime(2019,1,1,0,0), \
                       fcstHrs       = dt.timedelta(hours=6) ):


    if not os.path.exists(expTplDir):
        raise RuntimeError("Exp template dir ({}) does not exist.".format(expTplDir))
        sys.exit(1)

    # create the work dir using existing template dir
    if os.path.exists(wkdir):
        wkdirRenamed=wkdir+dt.datetime.now().strftime("_renamed_%Y%m%dT%H%M%S")
        os.rename(wkdir, wkdirRenamed)
        print("wkdir ({}) already exists. rename the existing dir to {}.".format(wkdir, wkdirRenamed) )
    print("create wkdir based on exp template")
    shutil.copytree(expTplDir, wkdir)

    # prepare initial conditions
    print("copy ocean ana dir RESTART in cycleAnalDir to wkdir")
    srcOcnAnalDir = os.path.join(cycleAnalDir,"RESTART")
    dstOcnAnalDir = os.path.join(wkdir, "RESTART")
    shutil.copytree(srcOcnAnalDir, dstOcnAnalDir)

    print("copy other geos files in cyclBkgdDir to wkdir")
    bkgdPathList = glob.glob(os.path.join(cycleBkgdDir,"*_rst"))
    for srcPath in bkgdPathList:
        srcFile =  os.path.basename(srcPath)
        dstPath = os.path.join(wkdir,srcFile)
        shutil.copy2(srcPath, dstPath)
        print(srcFile)

    print("generate HISTORY.rc, __init__.py, .HOMDIR")
    expName = os.path.basename(wkdir)
    cmd = 'sed -i -e "s#@GEOS_CDA_EXPID@#{}#g" HISTORY.rc.template'.format(expName)
    run_shell_cmd(cmd, wkdir)
    os.rename(os.path.join(wkdir,"HISTORY.rc.template"), os.path.join(wkdir,"HISTORY.rc"))

    cmd = 'sed -i -e "s#@GEOS_CDA_EXPID@#{}#g" -e "s#@GEOS_CDA_EXPDIR@#{}#g" __init__.py.template'.format(expName, wkdir)
    run_shell_cmd(cmd, wkdir)
    os.rename(os.path.join(wkdir,"__init__.py.template"), os.path.join(wkdir,"__init__.py"))

    fpath = os.path.join(wkdir,".HOMDIR")
    #if os.path.exists(fpath):
    with open(fpath,"w") as f:
        f.write(wkdir+"\n")

    print("copy the forward model (e.g., GEOSgcm.x) to the experiment dir")
    if not os.path.exists(args.fwdExec):
        raise RuntimeError("gcm executable does not exist at {}".format(args.fwdExec))
        sys.exit(2)
    execName = os.path.basename(args.fwdExec)
    shutil.copy2(args.fwdExec, os.path.join(wkdir,execName))

    print("generate cap_restart and revise CAP.rc")
    # create the cap_restart (e.g., 20100101 000000)
    if os.path.exists(os.path.join(wkdir, "cap_restart")):
        fnRenamed = "cap_restart.original"
        print("file (cap_restart) already exists at {}. Rename it as cap_restart.original".format(wkdir, fnRenamed) )
        os.rename(os.path.join(wkdir, "cap_restart"), os.path.join(wkdir, fnRenamed))

    with open(os.path.join(wkdir, "cap_restart"),"w") as f:
        f.write(fcstStartDate.strftime("%Y%m%d %H%M%S\n") )

    # update CAP.rc
    if fcstHrs.days > 99:
        raise RuntimeError("fcstHrs > 99 *24 hours not implemented")
        sys.exit(3)

    fcstEndDate = fcstStartDate + fcstHrs
    if os.path.exists(os.path.join(wkdir, "CAP.rc")):
        with open(os.path.join(wkdir,"CAP.rc"), "r") as f:
            lines = f.readlines()

        fnRenamed = "CAP.rc.original"
        print("rename CAP.rc to {} under dir: {}".format(fnRenamed, wkdir))
        os.rename(os.path.join(wkdir,"CAP.rc"), os.path.join(wkdir,fnRenamed))

        for i in range(len(lines)):
            if lines[i].find("BEG_DATE:") >= 0:
                lines[i] = lines[i][:14] + fcstStartDate.strftime("%Y%m%d %H%M%S\n")
            elif lines[i].find("END_DATE:") >= 0:
                lines[i] = lines[i][:14] + fcstEndDate.strftime("%Y%m%d %H%M%S\n")
            elif lines[i].find("JOB_SGMT:") >= 0:
                lines[i] = lines[i][:14] + "000000{:02d} {:02d}0000\n".format(fcstHrs.days, int(fcstHrs.seconds/3600))
            elif lines[i].find("NUM_SGMT:") >= 0:
                lines[i] = lines[i][:14] + "1\n"

        with open(os.path.join(wkdir,"CAP.rc"), "w") as f:
            for l in lines:
                f.write(l)

    else:
        raise RuntimeError("failed to find CAP.rc at {}".format(wkdir))
        sys.exit(4)


        


if __name__ == '__main__':
    args = parse_cmd_line()
    prep_geos_fcst_dir(args.wkdir, \
                       args.expTplDir, \
                       args.cycleAnalDir, \
                       args.cycleBkgdDir, \
                       args.fwdExec, \
                       args.fcstStartDate, \
                       args.fcstHrs )
