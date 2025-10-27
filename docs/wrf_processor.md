# WRF_tools User Guide

## Overview

- ERA5 download: see [ERA5DataDownloader](#era5datadownloader)
- WPS/WRF orchestration: see [WRFProcessor](#wrfprocessor)

This guide focuses on the minimum settings you need and step-by-step usage. Existing code examples and tables are kept as-is.

## Quick Start

1) Set environment variables (WPS/WRF/GEOG path, repository root, reanalysis root, and run base). See [Environment Variables](#environment-variables) below.
2) Define run period, domain center, and domain nest config using the code block under [Path definitions](#path-definitions).
3) Download ERA5 GRIBs using [ERA5DataDownloader](#era5datadownloader) into `paths['renaldir']`.
4) Run[ WRFProcessor](#wrfprocessor) once templates are prepared in `namelists/<setting>_namelist.wps` and `namelists/<setting>_namelist.input`.

Outputs: `met_em*` from WPS, `wrfinput_d0?`, `wrfbdy_d01`, and WRF outputs `wrfout_d0?_*` under your `run_dir`.


## Environment Variables


Add the following example to your shell startup file (e.g., `~/.bashrc` or `~/.profile`). Edit the paths to match your system before sourcing the file.

```bash
# filepath: ~/.bashrc (example lines to add)
# Set WPS, WRF, and geographic data locations
export WPS="/opt/wps"
export WRF="/opt/wrf"
export WPS_GEOG="/data/WPS_GEOG"

# Base directory for ERA5/reanalysis data; domain id appended by scripts
export REANAL="/data/reanalysis"

# WRF_tools repository root (contains namelists and utilities)
export WRF_TOOLS="/home/user/WRF_tools"

# Root simulation directory used to build run_dir
export SIMULATION="/home/user/simulations"
```

- After editing, reload: `source ~/.bashrc`

Notes:
- You may set paths directly in Python code instead of environment variables, or manage them via a hidden file such as `.env`.

## Domain and Path Setup

### Path definitions

- **Python script**

```python
run_period = { 'start_date' : "2025-01-01 00", 'end_date' : "2025-01-08 00" }

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

setting = "test"
base_dir = os.environ.get('SIMULATION')
run_dir = os.path.join(base_dir, 'Run_WRF', domain_center['id'], setting)
```

Use the snippet above as a template. Then adjust `run_period`, `domain_center`, `domain`, and `setting` per your case.

### Simulation / Domain variables

| Variable name | Description | namelist.wps |
|:---|:---|:---|
| **run_period** | Dictionary defining the simulation period. Contains:  | &share |
| ├─ **start_date** | Simulation start timestamp; used to set the initial time for the model run. | `start_date` |
| └─ **end_date** | Simulation end timestamp; defines the termination time for the model run. | `end_date` |
| **domain_center** | Dictionary specifying the domain’s identifier and geographic center. Used for directory naming and selecting reanalysis subsets. | &geogrid  |
| ├─ **id** | Unique string identifier for the simulation domain (e.g., `"Tokyo"`). | - |
| ├─ **lat** | Central latitude of the domain. | `ref_lat` |
| └─ **lon** | Central longitude of the domain. | `ref_lon` |
| **domain** | Dictionary containing WRF domain configuration parameters, including nesting and grid resolution. | &geogrid |
| ├─ **max_dom** | Number of nested domains. |  `max_dom` |
| ├─ **parent_grid_ratio** | Ratio of grid spacing between parent and child domains. | `parent_grid_ratio` |
| ├─ **dx**, **dy** | Horizontal grid spacing (m) in the west–east and south–north directions. |  `dx`, `dy` |
| ├─ **e_we_ini**, **e_sn_ini** | Initial domain size (grid points) before refinement or adjustment. | `e_we`, `e_sn` |

### Run settings and paths

| Variable name | Description |
|:---|:---|
| **paths** | Dictionary containing all key directory and configuration file paths used by WRF and WPS. |
| ├─ **wpsdir** | Path to the WPS installation directory (from `$WPS`). |
| ├─ **wrfdir** | Path to the WRF installation directory (from `$WRF`). |
| ├─ **geogdir** | Path to the WPS geographic data directory (from `$WPS_GEOG`). |
| ├─ **renaldir** | Path to the ERA5 reanalysis data for the domain (constructed from `$REANAL` and `domain_center['id']`). |
| ├─ **namelist_wps** | Path to the WPS namelist file for the current setting (constructed from `$WRF_TOOLS` and `setting`). |
| └─ **namelist_input** | Path to the WRF `namelist.input` file for the current setting (constructed from `$WRF_TOOLS` and `setting`). |
| **setting** | Logical name for the current configuration; determines which namelist files are used (e.g., `"test"`). |
| **base_dir** | Root directory for simulations (from `$SIMULATION`); serves as the top-level directory for all runs. |
| **run_dir** | Full path to the run directory for the specific domain and setting: `base_dir/Run_WRF/<domain_center['id']>/<setting>`. |


## ERA5DataDownloader

- Location: `wrf_tools/era_downloader.py`
- Purpose: Download ERA5 pressure-level and single-level GRIB files for a rectangular area derived from your WRF domain and a given period.

### Usage
- Prerequisites: install `cdsapi` and set a valid CDS API key in `~/.cdsapirc`.
- Area calculation: the rectangle is centered at `domain_center` and sized from `domain['dx'] * domain['e_we_ini'][0]` (times 2 as buffer), converted to degrees considering latitude.
- Files written: `era5_ungrib_pressure_levels_YYYYMMDD.grib`, `era5_ungrib_surface_levels_YYYYMMDD.grib` into `download_dir` (typically `paths['renaldir']`).

### Quick start example

- **Python script**

```python
from wrf_tools.era_downloader import ERA5DataDownloader

run_period = { 'start_date' : "2025-01-01 00", 'end_date' : "2025-01-08 00" }

domain_center = {
    'id': 'Bangkok',
    'lat': 13.75,
    'lon': 100.50
}

domain = { 'max_dom': 3, 'parent_grid_ratio' : (1,3,3), 
        'dx' : 18000, 'dy' : 18000, 
        'e_we_ini' : (100, 100, 100),
        'e_sn_ini' : (100, 100, 100) }

download_dir = paths['renaldir']
# download_dir = os.path.join(os.environ.get('REANAL'), "era5/"+domain_center['id']+'/')

down = ERA5DataDownloader(run_period, domain_center, domain, download_dir)
down.download_data()
```

- **downloaded data**

```bash
reanalysis
├── era5
    ├── Bangkok
        ├── era5_ungrib_pressure_levels_20250101.grib
        ├── era5_ungrib_pressure_levels_20250102.grib
        ├── era5_ungrib_pressure_levels_20250103.grib
        ├── era5_ungrib_pressure_levels_20250104.grib
        ├── era5_ungrib_pressure_levels_20250105.grib
        ├── era5_ungrib_pressure_levels_20250106.grib
        ├── era5_ungrib_pressure_levels_20250107.grib
        ├── era5_ungrib_pressure_levels_20250108.grib
        ├── era5_ungrib_surface_levels_20250101.grib
        ├── era5_ungrib_surface_levels_20250102.grib
        ├── era5_ungrib_surface_levels_20250103.grib
        ├── era5_ungrib_surface_levels_20250104.grib
        ├── era5_ungrib_surface_levels_20250105.grib
        ├── era5_ungrib_surface_levels_20250106.grib
        ├── era5_ungrib_surface_levels_20250107.grib
        └── era5_ungrib_surface_levels_20250108.grib
```

### More details in ["Details of ERA5DataDownloader"](#details-of-era5datadownloader)

## WRFProcessor

- Location: `wrf_tools/wrf_processor.py`
- Purpose: End-to-end orchestration to configure WPS/WRF, pre-process ERA5, and run `real.exe` and `wrf.exe` (MPI supported).

### Minimal driver example

- **Python script**

```python
from wrf_tools.wrf_processor import WRFProcessor
import os

run_period = {'start_date': '2025-01-01 00', 'end_date': '2025-01-08 00'}
domain_center = {'id': 'Bangkok', 'lat': 13.75, 'lon': 100.50}
domain = {
    'max_dom': 3,
    'parent_grid_ratio': (1, 3, 3),
    'dx': 18000, 'dy': 18000,
    'e_we_ini': (100, 100, 100),
    'e_sn_ini': (100, 100, 100)
}

setting = 'test'
paths = {
    'wpsdir': os.environ['WPS'],
    'wrfdir': os.environ['WRF'],
    'geogdir': os.environ['WPS_GEOG'],
    'renaldir': os.path.join(os.environ['REANAL'], f"era5/{domain_center['id']}/"),
    'namelist_wps': os.path.join(os.environ['WRF_TOOLS'], 'namelists', f'{setting}_namelist.wps'),
    'namelist_input': os.path.join(os.environ['WRF_TOOLS'], 'namelists', f'{setting}_namelist.input'),
}

run_dir = os.path.join(os.environ['SIMULATION'], 'Run_WRF', domain_center['id'], setting)

wrf = WRFProcessor(run_period, domain_center, domain, paths, run_dir, num_process=16, other_GEOTBL=None)
wrf.run_wrf()
```

- **Output data**

```bash
simulation/Run_WRF/
├── Bangkok
    └── test
        ├── geogrid
        ├── metgrid
        ├── ungrib
        ├── namelist.wps
        ├── namelist.input
        ├── wrfbdy_d01
        ├── wrfinput_d01
        ├── :
        ├── wrfout_d01_2025-01-01_00:00:00
        ├── :
        ├── wrfout_d02_2025-01-01_00:00:00
        ├── :
        ├── wrfout_d03_2025-01-01_00:00:00
        ├── :
        └── wrfout_d03_2025-01-08_00:00:00
```

### Responsibilities
- Create a run directory populated with `geogrid`, `ungrib`, `metgrid`, and WRF `run/` files.
- Prepare `namelist.wps` and `namelist.input` from template files, adjusting time, domains, and paths.
- Run WPS steps: `geogrid.exe`, `ungrib.exe` (twice for pressure/surface), `metgrid.exe`.
- Infer metgrid dimensions and update counts (e.g., `num_metgrid_levels`) in `namelist.input`.
- Launch `real.exe` and `wrf.exe` (MPI via `mpirun -np <num_process>`).

### More details in ["Details of WRFProcessor"](#details-of-wrfprocessor)

# Appendix
## Details of ERA5DataDownloader

### Key methods
- `get_rectangle_bounds()`: returns dict with north/south/east/west bounds.
- `generate_date_range()`: returns list of `YYYY-MM-DD` dates; if `end_date` has non-zero hour, includes the end day.
- `download_pressure_level_data(date, area)`: writes one GRIB per day for mandatory pressure variables and levels.
- `download_surface_level_data(date, area)`: writes one GRIB per day for surface/single-level variables.
- `download_data()`: high-level loop over dates that calls both downloads.

### Notes and tips
- CDS credentials: create `~/.cdsapirc` with your API key. Test with a small request first.
- Area order for CDS `area` is `[north, west, south, east]` (handled internally). Bounds are rounded to 0.01°.
- Time steps: requests 00, 06, 12, 18 UTC consistent with typical WPS ungrib use.
- Extent heuristic: width uses `dx * e_we_ini[0] * 2` to add margin; adjust if coastal domains need more ocean coverage.
- Resume downloads: files are saved per day; reruns will skip already completed transfers.

## Details of WRFProcessor

### What it automates
- Directory setup: copies `{geogrid,ungrib,metgrid}` folders and their executables from `paths['wpsdir']` and links `link_grib.csh`.
- WRF runtime: copies all files from `paths['wrfdir']/run` except an existing `namelist.input`.
- Namelist templating: reads your templates and replaces keys that match `key = ...` at the start of lines.
- Domain inference: `set_domains()` computes child sizes and parent starts to match requested `e_we_ini/e_sn_ini` and `parent_grid_ratio`.
- Map projection: mercator for |lat| ≤ 30, lambert otherwise. Sets `truelat1`, `truelat2`, and `stand_lon` from the center.
- GEOGRID.TBL override: if `other_GEOTBL` is provided (e.g., `GEOGRID.TBL.ARW_LCZ` under `geogrid/`), it copies to `geogrid/GEOGRID.TBL`.
- Ungrib passes: runs twice with prefixes `ERA5A` and `ERA5S`, linking GRIBs from `paths['renaldir']` per day. Then sets `fg_name = "ERA5A", "ERA5S"`.
- Post-metgrid updates: reads a `met_em*` NetCDF to fill `num_metgrid_levels`, `num_metgrid_soil_levels`, and `num_land_cat` in `namelist.input`.
- Time step and parents: derives `run_days/hours`, `parent_id/grid_id`, per-domain `dx/dy`, `parent_time_step_ratio`, and a base `time_step = int(dx_root*6/1000)`.


### Execution notes
- Ensure `geogrid.exe`, `ungrib.exe`, `metgrid.exe` exist under `paths['wpsdir']`, and `real.exe`, `wrf.exe` plus runtime files exist under `paths['wrfdir']/run`.
- Place downloaded ERA5 GRIBs under `paths['renaldir']` with the required naming pattern.
- The processor redirects most tool output to `/dev/null`; check files like `rsl.error.0000` for WRF runtime issues.

### Common pitfalls and troubleshooting
- Missing Vtable: the processor symlinks `ungrib/Variable_Tables/Vtable.ECMWF` to `Vtable`. Ensure this file exists in your WPS tree.
- GRIB naming: must match `era5_ungrib_pressure_levels_YYYYMMDD.grib` and `era5_ungrib_surface_levels_YYYYMMDD.grib` for auto-linking.
- Dimension mismatches: if `e_we_ini/e_sn_ini` are inconsistent with `parent_grid_ratio`, `set_domains()` chooses the closest feasible sizes; verify final sizes in the written `namelist.wps`.
- MPI runs: `wrf.exe` uses `mpirun -np <num_process>`. Ensure your MPI environment is configured and accessible on PATH.
- Time window: if `end_date` hour > 0, include that end day’s GRIBs.

### CLI-style recipe
1) Download ERA5 to `paths['renaldir']` using the downloader above.
2) Prepare templates in `namelists/<setting>_namelist.(wps|input)`.
3) Export environment variables, build `paths` and `run_dir`.
4) Instantiate `WRFProcessor(..., num_process=N)` and call `run_wrf()`.


