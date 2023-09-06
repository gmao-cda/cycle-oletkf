#!/usr/bin/env python3

import os, sys, glob, argparse, platform, datetime as dt, subprocess as sp
import shutil
from env_modules_python import module
#import yaml
#import hashlib

rstFiles = ["fvcore_internal_rst",
            "moist_internal_rst",
            "surf_import_rst"]

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


def run_das_recenter(wkdir         = os.path.abspath("./"), \
                     cntrDir       = os.path.abspath("./"), \
                     ensize        = 3,  \
                     recenterExec  = os.path.abspath("./recenter.x"), \
                     nprocs        = 3, \
                     bkgdPrefixTpl = "bkgd{:04d}", \
                     analPrefixTpl = "anal{:04d}",\
                     cntrPrefix    = "cntr",\
                     meanPrefix    = "bkgdmean",\
                     sprdPrefix    = "bkgdsprd",\
                     otherArgs     = None):
 
    if not os.path.exists(wkdir):
        raise RuntimeError(f"wkdir ({wkdir}) does not exist")
        sys.exit(1)

    if not os.path.exists(cntrDir):
        raise RuntimeError(f"cntrDir ({cntrDir}) does not exist")
        sys.exit(2)

    if not os.path.isfile(recenterExec):
        raise RuntimeError(f"recenterExec ({recenterExec}) does not exist.")
        sys.exit(3)

    if ensize != nprocs:
        raise RuntimeError(f"ensize ({ensize}) does not match with nprocs ({nprocs})")
        sys.exit(4)

    # link center files to wkdir
    # copy ens mean & sprd files to wkdir using center files as template
    timeStamp = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    for f in rstFiles:
        if not os.path.exists(os.path.join(cntrDir,f)):
            raise RuntimeError("center file ({}) does not exists".format(os.path.join(cntrDir,f)))
            sys.exit(5)
        else:
            cntrFile = "{}.{}".format(cntrPrefix,f)
            if os.path.exists(os.path.join(wkdir,cntrFile)):
                fRenamed  = f"{cntrFile}_renamed_{timeStamp}"
                subDirRenamed = f"cntrFiles_renamed_{timeStamp}"
                os.makedirs(os.path.join(wkdir,subDirRenamed),exist_ok=True)
                shutil.move(os.path.join(wkdir,cntrFile), os.path.join(wkdir,subDirRenamed,fRenamed))
            print("recenter::ln -sf:", os.path.join(cntrDir,f), "---->", os.path.join(wkdir,cntrFile))
            os.symlink(os.path.join(cntrDir,f), os.path.join(wkdir,cntrFile))

            meanFile = "{}.{}".format(meanPrefix,f)
            if os.path.exists(os.path.join(wkdir,meanFile)):
                fRenamed  = f"{meanFile}_renamed_{timeStamp}"
                subDirRenamed = f"meanFiles_renamed_{timeStamp}"
                os.makedirs(os.path.join(wkdir,subDirRenamed),exist_ok=True)
                shutil.move(os.path.join(wkdir,meanFile), os.path.join(wkdir,subDirRenamed,fRenamed))
            print("mean::cp:", os.path.join(cntrDir,f), "---->", os.path.join(wkdir,meanFile))
            shutil.copy2(os.path.join(cntrDir,f), os.path.join(wkdir,meanFile))

            sprdFile = "{}.{}".format(sprdPrefix,f)
            if os.path.exists(os.path.join(wkdir,sprdFile)):
                fRenamed  = f"{sprdFile}_renamed_{timeStamp}"
                subDirRenamed = f"sprdFiles_renamed_{timeStamp}"
                os.makedirs(os.path.join(wkdir,subDirRenamed),exist_ok=True)
                shutil.move(os.path.join(wkdir,sprdFile), os.path.join(wkdir,subDirRenamed,fRenamed))
            print("sprd::cp:", os.path.join(cntrDir,f), "---->", os.path.join(wkdir,sprdFile))
            shutil.copy2(os.path.join(cntrDir,f), os.path.join(wkdir,sprdFile))




    # check if anal/bkgd files are complete at wkdir
    for imem in range(1,ensize+1):
        bkgdPrefix = bkgdPrefixTpl.format(imem)
        analPrefix = analPrefixTpl.format(imem)
        files = [f"{bkgdPrefix}.{f}" for f in rstFiles ] + \
                [f"{analPrefix}.{f}" for f in rstFiles]
        #print("files=", files)
        for f in files:
            if not os.path.exists(os.path.join(wkdir,f)):
                raise RuntimeError(f"file ({f}) does not exit for recentering")
                sys.exit(5)


    # link exec
    if os.path.exists( os.path.join(wkdir,os.path.basename(recenterExec)) ):
        os.remove( os.path.join(wkdir,os.path.basename(recenterExec)) )
    os.symlink(recenterExec, os.path.join(wkdir,os.path.basename(recenterExec)))

    if os.path.exists(os.path.join(wkdir,"EGRESS")):
        os.remove(os.path.join(wkdir,"EGRESS"))

    shell_cmd = "mpirun -n {} ./{} -nbv {}".format(nprocs, os.path.basename(recenterExec),ensize)
    if otherArgs is not None:
        shell_cmd += " {}".format(otherArgs)
    print(shell_cmd)

    load_g5modules(site="NCCS")
    print(shell_cmd)
    rc, msgOut = run_shell_cmd(cmd=shell_cmd, wkdir=wkdir, showError=True)

    print(msgOut)
    print("\nreturn code={}\n".format(rc))

    if rc != 0:
        raise RuntimeError("command ({}) failed with return code {}".format(shell_cmd, rc))
        sys.exit(4)
    

    if not os.path.exists(os.path.join(wkdir,"EGRESS")):
        raise RuntimeError(f"end signal EGRESS not found under wkdir ({wkdir})")
        sys.exit(5)

def parse_cmd_line():
    parser = argparse.ArgumentParser(description=("run letkf"))
    parser.add_argument("wkdir", help=("where to run fcst"))
    parser.add_argument("--cntrDir", required=True, help=())
    parser.add_argument("--ensize", required=True, type=int, help=(""))
    parser.add_argument("--recenterExec", required=True, default=None, help=(""))
    parser.add_argument("--nprocs", required=True, type=int, default=1, help=(""))
    parser.add_argument("--bkgdPrefixTpl", required=True, default="bkgd{:04d}", help=())
    parser.add_argument("--analPrefixTpl", required=True, default="anal{:04d}", help=())
    parser.add_argument("--cntrPrefix", required=True, default="center", help=())
    parser.add_argument("--meanPrefix", required=True, default="bkgdmean", help=())
    parser.add_argument("--sprdPrefix", required=True, default="bkgdsprd", help=())
    parser.add_argument("--otherArgs",     required=False, type=str, default=None, help=())
    parser.add_argument('--skip', action=argparse.BooleanOptionalAction,required=False, default=False)

    args = parser.parse_args()

    args.wkdir = os.path.abspath(args.wkdir)
    args.recenterExec = os.path.abspath(args.recenterExec)
    args.nprocs = max(args.nprocs, 1)

    print(args)
    return args    


if __name__ == '__main__':
    args = parse_cmd_line()
    if not args.skip:
        run_das_recenter(args.wkdir, \
                     args.cntrDir, \
                     args.ensize, \
                     args.recenterExec, \
                     args.nprocs, \
                     args.bkgdPrefixTpl,\
                     args.analPrefixTpl,\
                     args.cntrPrefix, \
                     args.meanPrefix, \
                     args.sprdPrefix, \
                     args.otherArgs)
     
