#!/usr/bin/env python3

import os, sys, glob, argparse, datetime as dt, subprocess as sp
import shutil
#import yaml
#import hashlib


def parse_cmd_line():
    parser = argparse.ArgumentParser(description=(""))
    parser.add_argument("letkfDir",help=(""))
    parser.add_argument("--bkgdMeanDir", required=True, help=(""))
    parser.add_argument("--bkgdSprdDir", required=True, help=(""))
    parser.add_argument("--analMeanDir", required=True, help=(""))
    parser.add_argument("--analSprdDir", required=True, help=(""))
    parser.add_argument("--ombDir",required=True, help=(""))
    parser.add_argument("--skip", action=argparse.BooleanOptionalAction,required=False, default=False)

    args = parser.parse_args()

    args.letkfDir = os.path.abspath(args.letkfDir)
    args.bkgdMeanDir = os.path.abspath(args.bkgdMeanDir)
    args.bkgdSprdDir = os.path.abspath(args.bkgdSprdDir)
    args.analMeanDir = os.path.abspath(args.analMeanDir)
    args.analSprdDir = os.path.abspath(args.analSprdDir)
    args.ombDir = os.path.abspath(args.ombDir)
    
    print(args)
    return args

def save_letkf_diag_output( letkfDir    = os.path.abspath("./"), \
                            bkgdMeanDir = os.path.abspath("./"), \
                            bkgdSprdDir = os.path.abspath("./"), \
                            analMeanDir = os.path.abspath("./"), \
                            analSprdDir = os.path.abspath("./"), \
                            ombDir      = os.path.abspath("./") ):
    if not os.path.exists(letkfDir):
        raise RuntimeError("letkfDir ({}) does not exist.".format(letkfDir))
        sys.exit(1)
    
    dnames = ["bkgdMeanDir", "bkgdSrpdDir", "analMeanDir", "analSprdDir", "ombDir"]
    dirs = [bkgdMeanDir, bkgdSprdDir, analMeanDir, analSprdDir, ombDir]
    files = ["gues_me.grd","gues_sp.grd","anal_me.grd","anal_sp.grd","omb_mean.dat"]

    for dnm, d, f in zip(dnames,dirs,files):
        srcPath = os.path.join(letkfDir, f)
        dstPath = os.path.join(d, f)
        if os.path.exists( srcPath ):
            # make dstDir check if dstDir does not exit
            if not os.path.exists( os.path.dirname(dstPath) ):
                print("make {} ({})".format(dnm,d))
                os.makedirs( os.path.dirname(dstPath) )
            else: # check if file with the same name already exist there
                if os.path.exists(dstPath):
                    dstPathRenamed = dstPath + dt.datetime.now().strftime("_renamed_%Y%m%dT%H%M%S")
                    print("Warning: file ({}) already exists there. rename it as {}".format(dstPath,dstPathRenamed))
                    os.rename(dstPath, dstPathRenamed)
            print("{}: {} --> {}".format(dnm, srcPath, dstPath))
            shutil.move(srcPath,dstPath)


if __name__ == '__main__':
    args = parse_cmd_line()
    if not args.skip:
        save_letkf_diag_output( args.letkfDir, \
                            args.bkgdMeanDir, \
                            args.bkgdSprdDir, \
                            args.analMeanDir, \
                            args.analSprdDir, \
                            args.ombDir )