## GHCNDataDownloader

- Location: `wrf_tools/ghcn_download_processor.py`
- Class: `GHCNhProcessor`
- Purpose: Download and process GHCN (hourly) station data over a user-defined bounding box and year range. Produces per-station CSVs and availability summaries and plots.

### Key configuration:
- `start_year`, `end_year`: inclusive range.
- `area`: `[lat_min, lat_max, lon_min, lon_max]` — often derived from a WRF domain file (e.g., `geo_em.d0?.nc`).
- `output_dir`: root directory to store downloads, processed data, and summaries.

- **Python script**

### Quick start example:
```python
from wrf_tools.ghcn_download_processor import GHCNhProcessor
import xarray as xr

geo_em = 'path/to/geo_em.d02.nc'
ds = xr.open_dataset(geo_em)
area = [
    float(ds['XLAT_C'].values[0][0, 0]),
    float(ds['XLAT_C'].values[0][-1, 0]),
    float(ds['XLONG_C'].values[0][0, 0]),
    float(ds['XLONG_C'].values[0][0, -1]),
]

proc = GHCNhProcessor(start_year=2024, end_year=2024, area=area, output_dir='out/GHCNh')
proc.download_data()
proc.plot_station_locations()       # if cartopy is installed
proc.plot_availability_heatmaps()   # if seaborn is installed
```

### Dependencies:
- Required: `pandas`, `numpy`, `wget`, `matplotlib`.
- Optional: `seaborn` (heatmaps), `cartopy` (maps).

### Notes on availability calculation:
- Missing sentinel values are converted to NaN per variable before counting.
- Time index is reindexed to hourly for the whole year to ensure consistent availability ratios.

### Workflow and outputs:
- Loads station metadata from `wrf_tools/data/ghcnh-station-list.csv` and filters by `area`.
- Downloads per-station, per-year PSV files from NCEI, saves under `<output_dir>/download/`.
- Processes PSV to hourly CSV per year under `<output_dir>/<year>/<station>.csv` and computes variable availability.
- Writes summaries under `<output_dir>/summaries/`:
  - `stations_summary.csv`, `download_results.csv`, `availability_summary.csv`.
  - Optional plots: station map (`station_location_map.png`, requires `cartopy`) and per-station availability heatmaps (`seaborn`).