#!/usr/bin/env python3

import shutil, os, sys, argparse, datetime as dt

def copy_init_ensemble_from_exp(expDir = os.path.abspath('./new_exp_dir'), \
                                members = 1, \
                                srcExpDir = os.path.abspath('./old_exp_dir'), \
                                cycleDate = dt.datetime(2019,1,1,6,0,0), \
                                dryRun = True):
    
    expDir    = os.path.abspath(expDir)
    srcExpDir = os.path.abspath(srcExpDir)
    for m in range(1,members+1):
        print("-"*80+"\n", "generating IC for member {:04d}".format(m))
        srcMemBkgdDir = os.path.join(srcExpDir, "bkgd", "{:04d}".format(m), cycleDate.strftime("%Y%m%dT%H"))
        dstMemBkgdDir = os.path.join(expDir,    "bkgd", "{:04d}".format(m), cycleDate.strftime("%Y%m%dT%H"))
        print("BKGD DIR:", srcMemBkgdDir, "---->", dstMemBkgdDir) 
        if not dryRun:
            shutil.copytree(srcMemBkgdDir, dstMemBkgdDir, dirs_exist_ok=True)

        srcMemAnalDir = os.path.join(srcExpDir, "anal", "{:04d}".format(m), cycleDate.strftime("%Y%m%dT%H"))
        dstMemAnalDir = os.path.join(expDir,    "anal", "{:04d}".format(m), cycleDate.strftime("%Y%m%dT%H"))
        print("ANAL DIR:", srcMemAnalDir, "---->", dstMemAnalDir) 
        if not dryRun:
            shutil.copytree(srcMemAnalDir, dstMemAnalDir, dirs_exist_ok=True)


    print("DONE!")

def parse_cmd_line():
    parser = argparse.ArgumentParser(description=("Generate an empty oletkf output directory"))
    parser.add_argument("expDir", help=("directory for saving letkf exp outputs"))
    parser.add_argument("--members", required=True, default=10, type=int, help=("number of members"))
    parser.add_argument("--cycleDate", required=True, default="2019010206", help=("yyyymmddHH"))
    parser.add_argument("--srcExpDir", required=True, default="./source_exp_dir", help=("source exp dir"))
    parser.add_argument("--dryRun", default=False, action="store_true",help=("only check the completeness of files, dirs and show the moving flow."))
    args = parser.parse_args()

    args.expDir = os.path.abspath(args.expDir)
    if args.members < 0:
        raise RuntimeError("members ({}) <0. exit...".format(members))
        sys.exit(1)
    args.cycleDate = dt.datetime.strptime(args.cycleDate,"%Y%m%d%H")

    
    print(args)
    return args


if __name__ == '__main__':
    print(" ".join(sys.argv))
    args = parse_cmd_line()
    copy_init_ensemble_from_exp(args.expDir, \
                           args.members, \
                           args.srcExpDir, \
                           args.cycleDate, \
                           args.dryRun)
