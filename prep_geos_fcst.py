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
    parser.add_argument("--exp_template", required=True, default=None, help=("experiment template"))
    parser.add_argument("--cycleAnalDir", required=True, default=None, help=("experiment template"))
    parser.add_argument("--cycleBkgdDir", required=True, default=None, help=("experiment template"))

    args = parser.parse_args()

    args.wkdir = os.path.abspath(args.wkdir)
    args.exp_template = os.path.abspath(args.exp_template)
    args.cycleAnalDir = os.path.abspath(args.cycleAnalDir)
    args.cycleBkgdDir = os.path.abspath(args.cycleBkgdDir)
    
    print(args)
    return args

def prep_geos_fcst_dir(wkdir=None, \
                       expTplDir=None, \
                       cycleAnalDir=None, \
                       cycleBkgdDir=None):


    if not os.path.exists(expTplDir):
        raise RuntimeError("Exp template dir ({}) does not exist.".format(expTplDir))
        sys.exit(1)

    # create the work dir using existing template dir
    if os.path.exists(wkdir):
        wkdirRenamed=wkdir+dt.datetime.now().strftime("_renamed_%Y%m%dT%H%M%S")
        os.rename(wkdir, wkdirRenamed)
        print("wkdir ({}) already exists. rename the existing dir to {}.".format(wkdir, wkdirRenamed) )
    shutil.copytree(expTplDir, wkdir)

    # prepare initial conditions
    # copy ocean ana dir RESTART in cycleAnalDir to wkdir
    srcOcnAnalDir = os.path.join(cycleAnalDir,"RESTART")
    dstOcnAnalDir = os.path.join(wkdir, "RESTART")
    shutil.copytree(srcOcnAnalDir, dstOcnAnalDir)

    # copy other geos files in cyclBkgdDir to wkdir
    bkgdPathList = glob.glob(os.path.join(cycleBkgdDir,"*_rst"))
    for srcPath in bkgdPathList:
        srcFile =  os.path.basename(srcPath)
        dstPath = os.path.join(wkdir,srcFile)
        shutil.copy2(srcPath, dstPath)
        print(srcFile)

    # generate HISTORY.rc & __init__.py from file templates 
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
    



        


if __name__ == '__main__':
    args = parse_cmd_line()
    prep_geos_fcst_dir(args.wkdir, \
                       args.exp_template, \
                       args.cycleAnalDir, \
                       args.cycleBkgdDir)
