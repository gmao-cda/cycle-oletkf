#!/usr/bin/env python3

import os, sys, glob, argparse, datetime as dt, subprocess as sp
import shutil
#import yaml
#import hashlib

OCN_FLIST = ["ocean_hourly_*_*_*_*.nc",\
             "prog_z.nc", \
             "sfc_ave.nc"]
ATM_FLIST = ["*.geosgcm_pcp_cda.*.nc4",\
             "*.geosgcm_surf_cda.*.nc4",\
             "*.prog.eta.*.nc4",\
             "*.geosgcm_prog.*.nc4"]

def run_shell_cmd(cmd, wkdir, showError=False):
    p = sp.Popen(cmd, cwd=wkdir, shell=True,stdout=sp.PIPE, stderr=sp.PIPE)
    out, err = p.communicate()
    if showError: print("ERROR_MESSAGE={}".format(err.decode()))
    return out.decode()

def parse_cmd_line():
    parser = argparse.ArgumentParser(description=(""))
    parser.add_argument("--srcDir", required=True,help=(""))
    parser.add_argument("--dstDir", required=True,help=(""))
    parser.add_argument('--skip', action=argparse.BooleanOptionalAction,required=False, default=False)

    args = parser.parse_args()

    args.srcDir = os.path.abspath(args.srcDir)
    args.dstDir = os.path.abspath(args.dstDir)
    
    print(args)
    return args

def save_geos_output_hist( srcDir = os.path.abspath("./source_dir"), \
                      dstDir = os.path.abspath("./destiation_dir") ):

    if not os.path.exists(srcDir):
        raise RuntimeError("source Dir ({}) does not exsit".format(srcDir))
        sys.exit(1)

    if not os.path.exists(dstDir):
        print("Destination dir ({}) does not exist. create it now.".format(dstDir))
        os.makedirs(dstDir)

    
    pattern_list = OCN_FLIST + ATM_FLIST
    for pattern in pattern_list:
        print("="*80+"\n")
        flist = glob.glob(os.path.join(srcDir, pattern))
        nFiles = len(flist)
        print("Pattern {} has {} files".format(pattern, nFiles))
        if nFiles > 0:
            for f in flist:
                srcFile = f
                dstFile = os.path.join(dstDir,os.path.basename(f))
                print("mv: {} ---> {}".format(srcFile, dstFile))
                shutil.move(srcFile, dstFile)



if __name__ == '__main__':
    args = parse_cmd_line()
    if not args.skip:
        save_geos_output_hist(args.srcDir, args.dstDir)
