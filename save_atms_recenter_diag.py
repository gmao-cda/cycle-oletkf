#!/usr/bin/env python3

import os, sys, glob, argparse, datetime as dt, subprocess as sp
import shutil
#import yaml
#import hashlib

rstFiles = ["fvcore_internal_rst",
            "moist_internal_rst",
            "surf_import_rst"]

def save_recenter_diag_output( recenterDir = os.path.abspath("./"), \
                               meanDir = os.path.abspath("./"), \
                               sprdDir = os.path.abspath("./"),\
                               meanPrefix = "bkgdmean", \
                               sprdPrefix = "bkgdsprd" ):

    if not os.path.exists(recenterDir):
        raise RuntimeError(f"recenterDir ({recenterDir}) does not exist.")
        sys.exit(1)
    
    dnames    = ["meanDir", "sprdDir"]
    dirs      = [meanDir, sprdDir]
    prefix    = [meanPrefix, sprdPrefix]
    fileList  = [["{}.{}".format(meanPrefix,f) for f in rstFiles ], \
                 ["{}.{}".format(sprdPrefix,f) for f in rstFiles ]]

    for files in fileList:
        for f in files:
            fpath = os.path.join(recenterDir, f)
            if not os.path.exists(fpath):
                raise RuntimeError(f"required file ({fpath}) does not exist.")
                sys.exit(2)

    for dnm, d, files in zip(dnames, dirs, fileList):
        srcDir = recenterDir
        dstDir = d

        if not os.path.exists(dstDir):
            print(f"{dnm} dir ({dstDir}) does not exist. creating it now")
            os.makedirs( dstDir, exist_ok = True)
        else:
            #make sure there is no exisitng files with the same name
            timeStamp = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
            for f in files:
                if os.path.exists( os.path.join(dstDir, f) ):
                    fRenamed  = f"{f}_renamed_{timeStamp}"
                    subDirRenamed = f"rstFiles_renamed_{timeStamp}"
                    os.makedirs(os.path.join(dstDir,subDirRenamed),exist_ok=True)
                    shutil.move(os.path.join(dstDir,f), os.path.join(dstDir,subDirRenamed,fRenamed))

        for f in files:
            print(f"mv {dnm} file: {srcDir}/{f} ----> {dstDir}/{f}")
            shutil.move(os.path.join(srcDir,f), os.path.join(dstDir,f))


def parse_cmd_line():
    parser = argparse.ArgumentParser(description=(""))
    parser.add_argument("recenterDir",help=(""))
    parser.add_argument("--meanDir", required=True, help=(""))
    parser.add_argument("--sprdDir", required=True, help=(""))
    parser.add_argument("--meanPrefix", required=False, default="bkgdmean", help=(""))
    parser.add_argument("--sprdPrefix", required=False, default="bkgdsprd", help=(""))

    args = parser.parse_args()

    args.recenterDir = os.path.abspath(args.recenterDir)
    args.meanDir = os.path.abspath(args.meanDir)
    args.sprdDir = os.path.abspath(args.sprdDir)
    
    print(args)
    return args



if __name__ == '__main__':
    args = parse_cmd_line()
    save_recenter_diag_output( args.recenterDir, \
                               args.meanDir, \
                               args.sprdDir,\
                               args.meanPrefix, \
                               args.sprdPrefix)
