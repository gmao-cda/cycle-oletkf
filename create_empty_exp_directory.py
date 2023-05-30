#!/usr/bin/env python3

import os, sys, subprocess as sp
import datetime as dt
import argparse

def parse_cmd_line():
    parser = argparse.ArgumentParser(description=("Generate an empty oletkf output directory"))
    parser.add_argument("expdir", help=("directory prepared by gcm_setup"))
    parser.add_argument("--members", required=True, default=10, type=int, help=("number of members"))
    parser.add_argument("--start_date", required=True, default="201901010000", help=("yyyymmddHH"))
    parser.add_argument("--end_date", default=None, help=("yyyymmddHH"))
    parser.add_argument("--tinc", default=6, type=int, help=("time interval between two day cycles (unit: hours)"))
    args = parser.parse_args()

    args.expdir = os.path.abspath(args.expdir)
    if args.members < 0:
        raise RuntimeError("members ({}) <0. exit...".format(members))
        sys.exit(1)
    args.start_date = dt.datetime.strptime(args.start_date,"%Y%m%d%H")
    if args.end_date is None:
        args.end_date = args.start_date
    else:
        args.end_date = dt.datetime.strptime(args.end_date,"%Y%m%d%H") 
    args.tinc = dt.timedelta(hours=args.tinc)
    
    print(args)
    return args

def generate_output_directory(expdir=None, \
                              members=10, \
                              sdate=dt.datetime(2019,1,1,0,0), \
                              edate=dt.datetime(2019,1,2,0,0), \
                              tinc=dt.timedelta(hours=6)):
    expdir = os.path.abspath(expdir)
    if os.path.exists(expdir):
        raise RuntimeError("experiment directory ({}) already exists. exit...".format(expdir))
        sys.exit(1)
    else:
        os.mkdir(expdir)

    subdirs = {'anal':    {'has_tdim':True, 'has_edim':True}, \
               'bkgd':    {'has_tdim':True, 'has_edim':True}, \
               'obsbkgd': {'has_tdim':True, 'has_edim':True}, \
               'obs':     {'has_tdim':True, 'has_edim':False}, \
               'cfg':     {'has_tdim':False,'has_edim':False} }

    # cmems list all all subdir names if a directory has_edim=True
    cmems = ["{:04d}".format(imem) for imem in range(1,members+1)]
    cmems += ["mean","sprd"]

    for subdir in subdirs.keys():
        dir_path = os.path.join(expdir,subdir)
        print(dir_path)
        os.mkdir(dir_path) 
        
        if subdirs[subdir]['has_tdim']:
            cdate = sdate
            while cdate <= edate:
                if subdirs[subdir]['has_edim']:
                    for cmem in cmems:
                        dir_path = os.path.join(expdir,subdir,cmem,cdate.strftime("%Y%m%dT%H"))
                        os.makedirs(dir_path)
                        print(dir_path)
                else:
                    dir_path = os.path.join(expdir,subdir,cdate.strftime("%Y%m%dT%H"))
                    os.makedirs(dir_path)
                    print(dir_path)
                cdate += tinc

    print("DONE!")

if __name__ == '__main__':
    args = parse_cmd_line()
    generate_output_directory(args.expdir, \
                              args.members, \
                              args.start_date, \
                              args.end_date, \
                              args.tinc)
