#!/usr/bin/env python3

import os, sys, glob, argparse, datetime as dt, subprocess as sp
import shutil
import yaml
#import hashlib

def run_shell_cmd(cmd, wkdir):
    p = sp.Popen(cmd, cwd=wkdir, shell=True,stdout=sp.PIPE, stderr=sp.PIPE)
    out, err = p.communicate()
    #if showError: print("ERROR_MESSAGE={}".format(err.decode())) if p.returncode != 0 else print("NO ERROR")
    return p.returncode, out.decode(), err.decode()


def run_single_obsop(wkdir       = os.path.abspath("./"), \
                     obsopExec   = os.path.abspath("./OCN.obsOp_mom6.sss.x"), \
                     rstFile     = os.path.abspath("./MOM.res.nc"), \
                     staticFile  = os.path.abspath("./ocean_static.nc"), \
                     topoFile    = os.path.abspath("./ocean_topo.nc"), \
                     nml         = os.path.abspath("./input.nml"),\
                     bkgdFileTpl = os.path.abspath("./ocean_hourly_%Y_%m_%d_%H.nc"),\
                     obsFileTpl  = os.path.abspath("./%Y%m%dT%H.sss.h5"),\
                     hxFile      = os.path.abspath("./obsout.dat"), \
                     startDate   = dt.datetime(2019,1,1,6,0,0), \
                     endDate     = dt.datetime(2019,1,1,12,0,0), \
                     rinc        = 6, \
                     otherArgs   = None):

    print("START: run_single_obsop")
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

    cdate=startDate
    while cdate <= endDate:
        cdateBkgdFile = cdate.strftime(bkgdFileTpl)
        cdateObsFile  = cdate.strftime(obsFileTpl)

        if not os.path.isfile(cdateBkgdFile):
            raise RuntimeError("nml ({}) does not exist.".format(cdateBkgdFile) )
            sys.exit(6)

        if not os.path.isfile(cdateObsFile):
            raise RuntimeError("obsFile ({}) does not exist.".format(cdateObsFile) )
            sys.exit(7)

        cdate += dt.timedelta(hours=rinc)


    # create a new dir for obsop
    if os.path.exists(wkdir):
       wkdirRenamed=wkdir+dt.datetime.now().strftime("_renamed_%Y%m%dT%H%M%S")
       os.rename(wkdir, wkdirRenamed)
       print("wkdir ({}) already exists. rename the existing dir to {}.".format(wkdir, wkdirRenamed) )
    
    os.mkdir(wkdir)

    # link fixed files & exec
    os.symlink(rstFile,    os.path.join(wkdir,"MOM.res.nc"))
    os.symlink(staticFile, os.path.join(wkdir,"ocean_static.nc"))
    os.symlink(topoFile,   os.path.join(wkdir,"ocean_topo.nc"))
    os.symlink(obsopExec,  os.path.join(wkdir,os.path.basename(obsopExec)))

    shutil.copy2(nml,   os.path.join(wkdir,"input.nml")) #cp in case of further editing

    # generate hx for each time slot
    cdate=startDate
    while cdate <= endDate:
        cdateBkgdFile = cdate.strftime(bkgdFileTpl)
        cdateObsFile  = cdate.strftime(obsFileTpl)
        cdateHxFile = os.path.basename(hxFile) + cdate.strftime(".%Y%m%dT%H")

        #print("ln1: {} -> {}".format(cdateBkgdFile,   os.path.join(wkdir,os.path.basename(cdateBkgdFile))))
        #print("ln2: {} -> {}".format(cdateObsFile,    os.path.join(wkdir,os.path.basename(cdateObsFile))))

        os.symlink(cdateBkgdFile,   os.path.join(wkdir,os.path.basename(cdateBkgdFile)))
        os.symlink(cdateObsFile,    os.path.join(wkdir,os.path.basename(cdateObsFile)))

        shellCmd="./{} -gues {} -obsin {} -obsout {} {}".format(\
                                       os.path.basename(obsopExec),\
                                       os.path.basename(cdateBkgdFile), \
                                       os.path.basename(cdateObsFile), \
                                       os.path.basename(cdateHxFile), \
                                       otherArgs if otherArgs is not None else "")
        print(shellCmd)

        rc, msg, err = run_shell_cmd(cmd=shellCmd, wkdir=wkdir)
        print(msg) if rc == 0 else print(msg+"\nError:"+err)
        print("\nreturn code={}\n".format(rc))

        if rc != 0:
            raise RuntimeError("command ({}) failed with return code {}".format(shellCmd, rc))
            sys.exit(10)

        if not os.path.exists( os.path.join(wkdir, os.path.basename(cdateHxFile)) ):
            raise RuntimeError("hx file ({}) for time slot ({}) not generated. abort...".format(cdateHxFile, cdate.strftime(".%Y%m%dT%H")))
            sys.exit(11)

        cdate += dt.timedelta(hours=rinc)

    # aggrate slot hx to 1 file
    shellCmd = "cat {} >> {}".format(os.path.basename(hxFile)+".*", os.path.basename(hxFile))
    print(shellCmd)

    rs, msg, err = run_shell_cmd(cmd=shellCmd, wkdir=wkdir)
    print(msg) if rc == 0 else print(msg+"\nError:"+err)
    if rc != 0:
       raise RuntimeError("command ({}) failed with return code {}".format(shellCmd, rc))
       sys.exit(12)

    # check if the aggregated file is generated
    if not os.path.exists( os.path.join(wkdir, os.path.basename(hxFile)) ):
        raise RuntimeError("hxFile ({}) is not generated.".format(os.path.basename(hxFile)))
        sys.exit(13)

    # move the final aggregated file to saved dir
    if wkdir != os.path.dirname(hxFile):
        if not os.path.exists( os.path.dirname(hxFile) ):
            print("hxFile dir ({}) does not exist. create it now.".format(os.path.dirname(hxFile)))
            os.makedirs(os.path.dirname(hxFile))
        else:
            # rename the file with the same name in the save dir
            if os.path.exists(hxFile):
                hxFileRenamed = hxFile + dt.datetime.now().strftime("_renamed_%Y%m%dT%H%M%S")
                os.rename(hxFile, hxFileRenamed)
                print("hxFile ({}) already exists. rename it to {}.".format(hxFile, hxFileRenamed) )

        shutil.move(os.path.join(wkdir, os.path.basename(hxFile)), hxFile)
    
    print("END: run_single_obsop")


