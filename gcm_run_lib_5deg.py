#import numpy as np
#import datetime as dt
import os, sys, shutil, platform, glob
import datetime as dt
import subprocess as sp
from config_tools import Config
from env_modules_python import module  #lmod

def calc_num_model_nodes(model_npes, ncpus_per_node):
    x = model_npes / ncpus_per_node
    y = int(x)
    return y+1 if x>y else y

def get_cmd_out(cmd, wkdir, showError=False):
    p = sp.Popen(cmd, cwd=wkdir, shell=True,stdout=sp.PIPE, stderr=sp.PIPE)
    out, err = p.communicate()
    if showError: print("ERROR_MESSAGE={}".format(err.decode()))
    return out.decode()

class ConfigGcmRun(Config):
    def __init__(self):
        self.flowdir = None 

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

        self.collections = None #create_history_collection 

        self.bcsdir    = None # link_bcs
        self.chmdir    = None
        self.bcrslv    = None
        self.dateline  = None
        self.emissions = None
        self.abcsdir   = None
        self.obcsdir   = None
        self.sstdir    = None
 
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
            self.gcmver = f.readline().strip().lstrip()
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

        self.nx      = int( get_cmd_out("grep '^\s*NX:'             AGCM.rc | cut -d: -f2", wkdir=self.homdir) )
        self.ny      = int( get_cmd_out("grep '^\s*NY:'             AGCM.rc | cut -d: -f2", wkdir=self.homdir) )
        self.agcm_im = int( get_cmd_out("grep '^\s*AGCM_IM:'        AGCM.rc | cut -d: -f2", wkdir=self.homdir) )
        self.agcm_jm = int( get_cmd_out("grep '^\s*AGCM_JM:'        AGCM.rc | cut -d: -f2", wkdir=self.homdir) )
        self.agcm_lm = int( get_cmd_out("grep '^\s*AGCM_LM:'        AGCM.rc | cut -d: -f2", wkdir=self.homdir) )
        self.ogcm_im = int( get_cmd_out("grep '^\s*OGCM\.IM_WORLD:' AGCM.rc | cut -d: -f2", wkdir=self.homdir) )
        self.ogcm_jm = int( get_cmd_out("grep '^\s*OGCM\.JM_WORLD:' AGCM.rc | cut -d: -f2", wkdir=self.homdir) )
        self.ogcm_lm = int( get_cmd_out("grep '^\s*OGCM\.LM:'       AGCM.rc | cut -d: -f2", wkdir=self.homdir) )
        self.nx      = int( get_cmd_out("grep '^\s*OGCM\.NX:'       AGCM.rc | cut -d: -f2", wkdir=self.homdir) )
        self.ny      = int( get_cmd_out("grep '^\s*OGCM\.NY:'       AGCM.rc | cut -d: -f2", wkdir=self.homdir) )

        self.use_ioserver = 0
        self.num_oserver_nodes = int( get_cmd_out("grep '^\s*IOSERVER_NODES:'  AGCM.rc | cut -d: -f2", wkdir=self.homdir) )
        self.num_backend_pes    = int( get_cmd_out("grep '^\s*NUM_BACKEND_PES:' AGCM.rc | cut -d: -f2", wkdir=self.homdir) )

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
                shutil.copy2(src, dst)    

        src = os.path.join(self.expdir, "cap_restart")
        dst = os.path.join(self.scrdir, "cap_restart")
        shutil.copy2(src, dst)

        for ftype in ("*.rc","*.nml","*.yaml"):
            srcs = glob.glob(os.path.join(self.homdir, ftype))
            for src in srcs:
                dst = os.path.join(self.scrdir, os.path.basename(src))
                shutil.copy2(src, dst)

        src = os.path.join(self.geosbin, "bundleParser.py")
        dst = os.path.join(self.scrdir, "bundleParser.py")
        shutil.copy2(src, dst)

        #cat fvcore_layout.rc >> input.nml
        with open(os.path.join(self.scrdir,"fvcore_layout.rc"), "r") as fin:
            buf = fin.read()
            with open(os.path.join(self.scrdir,"input.nml"), "a") as fout:
                fout.write(buf)

        for f in ("MOM_input","MOM_override"):
            src = os.path.join(self.homdir, f)
            dst = os.path.join(self.scrdir, f)
            shutil.copy2(src, dst)
        

        self.end_date  = get_cmd_out("grep '^\s*END_DATE:'     CAP.rc | cut -d: -f2", wkdir=self.scrdir).strip().lstrip() 
        self.num_sgmt  = get_cmd_out("grep '^\s*NUM_SGMT:'     CAP.rc | cut -d: -f2", wkdir=self.scrdir).strip().lstrip()
        self.fsegment  = get_cmd_out("grep '^\s*FCST_SEGMENT:' CAP.rc | cut -d: -f2", wkdir=self.scrdir).strip().lstrip()
        self.use_shmem = get_cmd_out("grep '^\s*USE_SHMEM:'    CAP.rc | cut -d: -f2", wkdir=self.scrdir).strip().lstrip()

    def create_history_collection(self):
        """
        Create HISTORY Collection Directories
        """

        src = os.path.join(self.flowdir, "get_collections.csh")
        dst = os.path.join(self.scrdir, "get_collections.csh")
        shutil.copy2(src, dst)

        self.collections = get_cmd_out("./get_collections.csh", wkdir=self.scrdir).strip().lstrip().split()
        print("collections=",self.collections)
        for collection in self.collections:
            if not os.path.exists( os.path.join(self.expdir,collection) ):
                os.makedirs( os.path.join(self.expdir,collection) )
            if not os.path.exists( os.path.join(self.expdir, "holding", collection) ):
                os.makedirs( os.path.join(self.expdir, "holding", collection) )

    def link_bcs(self, bcsdir=None,chmdir=None, bcrslv=None, dateline=None, \
                 emissions=None, abcsdir=None, obcsdir=None, sstdir=None):
        """
        Link Boundary Datasets
        """
        self.bcsdir = os.path.abspath(bcsdir)
        self.chmdir = os.path.abspath(chmdir)
        self.bcrslv = bcrslv
        self.dateline = dateline
        self.emissions = emissions
        self.abcsdir = os.path.abspath(abcsdir)
        self.obcsdir = os.path.abspath(obcsdir)  # FIXME: in gcm_run.j: OGCM_IM/JM not hard-coded
        self.sstdir  = os.path.abspath(sstdir)   # FIXME: in gcm_run.j: OGCM_IM/JM not hard-coded
        self.bctag   = os.path.basename(self.abcsdir)

        linkbcs_path = os.path.join(self.scrdir, "linkbcs")
        if os.path.exists(linkbcs_path): os.remove(linkbcs_path)
        msg = f"""#!/bin/csh -f

/bin/mkdir -p RESTART
/bin/mkdir -p            ExtData
/bin/ln    -sf {self.chmdir}/* ExtData

/bin/ln -sf {self.obcsdir}/SEAWIFS_KPAR_mon_clim.{self.ogcm_im}x{self.ogcm_jm} SEAWIFS_KPAR_mon_clim.data
/bin/ln -sf {self.abcsdir}/CF0012x6C_TM0072xTM0036-Pfafstetter.til   tile.data
/bin/ln -sf {self.abcsdir}/CF0012x6C_TM0072xTM0036-Pfafstetter.TRN   runoff.bin
/bin/ln -sf {self.obcsdir}/MAPL_Tripolar.nc .
/bin/ln -sf {self.obcsdir}/vgrid{self.ogcm_lm}.ascii ./vgrid.ascii
#/bin/ln -s /discover/nobackup/projects/gmao/ssd/aogcm/MOM6/DC048xPC025_TM0072xTM0036/DC048xPC025_TM0072xTM0036-Pfafstetter.til tile_hist.data

# Precip correction
#/bin/ln -s /discover/nobackup/projects/gmao/share/gmao_ops/fvInput/merra_land/precip_CPCUexcludeAfrica-CMAP_corrected_MERRA/GEOSdas-2_1_4 ExtData/PCP


# DAS or REPLAY Mode (AGCM.rc:  pchem_clim_years = 1-Year Climatology)
# --------------------------------------------------------------------
/bin/ln -sf {self.bcsdir}/Shared/pchem.species.Clim_Prod_Loss.z_721x72.nc4 species.data

# CMIP-5 Ozone Data (AGCM.rc:  pchem_clim_years = 228-Years)
# ----------------------------------------------------------
#/bin/ln -sf {self.bcsdir}/Shared/pchem.species.CMIP-5.1870-2097.z_91x72.nc4 species.data

# S2S pre-industrial with prod/loss of stratospheric water vapor
# (AGCM.rc:  pchem_clim_years = 3-Years,  and  H2O_ProdLoss: 1 )
# --------------------------------------------------------------
#/bin/ln -sf {self.bcsdir}/Shared/pchem.species.CMIP-6.wH2OandPL.1850s.z_91x72.nc4 species.data

# MERRA-2 Ozone Data (AGCM.rc:  pchem_clim_years = 39-Years)
# ----------------------------------------------------------
#/bin/ln -sf {self.bcsdir}/Shared/pchem.species.CMIP-5.MERRA2OX.197902-201706.z_91x72.nc4 species.data

/bin/ln -sf {self.bcsdir}/Shared/*bin .
/bin/ln -sf {self.bcsdir}/Shared/*c2l*.nc4 .


/bin/ln -sf {self.abcsdir}/visdf_{self.agcm_im}x{self.agcm_jm}.dat visdf.dat
/bin/ln -sf {self.abcsdir}/nirdf_{self.agcm_im}x{self.agcm_jm}.dat nirdf.dat
/bin/ln -sf {self.abcsdir}/vegdyn_{self.agcm_im}x{self.agcm_jm}.dat vegdyn.data
/bin/ln -sf {self.abcsdir}/lai_clim_{self.agcm_im}x{self.agcm_jm}.data lai.data
/bin/ln -sf {self.abcsdir}/green_clim_{self.agcm_im}x{self.agcm_jm}.data green.data
/bin/ln -sf {self.abcsdir}/ndvi_clim_{self.agcm_im}x{self.agcm_jm}.data ndvi.data



/bin/ln -sf {self.abcsdir}/topo_DYN_ave_{self.agcm_im}x{self.agcm_jm}.data topo_dynave.data
/bin/ln -sf {self.abcsdir}/topo_GWD_var_{self.agcm_im}x{self.agcm_jm}.data topo_gwdvar.data
/bin/ln -sf {self.abcsdir}/topo_TRB_var_{self.agcm_im}x{self.agcm_jm}.data topo_trbvar.data

if(     -e  {self.bcsdir}/{self.bcrslv}/Gnomonic_{self.bcrslv}.dat ) then
/bin/ln -sf {self.bcsdir}/{self.bcrslv}/Gnomonic_{self.bcrslv}.dat .
endif

 cp {self.homdir}/*_table .
 cp {self.obcsdir}/INPUT/* INPUT
 /bin/ln -sf {self.obcsdir}/cice/kmt_cice.bin .
 /bin/ln -sf {self.obcsdir}/cice/grid_cice.bin .

        """
        with open(linkbcs_path,"w") as f:
            f.write(msg)

        os.chmod(linkbcs_path, 0o755)  # equivalent to chmod 755
        dst = os.path.join(self.expdir, os.path.basename(linkbcs_path))
        shutil.copy2(linkbcs_path, dst)
        

    def get_exec_rst(self):
        """
        Get Executable and RESTARTS
        """

        print("Hello from get_exec_rst") 

        src = os.path.join(self.expdir, "GEOSgcm.x")
        dst = os.path.join(self.scrdir, "GEOSgcm.x")
        shutil.copy2(src, dst)

        self.rst_files        = get_cmd_out("grep 'RESTART_FILE'    AGCM.rc | grep -v VEGDYN | grep -v '#' | cut -d ':' -f1 | cut -d '_' -f1-2",wkdir=self.scrdir).strip().lstrip().split()
        self.rst_file_names    = get_cmd_out("grep 'RESTART_FILE'    AGCM.rc | grep -v VEGDYN | grep -v '#' | cut -d ':' -f2",wkdir=self.scrdir).strip().lstrip().split()
        self.chk_files         = get_cmd_out("grep 'CHECKPOINT_FILE' AGCM.rc | grep -v '#' | cut -d ':' -f1 | cut -d '_' -f1-2",wkdir=self.scrdir).strip().lstrip().split()
        self.chk_file_names    = get_cmd_out("grep 'CHECKPOINT_FILE' AGCM.rc | grep -v '#' | cut -d ':' -f2",wkdir=self.scrdir).strip().lstrip().split()
        self.monthly_chk_names = get_cmd_out(f"cat {self.expdir}/HISTORY.rc | grep -v '^[\\t ]*#' | sed -n 's/\([^\\t ]\+\).monthly:[\\t ]*1.*/\\1/p' | sed 's/$/_rst/'",wkdir=self.scrdir).strip().lstrip().split()

        # Remove possible bootstrap parameters(+/-)
        print("Remove possible bootstrap parameters(+/-)")
        for i in range(len(self.rst_file_names)):
            if self.rst_file_names[i][0:1] == '+' or self.rst_file_names[i][0:1] == '-':
                self.rst_file_names[i] = self.rst_file_names[i][1:]

        # Copy Restarts to Scratch Directory
        print("Copy Restarts to Scratch Directory")
        all_rst_files = self.rst_file_names + self.monthly_chk_names
        for rst_file in all_rst_files:
            src = os.path.join(self.expdir,rst_file)
            dst = os.path.join(self.scrdir,rst_file)
            if os.path.exists(src):
                shutil.copy2(src, dst)

        os.makedirs( os.path.join(self.scrdir, "INPUT"))
        srcs = glob.glob(os.path.join(self.expdir,"RESTART/*"))
        if not srcs:
            raise RuntimeError("RESTART directory ({}) is empty. Abort...".format(os.path.join(self.expdir,"RESTART")))
            sys.exit(5)

        for src in srcs:
            file_name = os.path.basename(src)
            dst = os.path.join(self.scrdir, "INPUT", file_name)
            shutil.copy2(src, dst)

        # Copy and Tar Initial Restarts to Restarts Directory
        print("Copy and Tar Initial Restarts to Restarts Directory")
        # cap_restart YYYYMMDD HHmmss
        #             123456789012345
        #             012345678901234
        with open(os.path.join(self.scrdir,"cap_restart"),"r") as f:
            date_str = f.readline().strip().lstrip()
        edate = "e{}_{}z".format(date_str[0:8],date_str[9:11])
        print(edate)
        rst_tar_files = glob.glob(os.path.join(self.expdir, f"restarts/*{edate}*"))
        if not rst_tar_files: # does not exist saved IC

            # create a tmp dir to prepare IC tarball
            tmp_tardir = os.path.join(self.expdir,"restarts","tmp_tardir_{}".format(edate))
            os.makedirs(tmp_tardir)

            # non-ocean restart files
            for rst in self.rst_file_names:
                src = os.path.join(self.scrdir, rst)
                file_name = f"{self.expid}.{rst}.{edate}.{self.gcmver}.{self.bctag}_{self.bcrslv}"
                dst = os.path.join(tmp_tardir,file_name)
                if os.path.exists(src) and not os.path.exists(dst):
                    print(src,"-->",dst)
                    shutil.copy2(src, dst)

            # ocean restart files
            src = os.path.join(self.expdir,"RESTART")
            dst = os.path.join(tmp_tardir,f"RESTART.{edate}")
            if not os.path.exists(dst):
                shutil.copytree(src,dst)
            else:
                raise RuntimeError("copy ocean restart files: directory ({}) already exists. abort...".format(dst))
                sys.exit(6)
            
            # create tarball
            tar_file_name = f"restarts.{edate}.tar"
            pattern = f"{self.expid}.*.{edate}.{self.gcmver}.{self.bctag}_{self.bcrslv}"
            rst_file_paths = glob.glob(os.path.join(tmp_tardir, pattern))
            rst_files = []
            for rst_file_path in rst_file_paths:
                rst_files.append(os.path.basename(rst_file_path))
            tar_cmd = f"tar cvf {tar_file_name} " + " ".join(rst_files) + f" RESTART.{edate}"
            get_cmd_out(tar_cmd, wkdir=tmp_tardir)
            shutil.move(os.path.join(tmp_tardir,tar_file_name), os.path.join(self.expdir,"restarts"))
            # remove the tmp dir for preparing the tarball
            if os.path.exists(tmp_tardir): shutil.rmtree(tmp_tardir)

        
        # If any restart is binary, set NUM_READERS to 1 so that
        # +-style bootstrapping of missing files can occur in
        # MAPL. pbinary cannot do this, but pnc4 can.
        print("check binary")
        found_binary = 0
        for rst in self.rst_file_names:
            if os.path.exists(os.path.join(self.scrdir,rst)):
                rst_type = get_cmd_out(f"/usr/bin/file -Lb --mime-type {rst}", wkdir=self.scrdir).strip().lstrip()
                print("rst, type=", rst, rst_type)
                if "application/octet-stream" in rst_type: found_binary = 1

        if found_binary == 1:
            print("find_binary==1")
            AGCM_path = os.path.join(self.scrdir,"AGCM.rc")
            tmp_AGCM_path = os.path.join(self.scrdir,"AGCM.tmp")
            os.rename(AGCM_path,tmp_AGCM_path)
            get_cmd_out("cat AGCM.tmp | sed -e '/^NUM_READERS/ s/\([0-9]\+\)/1/g' > AGCM.rc",wkdir=self.scrdir)
            if os.path.exists(tmp_AGCM_path): os.remove(tmp_AGCM_path)


    def prepare_extdata(self):
        dst = os.path.join(self.scrdir,"EGRESS") 
        if os.path.exists(dst): os.remove(dst)

        # skip the segment run date parsing
        # cap_restart YYYYMMDD HHmmss
        #             123456789012345
        #             012345678901234
        with open(os.path.join(self.scrdir,"cap_restart"),"r") as f:
            date_str = f.readline().strip().lstrip()
        #nymdc = data_str[0:8]
        nymdc = dt.datetime.strptime(date_str,"%Y%m%d %H%M%S")
        sgmt_str = get_cmd_out("grep '^\s*JOB_SGMT:' CAP.rc | cut -d: -f2",wkdir=self.scrdir).strip().lstrip()
        dyear  = int(sgmt_str[0:4])
        dmonth = int(sgmt_str[4:6])
        dday   = int(sgmt_str[6:8])
        dhour  = int(sgmt_str[9:11])
        dminute = int(sgmt_str[11:13])
        dsecond = int(sgmt_str[13:15])
        print(dyear,dmonth,dday,dhour,dminute,dsecond)
        #00000100 000000
        #yyyymmdd HHMMSS
        #012345678901234
        if dyear > 0 or dmonth > 0:
            raise RuntimeError("does not support setting segment using YYYY or MM.abort...")
            sys.exit(8)
        dt_sgmt = dt.timedelta(days=dday, hours=dhour, minutes=dminute, seconds=dsecond)
        nymdf = nymdc + dt_sgmt
        print("nymdc   = ",nymdc)
        print("dt_sgmt = ",dt_sgmt)
        print("nymdf   = ",nymdf)

        num_sgmt = int(get_cmd_out("grep '^\s*NUM_SGMT:' CAP.rc | cut -d: -f2",wkdir=self.scrdir))
        if num_sgmt != 1:
            raise RuntimeError("Does not support running with >1 segment. abort...")
            sys.exit(7)

        # which ExtData are we using
        extdata2g_true = int(get_cmd_out("grep -i '^\s*USE_EXTDATA2G:\s*\.TRUE\.' CAP.rc | wc -l", \
                             wkdir=self.scrdir))
        print("extdata2g_true=",extdata2g_true)

        # Select proper AMIP GOCART Emission RC Files
        if self.emissions == "AMIP_EMISSIONS":
            if extdata2g_true == 0:
                AMIP_Transition_Date = dt.datetime(2000,3,1,0,0,0) 
                # Before 2000-03-01, we need to use AMIP.20C which has different
                # emissions (HFED instead of QFED) valid before 2000-03-01. Note
                # that if you make a change to anything in $EXPDIR/RC/AMIP or
                # $EXPDIR/RC/AMIP.20C, you might need to make a change in the other
                # directory to be consistent. Some files in AMIP.20C are symlinks to
                # that in AMIP but others are not.

                if nymdc < AMIP_Transition_Date:
                    AMIP_EMISSIONS_DIRECTORY = os.path.join(self.expdir, "RC", "AMIP.20C")
                    if nymdf > AMIP_Transition_Date:
                        raise RuntimeError("nymdc ({}) and nymdf ({}) cross the AMIP trans date ({})".format(nymdc, nymdf, AMIP_Transition_Date))
                        sys.exit(9)
                else:
                    AMIP_EMISSIONS_DIRECTORY = os.path.join(self.expdir, "RC", "AMIP")

                if self.agcm_lm == 72:
                    for ftype in ("*.rc","*.yaml"):
                        srcs = glob.glob(os.path.join(AMIP_EMISSIONS_DIRECTORY, ftype))
                        for src in srcs:
                            dst = os.path.join(self.scrdir, os.path.basename(src))
                            #print("src:",src,"---> dst:", dst)
                            shutil.copy2(src,dst)
                else:
                    raise RuntimeError("agcm_lm/=72 not implemented yet. abort...")
                    sys.exit(10)

                    #srcs  = glob.glob(os.path.join(AMIP_EMISSIONS_DIRECTORY,"*.rc")) + \
                    #        glob.glob(os.path.join(AMIP_EMISSIONS_DIRECTORY,"*.yaml"))

                    #for src in srcs:
                    #    if os.path.exists(src): shutil.remove(src)
                    #    dummy = os.path.join(self.scrdir,"dummy")
                    #    if os.path.exists(dummy): shutil.remove(dummy)
                    #    shutil.copy2(src, dummy)
                    #    cmd = f"cat dummy | sed -e 's|/L72/|/L{self.agcm_lm}/|g' | sed -e 's|z72|z{self.agcm_lm}|g' > {src}"
                    #    print(cmd)
                    #    get_cmd_std(cmd,wkdir=self.scrdir)
                        
        # Rename big ExtData files that are not needed                    
        ExtData_opt_files = {"ENABLE_STRATCHEM":   "StratChem_ExtData.rc", \
                             "ENABLE_GMICHEM":     "GMI_ExtData.rc", \
                             "ENABLE_GEOSCHEM":    "GEOSCHEMchem_ExtData.rc", \
                             "ENABLE_CARMA":       "CARMAchem_GridComp_ExtData.rc", \
                             "ENABLE_DNA":         "DNA_ExtData.rc", \
                             "ENABLE_ACHEM":       "GEOSachem_ExtData.rc", \
                             "ENABLE_GOCART_DATA": "GOCARTdata_ExtData.rc"}
        for opt in ExtData_opt_files.keys():
            cmd = f"grep -i '^\s*{opt}:\s*\.TRUE\.' GEOS_ChemGridComp.rc | wc -l"
            opt_true = int(get_cmd_out(cmd,wkdir=self.scrdir))
            if opt_true == 0 and os.path.exists( os.path.join(self.scrdir, ExtData_opt_files[opt]) ):
                src = os.path.join(self.scrdir, ExtData_opt_files[opt])
                dst = os.path.join(self.scrdir, ExtData_opt_files[opt]+".NOT_USED")
                #print("rename: src",src,": dst", dst)
                os.rename(src,dst)

        # 1MOM and GFDL microphysics do not use WSUB_NATURE
        if extdata2g_true == 0: 
            src = os.path.join(self.scrdir,"WSUB_ExtData.rc")
            dst = os.path.join(self.scrdir,"WSUB_ExtData.tmp")
            os.rename(src, dst)
            cmd = "cat WSUB_ExtData.tmp | sed -e '/^WSUB_NATURE/ s#ExtData.*#/dev/null#' > WSUB_ExtData.rc"
            get_cmd_out(cmd, wkdir=self.scrdir)
        else:
            src = os.path.join(self.scrdir,"WSUB_ExtData.yaml")
            dst = os.path.join(self.scrdir,"WSUB_ExtData.tmp")
            os.rename(src, dst)
            cmd = "cat WSUB_ExtData.tmp | sed -e '/collection:/ s#WSUB_Wvar_positive_05hrdeg.*#/dev/null#' > WSUB_ExtData.yaml"
            get_cmd_out(cmd, wkdir=self.scrdir)
        os.remove(dst)

        # Generate the complete ExtData.rc
        if os.path.exists(os.path.join(self.scrdir,"ExtData.rc")):
            os.remove(os.path.join(self.scrdir,"ExtData.rc"))

        #extdata_files = glob.glob(os.path.join(self.scrdir,"*_ExtData.rc")) 
        extdata_files = get_cmd_out("ls -1 *_ExtData.rc",wkdir=self.scrdir).strip().lstrip().split()
        print(extdata_files)

        if extdata2g_true == 0: 
            MODIS_Transition_Date = dt.datetime(2021,11,1)
            if self.emissions == "OPS_EMISSIONS" and nymdc >= MODIS_Transition_Date: 
                raise RuntimeError("Not implemented yet. abort...")
                sys.exit(11)
            else:
                with open(os.path.join(self.scrdir,"ExtData.rc"),"w") as fout:
                    for rc in extdata_files:
                        print("append rc file:", rc)
                        with open(os.path.join(self.scrdir,rc),"r") as fin:
                            fout.write(fin.read())

        if extdata2g_true == 1:
            get_cmd_out(f"{self.geosbin}/construct_extdata_yaml_list.py GEOS_ChemGridComp.rc", wkdir=self.scrdir)
            get_cmd_out("touch ExtData.rc", wkdir=self.scrdir)


        # Move GOCART to use RRTMGP bands
        # skip


        # Link Boundary Conditions for Appropriate Date
        os.environ['YEAR'] = str(nymdc.year)
        print("linkBCS now.")
        get_cmd_out("./linkbcs",wkdir=self.scrdir,showError=True)

        if not os.path.exists(os.path.join(self.scrdir, "tile.bin")):
            cmd = f"{self.geosbin}/binarytile.x tile.data tile.bin"
            get_cmd_out(cmd, wkdir=self.scrdir, showError=True)
            
            
        #########################
        # Split Saltwater
        #########################
        if os.path.exists( os.path.join(self.scrdir,"openwater_internal_rst") ) or \
           os.path.exists( os.path.join(self.scrdir,"seaicethermo_internal_rst")):
           print("Saltwater internal state is already split, good to go!")
        else:
           raise RuntimeError("Not implemented. Abort...")
           sys.exit(12)


        # Test Openwater Restart for Number of tiles correctness
        if False and os.path.exists(os.path.join(self.geosbin, "rs_numtiles.x")) and \
           os.access(os.path.join(self.geosbin, "rs_numtiles.x"), os.X_OK):
           print("Testing Openwater")
           N_OPENW_TILES_EXPECTED = int(get_cmd_out("grep '^\s*0' tile.data | wc -l", wkdir=self.scrdir))
           print("N_OPENW_TILES_EXPECTED=",N_OPENW_TILES_EXPECTED)
           cmd = "{} 1 {}/rs_numtiles.x openwater_internal_rst | grep Total | awk '{{print $NF}}'".format(self.run_cmd, self.geosbin)
           print("cmd=",cmd)
           N_OPENW_TILES_FOUND = int(get_cmd_out(cmd, wkdir=self.scrdir,showError=True).strip().lstrip())
           print("N_OPENW_TILES_FOUND=",N_OPENW_TILES_FOUND)
           if N_OPENW_TILES_EXPECTED != N_OPENW_TILES_FOUND:
              msg = f"Error! Found {N_OPENW_TILES_FOUND} tiles in openwater. Expect to find {N_OPENW_TILES_EXPECTED} tiles." \
                     + f"\nYour restarts are probably for a different ocean."
              raise RuntimeError(msg)
              sys.exit(13)
           else:
              print("Passed test openwater")
           

        # Check for MERRA2OX Consistency
        PCHEM_CLIM_YEARS = int(get_cmd_out("awk '/pchem_clim_years/ {print $2}' AGCM.rc", wkdir=self.scrdir))
        print("PCHEM_CLIM_YEARS=",PCHEM_CLIM_YEARS)

        if PCHEM_CLIM_YEARS == 39:
            with open(os.path.join(self.scrdir,"cap_restart"),"r") as f:
                date_str = f.readline().strip().lstrip()
            YEARMON = dt.datetime.strptime(date_str,"%Y%m%d %H%M%S")
            MERRA2OX_END_DATE = dt.datetime(2017,6,1)
            if YEARMON.year*100 + YEARMON.month > MERRA2OX_END_DATE.year*100 + MERRA2OX_END_DATE.month:
                msg = f"You seem to be using MERRA2OX pchem species file, but your simulation date " \
                      + "[{YEARMON}] is after 201706. This file is only valid until this time."
                raise RuntimeError(msg)
                sys.exit(14)

        # Environment variables for MPI, etc
        os.environ["I_MPI_ADJUST_ALLREDUCE"] = "12"
        os.environ["I_MPI_ADJUST_GATHERV"]   =  "3"

        # This flag prints out the Intel MPI state. Uncomment if needed
        os.environ["I_MPI_DEBUG"] = "9"
        os.environ["I_MPI_SHM_HEAP_VSIZE"] = "512"
        os.environ["PSM2_MEMORY"] = "large"
        os.environ["I_MPI_EXTRA_FILESYSTEM"] = "1"
        os.environ["I_MPI_EXTRA_FILESYSTEM_FORCE"] = "gpfs"

        # Run bundleParser.py
        get_cmd_out("python bundleParser.py",wkdir=self.scrdir)

        # If REPLAY, link necessary forcing files
        REPLAY_MODE = get_cmd_out("grep '^\s*REPLAY_MODE:' AGCM.rc | cut -d: -f2", wkdir=self.scrdir).strip().lstrip()
        if REPLAY_MODE == 'Exact' or REPLAY_MODE == 'Regular': 
            raise RuntimeError("Replay not supported yet. abort...")
            sys.exit(15)

        # Establish safe default number of OpenMP threads
        os.environ["OMP_NUM_THREADS"] = "1"


        # Run GEOSgcm.x
        if self.use_shmem == 1:
            raise RuntimeError("USE_SHMEM==1 not supported. aborted...")
            sys.exit(16)

        if self.use_ioserver == 1:
            IOSERVER_OPTIONS = f"--npes_model {self.model_npes} --nodes_output_server {self.num_oserver_nodes}"
            IOSERVER_EXTRA   = f"--oserver_type multigroup --npes_backend_pernode {self.num_backend_pes}"
        else:
            IOSERVER_OPTIONS = ""
            IOSERVER_EXTRA   = ""

        #cmd0 = "ln -sf /discover/nobackup/projects/gmao/ssd/aogcm/ocean_bcs/MOM6/72x36/cice/kmt_cice.bin ."
        #get_cmd_out(cmd0, wkdir=self.scrdir, showError=True)

        cmd = f"env LD_PRELOAD={self.geosdir}/lib/libmom6.so {self.run_cmd} {self.total_pes} ./GEOSgcm.x {IOSERVER_OPTIONS} {IOSERVER_EXTRA} --logging_config 'logging.yaml'"
        
        print(cmd)
        print(get_cmd_out(cmd, wkdir=self.scrdir, showError=True))



                


        

        


