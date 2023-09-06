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
    return out.decode()

def reconcile_recenter_mem( bkgdDir = os.path.abspath("./bkgd"), \
                            analDir = os.path.abspath("./anal") ):
    """
    1. mv ocean RESTART from bkgd to anal
    2. mv fvcore_,moist_surf under bkgd to bkgd/before_recenter
    3. copy fvcore_,moist_surf under anal to bkgd
    """

    bkgdDir = os.path.abspath(bkgdDir)
    analDir = os.path.abspath(analDir)

    if not os.path.exists(bkgdDir):
        raise RuntimeError(f"bkgdDir ({bkgdDir}) does not exist.")
        sys.exit(1)

    if not os.path.exists(analDir):
        # analDir should exist because recenter steps moves analFile to it
        raise RuntimeError(f"analDir ({analDir}) does not exist.")
        sys.exit(2)
    else:
        # check if anal rstFiles exist there
        for f in rstFiles:
            fpath = os.path.join(analDir,f)
            if not os.path.exists(fpath):
                raise RuntimeError(f"required rst file ({fpath}) does not exist")
                sys.exit(3)

    # mv ocean RESTART from bkgd to anal
    ocnBkgdDir = os.path.join(bkgdDir, "RESTART")
    ocnAnalDir = os.path.join(analDir, "RESTART")
    shutil.move(ocnBkgdDir, ocnAnalDir)

    # mv fvcore_,moist_surf under bkgd to bkgd/atms_before_recenter_{timeStamp}
    timeStamp = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    atmsRstDir=os.path.join(bkgdDir, f"atms_before_recenter_{timeStamp}")

    if not os.path.exists(atmsRstDir):
        os.makedirs(atmsRstDir, exist_ok = True)

    for f in rstFiles:
        if os.path.exists(os.path.join(bkgdDir, f)):
            fRenamed = f"{f}_before_recenter_{timeStamp}"
            shutil.move(os.path.join(bkgdDir,f), os.path.join(atmsRstDir,fRenamed))


    # copy anal rstFiles to bkgdDir
    for f in rstFiles:
        srcPath = os.path.join(analDir,f)
        dstPath = os.path.join(bkgdDir,f)
        print("cp: ", srcPath, "--->", dstPath) 
        shutil.copy2(srcPath, dstPath)


def parse_cmd_line():
    parser = argparse.ArgumentParser(description=())
    parser.add_argument("--bkgdDir",required=True, help=())
    parser.add_argument("--analDir",required=True, help=())
    parser.add_argument('--skip', action=argparse.BooleanOptionalAction,required=False, default=False)

    args = parser.parse_args()
   
    args.bkgdDir = os.path.abspath(args.bkgdDir)
    args.analDir = os.path.abspath(args.analDir)
    
    print(args)
    return args


if __name__ == '__main__':
    args = parse_cmd_line()
    if not args.skip:
        reconcile_recenter_mem(args.bkgdDir, \
                               args.analDir)
