#!/usr/bin/env python3

import os, sys, glob, argparse, datetime as dt, subprocess as sp
import shutil
#import yaml
#import hashlib


def clean_tmpdir( letkfDir     = os.path.abspath("./20190101T05_letkf"),        \
                  fcstDirTpl   = os.path.abspath("./20190101T05_fcst{:04d}"),   \
                  obsopDirTpl  = os.path.abspath("./20190101T05_obsop{:04d}"),  \
                  ensize       = 1):

    letkfDir = os.path.abspath(letkfDir)
    if os.path.exists(letkfDir):
        print(f"clean_tmpdir: remove letkfDir: {letkfDir}")
        shutil.rmtree(letkfDir)
    else:
        print(f"warning: letkfDir {letkfDir}) does not exist.")

    for imem in range(1,ensize+1):
        # geos fcst memdir
        fcstDir = os.path.abspath( fcstDirTpl.format(imem) )
        if os.path.exists(fcstDir):
            print(f"clean_tmpdir: remove fcstDir: {fcstDir}")
            shutil.rmtree(fcstDir)
        else:
            print(f"warning: fcstDir {fcstDir}) does not exist.")

        # obsop memdir
        obsopDir = os.path.abspath( obsopDirTpl.format(imem) )
        if os.path.exists(obsopDir):
            print(f"clean_tmpdir: remove obsopDir: {obsopDir}")
            shutil.rmtree(obsopDir)
        else:
            print(f"warning: obsopDir {obsopDir}) does not exist.")



def parse_cmd_line():
    parser = argparse.ArgumentParser(description=())
    parser.add_argument("--letkfDir",required=True, default="./20190101T05_letkf", type=str,help=())
    parser.add_argument("--fcstDirTpl", required=True, default="./20190101T05_fcst{:04d}", type=str,help=())
    parser.add_argument("--obsopDirTpl", required=True, default="./20190101T05_obsop{:04d}", type=str,help=())
    parser.add_argument("--ensize", required=True, default=1, type=int, help=())
    parser.add_argument('--skip', action=argparse.BooleanOptionalAction,required=False, default=False)

    args = parser.parse_args()
   
    args.letkfDir = os.path.abspath(args.letkfDir)
    
    print(args)
    return args


if __name__ == '__main__':
    args = parse_cmd_line()
    if not args.skip:
        clean_tmpdir(args.letkfDir,    \
                     args.fcstDirTpl,  \
                     args.obsopDirTpl, \
                     args.ensize)
