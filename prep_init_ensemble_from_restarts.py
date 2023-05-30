#!/usr/bin/env python3

import os, sys, glob, argparse, datetime as dt, subprocess as sp
import yaml

def parse_cmd_line():
    parser = argparse.ArgumentParser(description=("Generate an empty oletkf output directory"))
    parser.add_argument("expdir", help=("directory prepared by gcm_setup"))
    parser.add_argument("--members", required=True, default=10, type=int, help=("number of members"))
    parser.add_argument("--start_date", required=True, default="201901010000", help=("yyyymmddHH"))
    parser.add_argument("--cfg_file", required=True, default="init_member_mapping.yaml", help=("yaml file including initial member mappings"))
    parser.add_argument("--dry_run", default=False, action="store_true",help=("only check the completeness of files, dirs and show the moving flow."))
    args = parser.parse_args()

    args.expdir = os.path.abspath(args.expdir)
    if args.members < 0:
        raise RuntimeError("members ({}) <0. exit...".format(members))
        sys.exit(1)
    args.start_date = dt.datetime.strptime(args.start_date,"%Y%m%d%H")

    args.cfg_file = os.path.abspath(args.cfg_file)
    
    print(args)
    return args

def generate_init_ensemble(expdir=None, \
                           members=10, \
                           sdate=dt.datetime(2019,1,1,0,0), \
                           cfg_file="init_member_mapping.yaml",\
                           dry_run=True):
    with open(cfg_file, "r") as f:
        cfg = yaml.safe_load(f)

    nml_name="initial_ensemble_mapping"
    if members != len(cfg[nml_name]):
        raise RuntimeError("the input ensemble size is not equal to the # of restart files in {}.".format(cfg_file))
        sys.exit(2)

    # check if the path_to and tarfile are ready for init members
    mappings={}
    for m in range(1,members+1):
        cmem="{:04d}".format(m)
        cdate=sdate.strftime("%Y%m%dT%H")

        # generate path_to  & check if it exists and empty
        memBkgdDir=os.path.join(expdir,"bkgd",cmem,cdate)  # e.g., expdir/bkgd/0001/20220101T00
        memAnalDir=os.path.join(expdir,"anal",cmem,cdate)  # e.g., expdir/anal/0001/20220101T00

        for memdir in [memBkgdDir, memAnalDir]:
            if not os.path.isdir(memdir):
                raise RuntimeError("directory to store the initial member{} ({}) does not exist".format(cmem,memdir))
                exit(3)
            else:
                if os.listdir(memdir): # not empty dir
                    print(os.listdir(memdir))
                    raise RuntimeError("directory {} is not empty. stop".format(memdir))
                    exit(4)
             
        # generate tarfile_from & check if it exists
        tarfile=cfg[nml_name]["member{}".format(cmem)]
        if not os.path.exists(tarfile):
            raise RuntimeError("tar file of member{} ({}) does not exist".format(cmem, tarfile))
            exit(5)

        # store the mapping for each member
        mappings[m] = [memBkgdDir, memAnalDir, tarfile]


    for m in range(1,members+1):
        memBkgdDir, memAnalDir, tarfile = mappings[m]
        print("member_{}: {}\n{} <--- {}\n".format(m, memBkgdDir, memAnalDir, tarfile))

    if not dry_run:
        for m in range(1,members+1):
            memBkgdDir, memAnalDir, tarfile = mappings[m]
            move_restart(memBkgdDir, memAnalDir, tarfile)

        
    print("DONE!")

def move_restart(bkgdDir=None, analDir=None, tarfile=None):

    bkgdDir = os.path.abspath(bkgdDir)
    analDir = os.path.abspath(analDir)
    tarfile = os.path.abspath(tarfile)
    tarfileName = os.path.basename(tarfile)

    # bkgdDir: untar the restart tar file
    os.symlink(tarfile, os.path.join(bkgdDir,tarfileName))
    sp.run(["tar","-xvf", tarfileName], cwd=bkgdDir, check=True)
    os.unlink(os.path.join(bkgdDir,tarfileName))

    # bkgdDir: create cap_restart
    flist = glob.glob(os.path.join(bkgdDir,"*_rst*.nc4"))
    cRestartDate = flist[0].split(".")[2]
    restartDate = dt.datetime.strptime(cRestartDate,"e%Y%m%d_%Hz") # e.g., e20160201_00z
    with open(os.path.join(bkgdDir,"init_ensemble_info.txt"),"w") as f:
        f.write(restartDate.strftime("%Y%m%d %H%M%S\n")) #e.g., 20160201 000000
        f.write("init_tarfile: {}\n".format(tarfile))
        f.write("init_bkgd_dir: {}\n".format(bkgdDir))
        f.write("init_anal_dir: {}\n".format(analDir))

    # bkgdDir: rename atm, chemical, seaice restart files: trim the prefix and suffix
    # 5deg.solar_internal_rst.e20160101_06z.GEOSgcm-v10.23.0.CF0012x6C_TM0072xTM0036_CF0012x6C_DE0360xPE0180.nc4 => solar_internal_rst
    [os.rename(os.path.join(bkgdDir,f), os.path.join(bkgdDir,f.split(".")[1])) for f in flist]

    # bkgdDir: rename ocean restart file dir & move it to analDir
    ocn_dirname = "RESTART.{}".format(cRestartDate)
    os.rename(os.path.join(bkgdDir,ocn_dirname), os.path.join(analDir,"RESTART"))

    print("DONE!")


if __name__ == '__main__':
    args = parse_cmd_line()
    generate_init_ensemble(args.expdir, \
                              args.members, \
                              args.start_date, \
                              args.cfg_file, \
                              args.dry_run)
