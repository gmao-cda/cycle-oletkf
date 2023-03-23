#!/usr/bin/env python3
"""
scripts to prepare restart files required by teh GEOS-ESM.
"""

import os, sys, subprocess as sp
import glob
import datetime as dt
import argparse

def parse_cmd_line():
    parser = argparse.ArgumentParser(description=("prepare GEOS-ESM restart files "))
    parser.add_argument("wkdir", help=("directory prepared by gcm_setup"))
    parser.add_argument("restart_tar_file", help=("path to the restart tar file that usually under /restarts"))
    args = parser.parse_args()

    #print(args)
    return args

def prepare_restart_directory(wkdir=None, restart_tar_file=None):

    wkdir = os.path.abspath(wkdir)
    restart_tar_file = os.path.abspath(restart_tar_file)
    tar_file_name = os.path.basename(restart_tar_file)

    # untar the restart tar file
    os.symlink(restart_tar_file, os.path.join(wkdir,tar_file_name))
    sp.run(["tar","-xvf", tar_file_name], cwd=wkdir, check=True)
    os.unlink(os.path.join(wkdir,tar_file_name))

    # create cap_restart 
    flist = glob.glob(os.path.join(wkdir,"*_rst*.nc4"))
    restart_date_str = flist[0].split(".")[2]
    restart_date = dt.datetime.strptime(restart_date_str,"e%Y%m%d_%Hz") # e.g., e20160201_00z
    with open(os.path.join(wkdir,"cap_restart"),"w") as f:
        f.write(restart_date.strftime("%Y%m%d %H%M%S")) #e.g., 20160201 000000

    # rename atm, chemical, seaice restart files
    [os.rename(os.path.join(wkdir,f), os.path.join(wkdir,f.split(".")[1])) for f in flist]

    # rename ocean restart file dir
    ocn_dirname = "RESTART.{}".format(restart_date_str)
    os.rename(os.path.join(wkdir,ocn_dirname), os.path.join(wkdir,"RESTART"))

    print("DONE!")

if __name__ == '__main__':
    args = parse_cmd_line()
    prepare_restart_directory(args.wkdir, \
                              args.restart_tar_file)
