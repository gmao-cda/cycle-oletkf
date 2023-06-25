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


def create_empty_dir(wkdir = "./"):
    if os.path.exists(wkdir):
       wkdirRenamed=wkdir+dt.datetime.now().strftime("_renamed_%Y%m%dT%H%M%S")
       os.rename(wkdir, wkdirRenamed)
       print("wkdir ({}) already exists. rename the existing dir to {}.".format(wkdir, wkdirRenamed) )

    os.mkdir(wkdir)
   

def parse_cmd_line():
    parser = argparse.ArgumentParser(description=("Prepare a directory to run letkf"))
    parser.add_argument("wkdir", help=("where to run letkf"))

    args = parser.parse_args()

    args.wkdir = os.path.abspath(args.wkdir)

    print(args)
    return args    


if __name__ == '__main__':
    args = parse_cmd_line()
    create_empty_dir(args.wkdir)

