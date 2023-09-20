#!/usr/bin/env python3

import os, sys, glob, argparse, platform, datetime as dt, subprocess as sp
import shutil
from env_modules_python import module
#import yaml
#import hashlib

def load_g5modules(site="NCCS"):
    """
    dirty verion that only works on NCCS discover and my gcm version
    """
    #module("purge")

    if site == "NCCS":
        # usemods
        usemods = ["/discover/swdev/gmao_SIteam/modulefiles-SLES12"]
        for usemod in usemods:
            module("use", "-a", usemod)
        #mods
        mods = ["GEOSenv", \
                "comp/gcc/10.3.0", \
                "comp/intel/2021.6.0", \
                "mpi/impi/2021.6.0", \
                "python/GEOSpyD/Min4.11.0_py3.9_AND_Min4.8.3_py2.7"]
        for mod in mods:
            module("load",mod)

        module("list")

        basedir = "/discover/swdev/gmao_SIteam/Baselibs/ESMA-Baselibs-7.5.0/x86_64-pc-linux-gnu/ifort_2021.6.0-intelmpi_2021.6.0"
        arch = platform.system() # e.g., "Linux", "Darwin"
        baselib_path = "{}/{}/lib".format(basedir, arch)
        if "LD_LIBRARY_PATH" not in os.environ.keys():
            os.environ["LD_LIBRARY_PATH"] = baselib_path
        else:
            if baselib_path not in os.environ["LD_LIBRARY_PATH"]:
                os.environ["LD_LIBRARY_PATH"] += ":{}".format(baselib_path)

        if "LD_LIBRARY64_PATH" not in os.environ.keys():
            os.environ["LD_LIBRARY64_PATH"] = baselib_path
        else:
            if baselib_path not in os.environ["LD_LIBRARY64_PATH"]:
                os.environ["LD_LIBRARY64_PATH"] += ":{}".format(baselib_path)


def run_shell_cmd(cmd, wkdir, showError=False):
    p = sp.Popen(cmd, cwd=wkdir, shell=True,stdout=sp.PIPE, stderr=sp.PIPE)
    out, err = p.communicate()
    if showError: print("ERROR_MESSAGE={}".format(err.decode()))
    return p.returncode, out.decode()


def run_das_letkf(wkdir="./", \
                  ensize = 10, \
                  letkfExec="./OCN.obsOp_mom6.sss.x", \
                  nprocs=10, \
                  rstFile="./MOM.res.nc", \
                  staticFile="./ocean_static.nc", \
                  topoFile="./ocean_topo.nc", \
                  nml="./input.nml",\
                  bkgdFile1Tpl="gs01#MEMBER#.MOM.res.nc",\
                  bkgdFile2Tpl="gs01#MEMBER#.MOM.res_1.nc",\
                  analFile1Tpl="anal#MEMBER#.MOM.res.nc", \
                  analFile2Tpl="anal#MEMBER#.MOM.res_1.nc", \
                  obsFileTpl="obs01#MEMBER#.dat", \
                  strLength = 3):

    if bkgdFile1Tpl.find("#MEMBER#") < 0 or bkgdFile2Tpl.find("#MEMBER#") < 0:
        raise RuntimeError("bgkdFile1Tpl ({}) or bkgdFile2Tpl ({})cannot find string #MEMBER#".format(\
                           bkgdFile1Tpl, bkgdFile2Tpl))
        sys.exit(1)

    if analFile1Tpl.find("#MEMBER#") < 0 or analFile2Tpl.find("#MEMBER#") < 0:
        raise RuntimeError("analFile1Tpl ({}) or analFile2Tpl ({}) cannot find string #MEMBER#".format(\
                           analFile1Tpl, analFile2Tpl))
        sys.exit(2)

    if obsFileTpl.find("#MEMBER#") < 0:
        raise RuntimeError("obsFileTpl ({}) cannot find string #MEMBER#".format(obsFileTpl))
        sys.exit(3)


    if not os.path.isfile(letkfExec):
        raise RuntimeError("letkfExec ({}) does not exist.".format(letkfExec) )
        sys.exit(4)

    if not os.path.isfile(rstFile):
        raise RuntimeError("rstFile ({}) does not exist.".format(rstFile) )
        sys.exit(5)

    if not os.path.isfile(staticFile):
        raise RuntimeError("staticFile ({}) does not exist.".format(staticFile) )
        sys.exit(6)
    
    if not os.path.isfile(topoFile):
        raise RuntimeError("topoFile ({}) does not exist.".format(topoFile) )
        sys.exit(7)

    if not os.path.isfile(nml):
        raise RuntimeError("nml ({}) does not exist.".format(nml) )
        sys.exit(8)

    if not os.path.exists(wkdir):
       raise RuntimeError("wkdir ({}) does not exist".format(wkdir))
       sys.exit(9)

    strFmt = "{" + ":0{}d".format(strLength) + "}"
    fileTplList = [bkgdFile1Tpl, bkgdFile2Tpl, analFile1Tpl, analFile2Tpl, obsFileTpl]
    for imem in range(1, ensize+1):
        #print("----------")
        for tpl in fileTplList:
            file =  tpl.replace("#MEMBER#", strFmt.format(imem))
            print(file)
            if not os.path.exists( os.path.join(wkdir,file) ):
               raise RuntimeError("File ({}) required by LETKF does not exist.".format(file))
               sys.exit(10)

    # link necesary files
    suffix=dt.datetime.now().strftime("_renamed_%Y%m%dT%H%M%S")
    lnFileList = ["MOM.res.nc", "ocean_static.nc", "ocean_topo.nc", os.path.basename(letkfExec)]
    for file in lnFileList:
        if os.path.exists(os.path.join(wkdir, file)):
            newfile = "{}{}".format(file, suffix)
            os.rename(os.path.join(wkdir, file), \
                      os.path.join(wkdir, newfile) )

    os.symlink(rstFile,    os.path.join(wkdir, "MOM.res.nc"))
    os.symlink(staticFile, os.path.join(wkdir, "ocean_static.nc"))
    os.symlink(topoFile,   os.path.join(wkdir, "ocean_topo.nc"))
    os.symlink(letkfExec,  os.path.join(wkdir, os.path.basename(letkfExec)))

    # generate namelist
    with open(nml, "r") as fin:
        lines = fin.readlines()
    with open(os.path.join(wkdir, "input.nml"), "w") as fout:
        for l in lines:
            fout.write(l.replace("#MEMBER#", str(ensize)))

    shell_cmd = "mpirun -n {} ./{}".format(nprocs, os.path.basename(letkfExec))

    load_g5modules(site="NCCS")
    print(shell_cmd)
    rc, msgOut = run_shell_cmd(cmd=shell_cmd, wkdir=wkdir, showError=True)

    print(msgOut)
    print("\nreturn code={}\n".format(rc))

    if rc != 0:
        raise RuntimeError("command ({}) failed with return code {}".format(shell_cmd, rc))
        sys.exit(11)
    