def parse_cmd_line():
    parser = argparse.ArgumentParser(description=("Prepare a directory to start GEOS-ESM forecast"))
    parser.add_argument("wkdir",                      type=str,default=None, help=("where to run fcst"))
    parser.add_argument("--obsopExec", required=True, type=str,default=None, help=(""))
    parser.add_argument("--rstFile",   required=True, type=str,default=None, help=(""))
    parser.add_argument("--staticFile",required=True, type=str,default=None, help=(""))
    parser.add_argument("--topoFile",  required=True, type=str,default=None, help=(""))
    parser.add_argument("--nml",       required=True, type=str,default=None, help=(""))
    parser.add_argument("--bkgdFileTpl",  required=True, type=str,help=(""))
    parser.add_argument("--obsFileTpl",   required=True, type=str,help=())
    parser.add_argument("--hxFile",    required=True, type=str,help=()) # out
    parser.add_argument("--startDate", required=True, type=str,default="201001010T06",metavar="YYYYMMDDHH", help=())
    parser.add_argument("--endDate",   required=False,type=str,default=None, metavar="YYYYMMDDHH", help=())
    parser.add_argument("--rinc",      required=False,type=int,default=0, help=("(hours)"))
    parser.add_argument("--otherArgs", required=False,type=str,default=None, help=("other args to obsop"))
    parser.add_argument('--skip', action=argparse.BooleanOptionalAction,required=False, default=False)

    args = parser.parse_args()

    #args.fcstStartDate = dt.datetime.strptime(args.fcstStartDate,"%Y%m%dT%H")

    args.wkdir = os.path.abspath(args.wkdir)
    args.obsopExec = os.path.abspath(args.obsopExec)
    args.rstFile = os.path.abspath(args.rstFile)
    args.staticFile = os.path.abspath(args.staticFile)
    args.topoFile = os.path.abspath(args.topoFile)
    args.nml = os.path.abspath(args.nml)
    args.bkgdFileTpl = os.path.abspath(args.bkgdFileTpl)
    args.obsFileTpl = os.path.abspath(args.obsFileTpl)
    args.hxFile = os.path.abspath(args.hxFile)


    args.startDate = dt.datetime.strptime(args.startDate,"%Y%m%dT%H")
    if args.endDate is None:
        args.endDate = args.startDate
    else:
        args.endDate = dt.datetime.strptime(args.endDate,"%Y%m%dT%H")


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
                      args.bkgdFileTpl, \
                      args.obsFileTpl, \
                      args.hxFile, \
                      args.startDate, \
                      args.endDate, \
                      args.rinc, \
                      args.otherArgs)

