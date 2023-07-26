#!/usr/bin/env python3

import os, sys, glob, argparse, datetime as dt, subprocess as sp
import shutil
#import yaml
#import hashlib

flistArchived = ["achem_internal_rst", "aiau_import_rst", "cabc_internal_rst", "cabr_internal_rst", "caoc_internal_rst",\
             "catch_internal_rst", "du_internal_rst", "fvcore_internal_rst", "gocart_import_rst", "gocart_internal_rst", \
             "gwd_import_rst",  "hemco_import_rst", "hemco_internal_rst", "irrad_internal_rst", "lake_internal_rst", \
             "landice_internal_rst", "moist_import_rst", "moist_internal_rst", "ni_internal_rst", "ocean_internal_rst", \
             "openwater_internal_rst", "pchem_internal_rst", "saltwater_import_rst", "seaice_import_rst", "seaice_internal_rst", \
             "seaicethermo_internal_rst", "solar_internal_rst", "ss_internal_rst", "su_internal_rst", "surf_import_rst", \
             "tr_import_rst", "tr_internal_rst", "turb_import_rst", "turb_internal_rst"]


def run_shell_cmd(cmd, wkdir, showError=False):
    p = sp.Popen(cmd, cwd=wkdir, shell=True,stdout=sp.PIPE, stderr=sp.PIPE)
    out, err = p.communicate()
    if showError: print("ERROR_MESSAGE={}".format(err.decode()))
    return out.decode()

def parse_cmd_line():
    parser = argparse.ArgumentParser(description=(""))
    parser.add_argument("srcDir", help=(""))
    parser.add_argument("dstDir", help=(""))

    args = parser.parse_args()

    args.srcDir = os.path.abspath(args.srcDir)
    args.dstDir = os.path.abspath(args.dstDir)
    
    print(args)
    return args

def save_geos_output( srcDir = os.path.abspath("./source_dir"), \
                      dstDir = os.path.abspath("./destiation_dir") ):

    if not os.path.exists(srcDir):
        raise RuntimeError("source Dir ({}) does not exsit".format(srcDir))
        sys.exit(1)

    if not os.path.exists(dstDir):
        print("Destination dir ({}) does not exist. create it now.".format(dstDir))
        os.makedirs(dstDir)

    # move the non-MOM6 restart files
    ## get the file list of checkpoints
    srcPathList = glob.glob(os.path.join(srcDir,"*_checkpoint"))
    srcPathList_hist = glob.glob(os.path.join(srcDir,"geosgcm_*_checkpoint")) #
    srcPathList = [s for s in srcPathList if s not in srcPathList_hist]
    print(srcPathList)
    if len(flistArchived) != len(srcPathList):
        print("num of *_checkpoint file = ".format(len(srcPathList)))
        print("num of predefined _rst file = ".format(len(flistArchived)))
        raise RuntimeError("num of *_checkpoint file ({len(srcPathList)}) not the same as the predefined number ({len(flistArchived)})")
        sys.exit(2)

    for srcPath in srcPathList:
        srcFile = os.path.basename(srcPath)
        dstFile = srcFile.replace("checkpoint","rst")
        dstPath = os.path.join(dstDir, dstFile)

        print("{} ---> {}".format(srcPath, dstPath))

        if os.path.exists(dstPath):
            dstPathRenamed = dstPath + dt.datetime.now().strftime("_renamed_%Y%m%dT%H%M%S")
            print("Warning: file ({}) already exists there. rename it as {}".format(dstPath,dstPathRenamed))
            os.rename(dstPath, dstPathRenamed)

        shutil.move(srcPath, dstPath)



    # move the MOM6 restart files
    ocnSrcDir = os.path.join(srcDir, "RESTART")
    if not os.path.exists(ocnSrcDir):
        raise RuntimeError("MOM6 restart dir ({}) does not exist".format(ocnSrcDir))
        sys.exit(3)

    ocnDstDir = os.path.join(dstDir, "RESTART")
    if os.path.exists(ocnDstDir):
       ocnDstDirRenamed = ocnDstDir + dt.datetime.now().strftime("_renamed_%Y%m%dT%H%M%S")
       print("Warning: ocn bkgd dir ({}) already exists there. rename it as {}".format(ocnDstDir,ocnDstDirRenamed))
       os.rename(ocnDstDir, ocnDstDirRenamed)

    shutil.move(ocnSrcDir, ocnDstDir)


if __name__ == '__main__':
    args = parse_cmd_line()
    save_geos_output(args.srcDir, args.dstDir)
