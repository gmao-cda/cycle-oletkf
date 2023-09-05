#!/usr/bin/env python3

import os, sys, glob, argparse, datetime as dt, subprocess as sp
import shutil
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



def prep_recenter_1mem(wkdir  = os.path.abspath("./"), \
                       memDir = os.path.abspath("./"), \
                       member = 1):
   
    if not os.path.exists(wkdir):
        raise RuntimeError("wkdir ({}) does not exist".format(wkdir))
        sys.exit(1)

    if not os.path.exists(memDir):
        raise RuntimeError("memDir ({}) does not exist.".format(memDir))
        sys.exit(2)

    for f in rstFiles:
        rstFile = os.path.join(memDir, f)
        if not os.path.isfile( os.path.join(rstFile) ):
            raise RuntimeError("obsFile ({}) does not exist.".format(rstFile))
            sys.exit(3)

    srcBkgdFiles = rstFiles
    dstBkgdFiles = ["bkgd{:04d}.{}".format(member,f) for f in rstFiles]
    dstAnalFiles = ["anal{:04d}.{}".format(member,f) for f in rstFiles]

    # link bgkdFile to wkdir
    timeStamp = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    for fSrc, fDst in zip(srcBkgdFiles, dstBkgdFiles):
        if os.path.exists(os.path.join(wkdir,fDst)):
            fRenamed  = f"{fDst}_renamed_{timeStamp}"
            subDirRenamed = "bkgdFiles_renamed_mem{:04d}_{}".format(member, timeStamp)
            os.makedirs(os.path.join(wkdir,subDirRenamed),exist_ok=True)
            shutil.move(os.path.join(wkdir,fDst), os.path.join(wkdir,subDirRenamed,fRenamed))
        
        print("ln -sf", os.path.join(memDir,fSrc), "---->", os.path.join(wkdir,fDst))
        os.symlink(os.path.join(memDir,fSrc), os.path.join(wkdir,fDst))

    # copy anal file template to wkdir
    for fSrc, fDst in zip(srcBkgdFiles, dstAnalFiles):
        if os.path.exists(os.path.join(wkdir,fDst)):
            fRenamed  = f"{fDst}_renamed_{timeStamp}"
            subDirRenamed = "analFiles_renamed_mem{:04d}_{}".format(member, timeStamp)
            os.makedirs(os.path.join(wkdir,subDirRenamed),exist_ok=True)
            shutil.move(os.path.join(wkdir,fDst), os.path.join(wkdir,subDirRenamed,fRenamed))
        
        print("cp:", os.path.join(memDir,fSrc), "---->", os.path.join(wkdir,fDst))
        shutil.copy2(os.path.join(memDir,fSrc), os.path.join(wkdir,fDst))




def parse_cmd_line():
    parser = argparse.ArgumentParser(description=("Prepare a directory to start GEOS-ESM forecast"))
    parser.add_argument("wkdir", help=("where to run recenter"))
    parser.add_argument("--memDir", required=True, help=(""))
    parser.add_argument("--member", required=True,type=int,help=("which member"))

    args = parser.parse_args()

    args.wkdir = os.path.abspath(args.wkdir)
    args.memDir = os.path.abspath(args.memDir)

    print(args)
    return args    


if __name__ == '__main__':
    args = parse_cmd_line()
    prep_recenter_1mem(args.wkdir, \
                    args.memDir, \
                    args.member)

