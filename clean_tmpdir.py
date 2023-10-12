#!/usr/bin/env python3

import os, sys, glob, argparse, datetime as dt, subprocess as sp
import shutil
#import yaml
#import hashlib


def clean_tmpdir( sharedDirs = os.path.abspath("./recenter"), \
                  memDirTpls  = os.path.abspath("./fcst_{:04d}"), \
                  delimiter   = ";", \
                  ensize      = 1):

    print("sharedDirs=",sharedDirs)
    sharedDirs = sharedDirs.split(delimiter)
    print("sharedDirs=",sharedDirs)
    print("len(sharedDirs)=", len(sharedDirs))
    for sharedDir in sharedDirs:
        d = os.path.abspath(sharedDir)
        if os.path.exists(d):
            print(f"clean_tmpdir: remove sharedDir: {d}")
            shutil.rmtree(d)
        else:
            print(f"warning: sharedDir ({d}) does not exist.")

    memDirTpls = memDirTpls.split(delimiter)
    print("memDirTpls=", memDirTpls)
    print("len(memDirTpls)=",len(memDirTpls))
    for memDirTpl in memDirTpls:
        for imem in range(1,ensize+1):
            d = os.path.abspath( memDirTpl.format(imem) )
            if os.path.exists(d):
                print(f"clean_tmpdir: remove memDir: {d}")
                shutil.rmtree(d)
            else:
                print(f"warning: memDir ({d}) does not exist.")


def parse_cmd_line():
    parser = argparse.ArgumentParser(description=())
    parser.add_argument("--sharedDirs",required=True, default="./20190101T05_recenter", type=str,help=())
    parser.add_argument("--memDirTpls", required=True, default="./20190101T05_fcst{:04d}", type=str,help=())
    parser.add_argument("--ensize", required=True, default=1, type=int, help=())
    parser.add_argument("--delimiter",required=False, default=";",type=str,help=())
    parser.add_argument('--skip', action=argparse.BooleanOptionalAction,required=False, default=False)

    args = parser.parse_args()
   
    print(args)
    return args


if __name__ == '__main__':
    args = parse_cmd_line()
    if not args.skip:
        pass
        clean_tmpdir(args.sharedDirs, \
                     args.memDirTpls, \
                     args.delimiter, \
                     args.ensize)
