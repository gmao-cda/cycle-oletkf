#!/usr/bin/env python3

import os, sys, glob, argparse, datetime as dt, subprocess as sp
import shutil
#import yaml
#import hashlib

def run_shell_cmd(cmd, wkdir, showError=False):
    p = sp.Popen(cmd, cwd=wkdir, shell=True,stdout=sp.PIPE, stderr=sp.PIPE)
    out, err = p.communicate()
    if showError: print("ERROR_MESSAGE={}".format(err.decode()))
    return out.decode()

def parse_cmd_line():
    parser = argparse.ArgumentParser(description=())
    parser.add_argument("analDir", help=())
    parser.add_argument("--letkfDir", required=True, help=("where to run fcst"))
    parser.add_argument("--bkgdDir", required=True, help=())
    parser.add_argument("--res", required=True, choices=["0d25","5"],help=())
    parser.add_argument("--member", required=True, type=int,help=())

    args = parser.parse_args()
    
    args.letkfDir = os.path.abspath(args.letkfDir)
    args.analDir  = os.path.abspath(args.analDir)
    args.bkgdDir  = os.path.abspath(args.bkgdDir)
    
    print(args)
    return args


def save_letkf_mem_output(analDir  = os.path.abspath("./"), \
                          letkfDir = os.path.abspath("./"), \
                          bkgdDir  = os.path.abspath("./"), \
                          res      = "5", \
                          member   = 1 ):
    
    if not os.path.exists(letkfDir):
        raise RuntimeError("letkfDir ({}) does not exist".format(letkfDir))
        sys.exit(1)

    ocnAnalDir = os.path.join(analDir, "RESTART")
    if os.path.exists(ocnAnalDir):
        ocnAnalDirRenamed = ocnAnalDir + dt.datetime.now().strftime("_renamed_%Y%m%dT%H%M%S")
        print("Warning: ocnAnalDir ({}) already exists there. rename it as {}".format(ocnAnalDir,ocnAnalDirRenamed))
        os.rename(ocnAnalDir, ocnAnalDirRenamed)
    os.makedirs(ocnAnalDir)

    if res == "5":
       # letkfDir/anal001.MOM.res.nc ---> analDir/RESTART/MOM.res.nc
       srcs = [ os.path.join(letkfDir, "anal{:03d}.MOM.res.nc".format(member)) ]
       dsts = [ os.path.join(ocnAnalDir, "MOM.res.nc") ]
       cmds = [ shutil.move ]
    elif res == "0d25":
        # letkfDir/anal001.MOM.res.nc ---> analDir/RESTART/MOM.res.nc
        # letkfDir/anal001.MOM.res_1.nc ---> analDir/RESTART/MOM.res_1.nc
        # bkgdDir/RESTART/not_updated MOM.res_2.nc ---> analDir/RESTART/ MOM.res_2.nc
        # bkgdDir/RESTART/not_updated MOM.res_3.nc ---> analDir/RESTART/ MOM.res_3.nc
       ocnBkgdDir = os.path.join(bkgdDir, "RESTART")
       srcs = [ os.path.join(letkfDir, "anal{:03d}.MOM.res.nc".format(member)), \
                os.path.join(letkfDir, "anal{:03d}.MOM.res_1.nc".format(member)), \
                os.path.join(ocnBkgdDir, "anal{:03d}.MOM.res_2.nc".format(member)), \
                os.path.join(ocnBkgdDir, "anal{:03d}.MOM.res_3.nc".format(member)) ]
       dsts = [ os.path.join(ocnAnalDir, "MOM.res.nc"), \
                os.path.join(ocnAnalDir, "MOM.res_1.nc"), \
                os.path.join(ocnAnalDir, "MOM.res_2.nc"), \
                os.path.join(ocnAnalDir, "MOM.res_3.nc") ]
       cmds = [ shutil.move, \
                shutil.move, \
                shutil.copy2, \
                shutil.copy2  ]
    else:
        raise RuntimeError("unsupported resolution ({})".format(res))
        sys.exit(2)

    for src, dst, cmd in zip(srcs, dsts, cmds):
        print("{} ---> {} cmd: {}".format(src, dst, cmd))
        if os.path.exists(dst):
            dstRenamed = dst + dt.datetime.now().strftime("_renamed_%Y%m%dT%H%M%S")
            print("Warning: file ({}) already exists there. rename it as {}".format(dst,dstRenamed))
            os.rename(dst,dstRenamed)
        cmd(src, dst)

if __name__ == '__main__':
    args = parse_cmd_line()
    save_letkf_mem_output(args.analDir, \
                          args.letkfDir, \
                          args.bkgdDir, \
                          args.res, \
                          args.member )
