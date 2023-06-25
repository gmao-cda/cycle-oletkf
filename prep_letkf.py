#!/usr/bin/env python3

import os, sys, glob, argparse, datetime as dt, subprocess as sp
import shutil
#import yaml
#import hashlib

def run_shell_cmd(cmd, wkdir, showError=False):
    p = sp.Popen(cmd, cwd=wkdir, shell=True,stdout=sp.PIPE, stderr=sp.PIPE)
    out, err = p.communicate()
    if showError: print("ERROR_MESSAGE={}".format(err.decode()))
    return p.returncode, out.decode()


def prep_letkf_1mem(wkdir = "./", \
                    bkgdFile1="./MOM.res.nc", \
                    bkgdFile2="./MOM.res_1.nc", \
                    obsFile="./obs01001.dat", \
                    member=1):
   
    if not os.path.exists(wkdir):
        raise RuntimeError("wkdir ({}) does not exist".format(wkdir))
        sys.exit(1)

    if not os.path.isfile(bkgdFile1):
        raise RuntimeError("bgkdFile1 ({}) does not exist.".format(bkgdFile1))
        sys.exit(2)

    if not os.path.isfile(bkgdFile2):
        raise RuntimeError("bgkdFile2 ({}) does not exist.".format(bkgdFile2))
        sys.exit(3)

    if not os.path.isfile(obsFile):
        raise RuntimeError("obsFile ({}) does not exist.".format(obsFile))
        sys.exit(4)

    daObsFile = "obs01{:03d}.dat".format(member)
    daBkgdFile1 = "gs01{:03d}.MOM.res.nc".format(member)
    daBkgdFile2 = "gs01{:03d}.MOM.res_1.nc".format(member)
    daAnalFile1 = "anal{:03d}.MOM.res.nc".format(member)
    daAnalFile2 = "anal{:03d}.MOM.res_1.nc".format(member)

    print("daObsFile=",daObsFile)
    print("daBkgdFile1=",daBkgdFile1)
    print("daBkgdFile2=",daBkgdFile2)
    print("daAnalFile1=",daAnalFile1)
    print("daAnalFile2=",daAnalFile2)
    

    # link obsfile & bgkdFile
    os.symlink(obsFile,   os.path.join(wkdir, daObsFile))
    os.symlink(bkgdFile1, os.path.join(wkdir, daBkgdFile1))
    if bkgdFile2 != bkgdFile1: 
        os.symlink(bgkdFile2, os.path.join(wkdir, daBkgdFile2))

    # copy files
    shutil.copy2(bkgdFile1, os.path.join(wkdir, daAnalFile1))
    if bkgdFile2 != bkgdFile1:
        shutil.copy2(bgkdFile2, os.path.join(wkdir, daAnalFile2))



def parse_cmd_line():
    parser = argparse.ArgumentParser(description=("Prepare a directory to start GEOS-ESM forecast"))
    parser.add_argument("wkdir", help=("where to run fcst"))
    parser.add_argument("--bkgdFile1", required=True, help=(""))
    parser.add_argument("--bkgdFile2", required=False, default=None,help=())
    parser.add_argument("--obsFile",required=True,help=(""))
    parser.add_argument("--member", required=True,type=int,help=("which member"))

    args = parser.parse_args()

    #args.fcstStartDate = dt.datetime.strptime(args.fcstStartDate,"%Y%m%dT%H")

    args.wkdir = os.path.abspath(args.wkdir)
    args.bkgdFile1 = os.path.abspath(args.bkgdFile1)
    if args.bkgdFile2 is None: 
        args.bkgdFile2 = args.bkgdFile1
    else:
        args.bkgdFile2 = os.path.abspath(args.bkgdFile2)
    args.obsFile = os.path.abspath(args.obsFile)


    print(args)
    return args    


if __name__ == '__main__':
    args = parse_cmd_line()
    prep_letkf_1mem(args.wkdir, \
                    args.bkgdFile1, \
                    args.bkgdFile2, \
                    args.obsFile, \
                    args.member)

