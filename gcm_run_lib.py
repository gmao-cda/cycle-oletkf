#import numpy as np
#import datetime as dt
import os, sys, shutil, platform, glob
import subprocess as sp
from config_tools import Config
from env_modules_python import module  #lmod

def calc_num_model_nodes(model_npes, ncpus_per_node):
    x = model_npes / ncpus_per_node
    y = int(x)
    return y+1 if x>y else y

def run_grep(cmd, wkdir):
    return sp.Popen(cmd, cwd=wkdir, shell=True,stdout=sp.PIPE).communicate()[0].decode()

class ConfigGcmRun(Config):
    def __init__(self):
        self.geosdir  = None
        self.geosbin  = None
        self.geosetc  = None
        self.geosutil = None
        self.gcmver   = None
        self.arch     = None
        self.site     = None
        self.basedir  = None

        self.expid   = None  # set_exp_vars
        self.expdir  = None
        self.homdir  = None

        self.scrdir = None #  create_exp_subdirs

        self.nx = None # set_exp_run_params
        self.ny = None
        self.agcm_im = None
        self.agcm_jm = None
        self.agcm_lm = None
        self.ogcm_im = None
        self.ogcm_jm = None
        self.ogcm_lm = None
        self.use_ioserver = None
        self.num_oserver_nodes = None
        self.num_backend_pes   = None
        self.model_npes = None
        self.ncpus_per_node = None
        self.num_model_nodes = None
        self.total_nodes = None
        self.total_pes = None
 
        self.end_date  = None #prepare_fixed_files
        self.num_sgmt  = None
        self.fsegment  = None
        self.use_shmem = None

    def load_g5modules(self,site):
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

            self.basedir = "/discover/swdev/gmao_SIteam/Baselibs/ESMA-Baselibs-7.5.0/x86_64-pc-linux-gnu/ifort_2021.6.0-intelmpi_2021.6.0"

            if self.arch is None:
                self.arch = platform.system() # e.g., "Linux", "Darwin"

            baselib_path = "{}/{}/lib".format(self.basedir,self.arch)
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

 
    def set_env_vars(self, site, geosdir, geosbin, geosetc, geosutil):
        """
        Architecture Specific Environment Variables
        """
        self.arch = platform.system() # e.g., "Linux", "Darwin"

        self.site     = site
        self.geosdir  = os.path.abspath(geosdir)
        self.geosbin  = os.path.abspath(geosbin)
        self.geosetc  = os.path.abspath(geosetc)
        self.geosutil = os.path.abspath(geosutil)

        # g5modules is loaded as a separate function
        baselib_path = "{}/{}/lib".format(self.basedir,self.arch)
        geoslib_path = "{}/lib".format(self.geosdir)
        if "LD_LIBRARY_PATH" not in os.environ.keys():
            os.environ["LD_LIBRARY_PATH"] = baselib_path
            os.environ["LD_LIBRARY_PATH"] += ":{}".format(geoslib_path)
        else:
            if baselib_path not in os.environ["LD_LIBRARY_PATH"]:
                os.environ["LD_LIBRARY_PATH"] += ":{}".format(baselib_path)
            if geoslib_path not in os.environ["LD_LIBRARY_PATH"]:
                os.environ["LD_LIBRARY_PATH"] += ":{}".format(geoslib_path)

        self.run_cmd = self.geosbin + "/esma_mpirun -np"

        with open(os.path.join(self.geosetc, ".AGCM_VERSION")) as f:
            self.gcmver = f.readline()
        print("VERSION:", self.gcmver)


    def set_exp_vars(self, expid, expdir, homdir):
        """
        Experiment Specific Environment Variables
        """
        self.expid = expid
        self.expdir = os.path.abspath(expdir)
        self.homdir = os.path.abspath(homdir)

        # skip RSTDATE
        # GCMEMIP

    def create_exp_subdirs(self):
        """
        Create Experiment Sub-Directories
        """
        subdirs=['restarts','holding','archive','post','plot']
        for subdir in subdirs:
            subdir_path = os.path.join(self.expdir,subdir)
            if not os.path.exists(subdir_path):
                os.makedirs(subdir_path)

        self.scrdir = os.path.join(self.expdir, "scratch")
        if not os.path.exists(self.scrdir):
            os.makedirs(self.scrdir)



    def set_exp_run_params(self, ncpus=45*27, ncpus_per_node=45):
        """
        Set Experiment Run Parameters
        """
        if not os.path.exists( os.path.join(self.homdir, "AGCM.rc")):
            raise RuntimeError("AGCM.rc not found under: {}".format(self.homdir))
            sys.exit(1)

        self.nx      = int( run_grep("grep '^\s*NX:'             AGCM.rc | cut -d: -f2", wkdir=self.homdir) )
        self.ny      = int( run_grep("grep '^\s*NY:'             AGCM.rc | cut -d: -f2", wkdir=self.homdir) )
        self.agcm_im = int( run_grep("grep '^\s*AGCM_IM:'        AGCM.rc | cut -d: -f2", wkdir=self.homdir) )
        self.agcm_jm = int( run_grep("grep '^\s*AGCM_JM:'        AGCM.rc | cut -d: -f2", wkdir=self.homdir) )
        self.agcm_lm = int( run_grep("grep '^\s*AGCM_LM:'        AGCM.rc | cut -d: -f2", wkdir=self.homdir) )
        self.ogcm_im = int( run_grep("grep '^\s*OGCM\.IM_WORLD:' AGCM.rc | cut -d: -f2", wkdir=self.homdir) )
        self.ogcm_jm = int( run_grep("grep '^\s*OGCM\.JM_WORLD:' AGCM.rc | cut -d: -f2", wkdir=self.homdir) )
        self.ogcm_lm = int( run_grep("grep '^\s*OGCM\.LM:'       AGCM.rc | cut -d: -f2", wkdir=self.homdir) )
        self.nx      = int( run_grep("grep '^\s*OGCM\.NX:'       AGCM.rc | cut -d: -f2", wkdir=self.homdir) )
        self.ny      = int( run_grep("grep '^\s*OGCM\.NY:'       AGCM.rc | cut -d: -f2", wkdir=self.homdir) )

        self.use_ioserver = 1
        self.num_oserver_nodes = int( run_grep("grep '^\s*IOSERVER_NODES:'  AGCM.rc | cut -d: -f2", wkdir=self.homdir) )
        self.num_backend_pes    = int( run_grep("grep '^\s*NUM_BACKEND_PES:' AGCM.rc | cut -d: -f2", wkdir=self.homdir) )

        self.model_npes = self.nx * self.ny
        self.ncpus_per_node = ncpus_per_node
        self.num_model_nodes = calc_num_model_nodes(self.model_npes, self.ncpus_per_node)

        if self.use_ioserver == 1:
            self.total_nodes = self.num_model_nodes + self.num_oserver_nodes
            self.total_pes   = self.total_nodes * self.ncpus_per_node

            if self.total_pes > ncpus:
                msg = f"""
                         CPU Resources are Over-Specified
                         --------------------------------
                         Allotted  NCPUs: {ncpus}
                         Requested NCPUs: {self.total_pes}
         
                         Specified NX: {self.nx}
                         Specified NY: {self.ny}

                         Specified model nodes: {self.num_model_nodes}
                         Specified oserver nodes: {self.num_oserver_nodes}
                         Specified cores per node: {self.ncpus_per_node}
                """
                raise RuntimeError(msg)
                sys.exit(3)
        else:
            self.total_pes = self.model_npes

            if self.total_pes > ncpus:
                msg = f"""
                         CPU Resources are Over-Specified
                         --------------------------------
                         Allotted  NCPUs: {ncpus}
                         Requested NCPUs: {self.total_pes}
         
                         Specified NX: {self.nx}
                         Specified NY: {self.ny}

                         Specified model nodes: {self.num_model_nodes}
                         Specified cores per node: {self.ncpus_per_node}
                """
                raise RuntimeError(msg)
                sys.exit(4)

    def prepare_fixed_files(self):
        """
        Move to Scratch Directory and Copy RC Files from Home Directory
        """
        if os.path.exists(self.scrdir):
            if len(os.listdir(self.scrdir)) != 0:
                print("scratch dir ({}) not empty. Delete it and recreate a one".format(self.scrdir))
                shutil.rmtree(self.scrdir)   
                os.makedirs(self.scrdir)

        else:
            raise RuntimeError("scratch directory ({}) not found".format(self.scrdir))
            sys.exit(4)

        rcdir = os.path.join(self.expdir, "RC")
        for f in os.listdir(rcdir):
            src = os.path.join(rcdir, f)
            dst = os.path.join(self.scrdir, f)

            if os.path.isfile(src) or os.path.islink(src):
                if os.path.exists(dst):
                    print("{} already in {}".format(f, self.scrdir))
                    os.remove(dst)
                shutil.copyfile(src, dst)    

        src = os.path.join(self.expdir, "cap_restart")
        dst = os.path.join(self.scrdir, "cap_restart")
        shutil.copyfile(src, dst)

        for ftype in ("*.rc","*.nml","*.yaml"):
            srcs = glob.glob(os.path.join(self.homdir, ftype))
            for src in srcs:
                dst = os.path.join(self.scrdir, os.path.basename(src))
                print(src, "--->", dst)
                shutil.copyfile(src, dst)

        src = os.path.join(self.geosbin, "bundleParser.py")
        dst = os.path.join(self.scrdir, "bundleParser.py")
        shutil.copyfile(src, dst)

        #cat fvcore_layout.rc >> input.nml
        with open(os.path.join(self.scrdir,"fvcore_layout.rc"), "r") as fin:
            buf = fin.read()
            with open(os.path.join(self.scrdir,"input.nml"), "a") as fout:
                fout.write(buf)

        for f in ("MOM_input","MOM_override"):
            src = os.path.join(self.homdir, f)
            dst = os.path.join(self.scrdir, f)
            shutil.copyfile(src, dst)
        

        self.end_date  = run_grep("grep '^\s*END_DATE:'     CAP.rc | cut -d: -f2", wkdir=self.scrdir).strip().lstrip() 
        self.num_sgmt  = run_grep("grep '^\s*NUM_SGMT:'     CAP.rc | cut -d: -f2", wkdir=self.scrdir).strip().lstrip()
        self.fsegment  = run_grep("grep '^\s*FCST_SEGMENT:' CAP.rc | cut -d: -f2", wkdir=self.scrdir).strip().lstrip()
        self.use_shmem = run_grep("grep '^\s*USE_SHMEM:'    CAP.rc | cut -d: -f2", wkdir=self.scrdir).strip().lstrip()