if __name__ == '__main__':
    cfg = ConfigGcmRun()
    cfg.flowdir = "/discover/nobackup/cda/develop_space/cycle-oletkf"
    cfg.flowdir = os.path.abspath(cfg.flowdir)

    cfg.load_g5modules(site = "NCCS")
    cfg.set_env_vars(site     = "NCCS", \
                     geosdir  = "/gpfsm/dnb06/projects/p179/cda/GEOSgcm_08Nov2022/install", \
                     geosbin  = "/gpfsm/dnb06/projects/p179/cda/GEOSgcm_08Nov2022/install/bin", \
                     geosetc  = "/gpfsm/dnb06/projects/p179/cda/GEOSgcm_08Nov2022/install/etc", \
                     geosutil = "/gpfsm/dnb06/projects/p179/cda/GEOSgcm_08Nov2022/install")
    #print(os.environ["LD_LIBRARY_PATH"])
    #print(os.environ["LD_LIBRARY64_PATH"])
    cfg.set_exp_vars(expid  = "fcst0001", \
                     expdir = "/discover/nobackup/cda/projects/letkf_exp/fcst0001", \
                     homdir = "/discover/nobackup/cda/projects/letkf_exp/fcst0001")
    cfg.create_exp_subdirs()
    cfg.set_exp_run_params(ncpus=40, ncpus_per_node=40) #skylake: 40, cascade: 45
    cfg.prepare_fixed_files()
    cfg.create_history_collection()
    cfg.link_bcs(bcsdir    = "/discover/nobackup/ltakacs/bcs/Icarus-NLv3/Icarus-NLv3_Reynolds", \
                 chmdir    = "/discover/nobackup/projects/gmao/share/gmao_ops/fvInput_nc3", \
                 bcrslv    = "CF0012x6C_DE0360xPE0180", \
                 dateline  = "DC", \
                 emissions = "OPS_EMISSIONS", \
                 #emissions = "AMIP_EMISSIONS", \
                 abcsdir   = "/discover/nobackup/projects/gmao/ssd/aogcm/atmosphere_bcs/Icarus-NLv3/MOM6/CF0012x6C_TM0072xTM0036", \
                 obcsdir   = "/discover/nobackup/projects/gmao/ssd/aogcm/ocean_bcs/MOM6/{}x{}".format(cfg.ogcm_im,cfg.ogcm_jm), \
                 sstdir    = "/discover/nobackup/projects/gmao/ssd/aogcm/SST/MERRA2/{}x{}".format(cfg.ogcm_im,cfg.ogcm_jm))
    cfg.get_exec_rst()
    cfg.prepare_extdata()
    #cfg.run_exec()
    print("="*80+'\n')
    print(cfg)
