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


def save_recenter_mem_output(recenterDir    = os.path.abspath("./"), \
                                 saveDir    = os.path.abspath("./"), \
                                 member     = 1, \
                              analPrefixTpl = "anal{:04d}"):
    
    if not os.path.exists(saveDir):
        raise RuntimeError("recenterDir ({}) does not exist".format(saveDir))
        sys.exit(1)

    if not os.path.exists(recenterDir):
        raise RuntimeError("recenterDir ({}) does not exist".format(recenterDir))
        sys.exit(2)

    srcDir = recenterDir
    dstDir = saveDir

    analPrefix = analPrefixTpl.format(member)
    srcFiles = ["{}.{}".format(analPrefix, f) for f in rstFiles]
    dstFiles = [f for f in rstFiles]

    for srcFile in srcFiles:
        srcPath = os.path.join(srcDir,srcFile)
        if not os.path.exists(srcPath):
            raise RuntimeError(f" file ({srcPath}) does not exist.")
            sys.exit(3)

    timeStamp = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    for srcFile, dstFile in zip(srcFiles, dstFiles):
        # check if dstFile already exists in dstDir
        if os.path.exists( os.path.join(dstDir, dstFile) ):
            dstFileRenamed  = f"{dstFile}_renamed_{timeStamp}"
            subDirRenamed = f"rstFiles_renamed_{timeStamp}"
            os.makedirs(os.path.join(dstDir,subDirRenamed),exist_ok=True)
            shutil.move(os.path.join(dstDir,dstFile), os.path.join(dstDir,subDirRenamed,dstFileRenamed))

        print("mv: ", os.path.join(srcDir, srcFile), "---->", os.path.join(dstDir,dstFile))
        shutil.move(os.path.join(srcDir, srcFile), os.path.join(dstDir,dstFile))


def parse_cmd_line():
    parser = argparse.ArgumentParser(description=())
    parser.add_argument("recenterDir", help=())
    parser.add_argument("--saveDir",required=True, help=())
    parser.add_argument("--member", required=True, type=int,help=())
    parser.add_argument("--analPrefixTpl",required=False,default="anal{:04d}",type=str,help=())
    parser.add_argument('--skip', action=argparse.BooleanOptionalAction,required=False, default=False)

    args = parser.parse_args()
   
    args.saveDir = os.path.abspath(args.saveDir)
    args.recenterDir = os.path.abspath(args.recenterDir)
    
    print(args)
    return args


if __name__ == '__main__':
    args = parse_cmd_line()
    if not args.skip:
        save_recenter_mem_output(args.recenterDir, \
                             args.saveDir, \
                             args.member, \
                             args.analPrefixTpl)
