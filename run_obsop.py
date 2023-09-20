#!/usr/bin/env python3

import os, sys, glob, argparse, datetime as dt, subprocess as sp
import shutil
import yaml
#import hashlib

def run_shell_cmd(cmd, wkdir, showError=False):
    p = sp.Popen(cmd, cwd=wkdir, shell=True,stdout=sp.PIPE, stderr=sp.PIPE)
    out, err = p.communicate()
    if showError: print("ERROR_MESSAGE={}".format(err.decode()))
    return p.returncode, out.decode()


def run_single_obsop(wkdir="./", \
                     obsopExec="./OCN.obsOp_mom6.sss.x", \
                     rstFile="./MOM.res.nc", \
                     staticFile="./ocean_static.nc", \
                     topoFile="./ocean_topo.nc", \
                     nml="./input.nml",\
                     bkgdFile="./ocean_hourly_2017_01_01_01.nc",\
                     obsFile="./SMAP_L2B_SSS_36950_20220101T005200_R18240_V5.0.h5",\
                     hxFile="./obsout.dat", \
                     otherArgs=None):

    #print("run_single_obsop")
    if not os.path.isfile(obsopExec):
        raise RuntimeError("obsopExec ({}) does not exist.".format(obsopExec) )
        sys.exit(1)

    if not os.path.isfile(rstFile):
        raise RuntimeError("rstFile ({}) does not exist.".format(rstFile) )
        sys.exit(2)

    if not os.path.isfile(staticFile):
        raise RuntimeError("staticFile ({}) does not exist.".format(staticFile) )
        sys.exit(3)
    
    if not os.path.isfile(topoFile):
        raise RuntimeError("topoFile ({}) does not exist.".format(topoFile) )
        sys.exit(4)

    if not os.path.isfile(nml):
        raise RuntimeError("nml ({}) does not exist.".format(nml) )
        sys.exit(5)

    if not os.path.isfile(bkgdFile):
        raise RuntimeError("nml ({}) does not exist.".format(bkgdFile) )
        sys.exit(6)

    if not os.path.isfile(obsFile):
        raise RuntimeError("obsFile ({}) does not exist.".format(obsFile) )
        sys.exit(7)


    if os.path.exists(wkdir):
       wkdirRenamed=wkdir+dt.datetime.now().strftime("_renamed_%Y%m%dT%H%M%S")
       os.rename(wkdir, wkdirRenamed)
       print("wkdir ({}) already exists. rename the existing dir to {}.".format(wkdir, wkdirRenamed) )
    
    os.mkdir(wkdir)
    os.symlink(rstFile,    os.path.join(wkdir,"MOM.res.nc"))
    os.symlink(staticFile, os.path.join(wkdir,"ocean_static.nc"))
    os.symlink(topoFile,   os.path.join(wkdir,"ocean_topo.nc"))

    os.symlink(obsopExec,  os.path.join(wkdir,os.path.basename(obsopExec)))

    os.symlink(bkgdFile,   os.path.join(wkdir,os.path.basename(bkgdFile)))
    os.symlink(obsFile,   os.path.join(wkdir,os.path.basename(obsFile)))

    shutil.copy2(nml,   os.path.join(wkdir,"input.nml")) 

    shell_cmd="./{} -gues {} -obsin {} -obsout {} {}".format(\
                                   os.path.basename(obsopExec),\
                                   os.path.basename(bkgdFile), \
                                   os.path.basename(obsFile), \
                                   os.path.basename(hxFile), \
                                   otherArgs if otherArgs is not None else "")
    print(shell_cmd)

    rc, msgOut = run_shell_cmd(cmd=shell_cmd, wkdir=wkdir, showError=True)
    print(msgOut)
    print("\nreturn code={}\n".format(rc))

    if rc != 0:
        raise RuntimeError("command ({}) failed with return code {}".format(shell_cmd, rc))
        sys.exit(10)

    if not os.path.exists( os.path.join(wkdir, os.path.basename(hxFile)) ):
        raise RuntimeError("hxFile ({}) is not generated.".format(os.path.basename(hxFile)))
        sys.exit(11)

    if wkdir != os.path.dirname(hxFile):
        if not os.path.exists( os.path.dirname(hxFile) ):
            print("hxFile dir ({}) does not exist. creat it now.".format(os.path.dirname(hxFile)))
            os.makedirs(os.path.dirname(hxFile))

        shutil.move(os.path.join(wkdir, os.path.basename(hxFile)), hxFile)
    
    #print("end of run_single_obsop")


def parse_cmd_line():
    parser = argparse.ArgumentParser(description=("Prepare a directory to start GEOS-ESM forecast"))
    parser.add_argument("wkdir", help=("where to run fcst"))
    parser.add_argument("--obsopExec", required=True, default=None, help=(""))
    parser.add_argument("--rstFile", required=True, default=None, help=(""))
    parser.add_argument("--staticFile", required=True, default=None, help=(""))
    parser.add_argument("--topoFile", required=True, default=None, help=(""))
    parser.add_argument("--nml", required=True, default=None, help=(""))
    parser.add_argument("--bkgdFile", required=True, help=(""))
    parser.add_argument("--obsFile", required=True,help=())
    parser.add_argument("--hxFile", required=True,help=()) # out
    parser.add_argument("--otherArgs",required=False,default=None)
    parser.add_argument("--skip", action=argparse.BooleanOptionalAction,required=False, default=False)

    args = parser.parse_args()

    #args.fcstStartDate = dt.datetime.strptime(args.fcstStartDate,"%Y%m%dT%H")

    args.wkdir = os.path.abspath(args.wkdir)
    args.obsopExec = os.path.abspath(args.obsopExec)
    args.rstFile = os.path.abspath(args.rstFile)
    args.staticFile = os.path.abspath(args.staticFile)
    args.topoFile = os.path.abspath(args.topoFile)
    args.nml = os.path.abspath(args.nml)
    args.bkgdFile = os.path.abspath(args.bkgdFile)
    args.obsFile = os.path.abspath(args.obsFile)
    args.hxFile = os.path.abspath(args.hxFile)


    print(args)
    return args    


if __name__ == '__main__':
    args = parse_cmd_line()
    if not args.skip:
        run_single_obsop( args.wkdir, \
                      args.obsopExec, \
                      args.rstFile, \
                      args.staticFile, \
                      args.topoFile, \
                      args.nml, \
                      args.bkgdFile, \
                      args.obsFile, \
                      args.hxFile, \
                      args.otherArgs)

