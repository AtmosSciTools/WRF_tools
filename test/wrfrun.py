# %%
from wrf_tools import WRFProcessor, ERA5DataDownloader
import os


# %%
run_period = { 'start_date' : "2026-04-01 00", 'end_date' : "2026-04-01 18" }

setting = "test"

#domain_center = { 'id': 'Mogadishu', 'lat': 2.05, 'lon': 45.32 }

domain_center = {
    'id': 'Bangkok',
    'lat': 13.75,
    'lon': 100.50
}

domain = { 'max_dom': 3, 'parent_grid_ratio' : (1,3,3), 
          'dx' : 18000, 'dy' : 18000, 
          'e_we_ini' : (100, 100, 100),
          'e_sn_ini' : (100, 100, 100) }

paths = {
    'wpsdir': os.environ.get('WPS'),
    'wrfdir': os.environ.get('WRF'),
    'geogdir': os.environ.get('WPS_GEOG'),
    'renaldir': os.path.join(os.environ.get('REANAL'), "era5/"+domain_center['id']+'/'), 
    'namelist_wps' : os.path.join(os.environ.get('WRF_TOOLS'), "namelists",f"{setting}_namelist.wps"),
    'namelist_input': os.path.join(os.environ.get('WRF_TOOLS'), "namelists",f"{setting}_namelist.input")
}
download_dir = paths['renaldir']

#  You can set directly as below if you do not want to use environment variables.
# paths = {
#     'wpsdir': "/Volumes/work/WRF_program/WRF_install/WPS/",
#     'wrfdir': "/Volumes/work/WRF_program/WRF_install/WRF_mpi/",
#     'geogdir': "/Volumes/work/WRF_program/WPS_GEOG",
#     'renaldir': "/Volumes/work/WRF_program/era5/"+domain_center['id']+'/',
#     'namelist_wps' : "/Volumes/work/WRF_program/WRF_install/WPS//namelist.wps",
#     'namelist_input': "/Volumes/work/WRF_program/WRF_install/WRF_mpi/run/namelist.input"
# }

# download_dir = f"/Volumes/work/WRF_program/era5/{domain_center['id']}/"

# %%
# downloader = ERA5DataDownloader(run_period, domain_center, domain, download_dir)
# downloader.download_data()

# %%
base_dir = os.environ.get('SIMULATION')
run_dir = os.path.join(base_dir, 'Run_WRF', domain_center['id'], setting)

wrf_processor = WRFProcessor(run_period, domain_center, domain, paths, run_dir, run_wrf=True, other_GEOTBL=None, force=True)
wrf_processor.run_wrf()

# import subprocess
# subprocess.run(["mpirun", "-np", "4", "./real.exe"], cwd=run_dir, check=True)