def parse_cmd_line():
    parser = argparse.ArgumentParser(description=("run letkf"))
    parser.add_argument("wkdir", help=("where to run fcst"))
    parser.add_argument("--ensize", required=True, type=int, help=(""))
    parser.add_argument("--letkfExec", required=True, default=None, help=(""))
    parser.add_argument("--nprocs", required=True, type=int, default=1, help=(""))
    parser.add_argument("--rstFile", required=True, default=None, help=(""))
    parser.add_argument("--staticFile", required=True, default=None, help=(""))
    parser.add_argument("--topoFile", required=True, default=None, help=(""))
    parser.add_argument("--nml", required=True, default=None, help=(""))
    parser.add_argument("--bkgdFile1Tpl", required=True, help=(""))
    parser.add_argument("--bkgdFile2Tpl", required=False, default=None,help=(""))
    parser.add_argument("--obsFileTpl", required=True,help=())
    parser.add_argument("--analFile1Tpl", required=True,help=())
    parser.add_argument("--analFile2Tpl", required=False, default=None,help=())
    parser.add_argument("--strLength", required=False, type=int, default=3, help=())
    parser.add_argument("--skip", action=argparse.BooleanOptionalAction,required=False, default=False)

    args = parser.parse_args()

    args.wkdir = os.path.abspath(args.wkdir)
    args.letkfExec = os.path.abspath(args.letkfExec)
    args.rstFile = os.path.abspath(args.rstFile)
    args.staticFile = os.path.abspath(args.staticFile)
    args.topoFile = os.path.abspath(args.topoFile)
    args.nml = os.path.abspath(args.nml)
    args.nprocs = max(args.nprocs, 1)

    if args.bkgdFile2Tpl is None: 
        args.bkgdFile2Tpl = args.bkgdFile1Tpl

    if args.analFile2Tpl is None:
        args.analFile2Tpl = args.analFile1Tpl

    print(args)
    return args    


if __name__ == '__main__':
    args = parse_cmd_line()
    if not args.skip:
        run_das_letkf(args.wkdir, \
                  args.ensize, \
                  args.letkfExec, \
                  args.nprocs, \
                  args.rstFile, \
                  args.staticFile, \
                  args.topoFile, \
                  args.nml,\
                  args.bkgdFile1Tpl,\
                  args.bkgdFile2Tpl,\
                  args.analFile1Tpl, \
                  args.analFile2Tpl, \
                  args.obsFileTpl, \
                  args.strLength )
     
