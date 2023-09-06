#!/usr/bin/env python3

import os, sys, glob, argparse, datetime as dt, subprocess as sp
import shutil
#import yaml
#import hashlib


def clean_tmpdir( recenterDir = os.path.abspath("./recenter"), \
                  fcstDirTpl  = os.path.abspath("./fcst_{:04d}"), \
                  ensize      = 1):

    recenterDir = os.path.abspath(recenterDir)
    if os.path.exists(recenterDir):
        print(f"clean_tmpdir: remove recenterDir: {recenterDir}")
        shutil.rmtree(recenterDir)
    else:
        print(f"warning: recenterDir {recenterDir}) does not exist.")

    for imem in range(1,ensize+1):
        fcstDir = os.path.abspath( fcstDirTpl.format(imem) )
        if os.path.exists(fcstDir):
            print(f"clean_tmpdir: remove fcstDir: {fcstDir}")
            shutil.rmtree(fcstDir)
        else:
            print(f"warning: fcstDir {fcstDir}) does not exist.")


def parse_cmd_line():
    parser = argparse.ArgumentParser(description=())
    parser.add_argument("--recenterDir",required=True, default="./20190101T05_recenter", type=str,help=())
    parser.add_argument("--fcstDirTpl", required=True, default="./20190101T05_fcst{:04d}", type=str,help=())
    parser.add_argument("--ensize", required=True, default=1, type=int, help=())
    parser.add_argument('--skip', action=argparse.BooleanOptionalAction,required=False, default=False)

    args = parser.parse_args()
   
    args.recenterDir = os.path.abspath(args.recenterDir)
    
    print(args)
    return args


if __name__ == '__main__':
    args = parse_cmd_line()
    if not args.skip:
        clean_tmpdir(args.recenterDir, \
                                 args.fcstDirTpl, \
                                 args.ensize)