def create_history_collection():
    """
    Create HISTORY Collection Directories
    """
    pass

def link_bcs():
    """
    Link Boundary Datasets
    """
    pass

def get_exec_rst():
    """
    Get Executable and RESTARTS
    """
    pass


if __name__ == '__main__':
    cfg = ConfigGcmRun()
    cfg.load_g5modules(site = "NCCS")
    cfg.set_env_vars(site     = "NCCS", \
                     geosdir  = "/gpfsm/dnb06/projects/p179/cda/GEOSgcm_08Nov2022/install", \
                     geosbin  = "/gpfsm/dnb06/projects/p179/cda/GEOSgcm_08Nov2022/install/bin", \
                     geosetc  = "/gpfsm/dnb06/projects/p179/cda/GEOSgcm_08Nov2022/install/etc", \
                     geosutil = "/gpfsm/dnb06/projects/p179/cda/GEOSgcm_08Nov2022/install")
    #print(os.environ["LD_LIBRARY_PATH"])
    #print(os.environ["LD_LIBRARY64_PATH"])
    cfg.set_exp_vars(expid  = "test_code", \
                     expdir = "/discover/nobackup/cda/projects/test_code", \
                     homdir = "/discover/nobackup/cda/projects/test_code")
    cfg.create_exp_subdirs()
    cfg.set_exp_run_params(ncpus=45*27, ncpus_per_node=45)
    cfg.prepare_fixed_files()

    print("="*80+'\n')
    print(cfg)
