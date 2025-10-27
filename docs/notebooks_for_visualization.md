# Sample code for visualizing WRF output

## Overview

## Examples of data structure

```bash
sample_data # data_dir
├── reanalysis
│    └── era5
│        └── Bangkok
│            ├── era5_ungrib_pressure_levels_20250101.grib
│            ├── :
│            ├── era5_ungrib_pressure_levels_20250101.grib
│            ├── era5_ungrib_surface_levels_20250101.grib
│            ├── :        
│            └── era5_ungrib_surface_levels_20250108.grib
├── point_data
│   └── GHCNh
│       ├── 2025 # <- reformated data
│       │   ├── GHCNh_THM00048420_2025.csv
│       │   ├── GHCNh_THM00048429_2025.csv
│       │   ├── GHCNh_THM00048453_2025.csv
│       │   ├── GHCNh_THM00048454_2025.csv
│       │   ├── GHCNh_THM00048455_2025.csv
│       │   └── GHCNh_THM00048457_2025.csv
│       ├── download
│       └── summaries
│           ├── availability_summary.csv
│           ├── download_results.csv
│           ├── station_location_map.png
│           └── stations_summary.csv
└── Run_WRF
    ├── Bangkok
    |   # contain namelist, wrfinput, wrfoutput in each dhirectpry
    │   ├── test
    │   │   ├── namelist.wps
    │   │   ├── namelist.input
    │   │   ├── wrfbdy_d01
    │   │   ├── wrfinput_d01
    │   │   ├── :
    │   │   ├── wrfout_d01_2025-01-01_00:00:00
    │   │   ├── :
    │   │   ├── wrfout_d02_2025-01-01_00:00:00
    │   │   ├── :
    │   │   ├── wrfout_d03_2025-01-01_00:00:00
    │   │   ├── :
    │   │   └── wrfout_d03_2025-01-08_00:00:00
    │   └── tropical
    └── Example
        ├── geo_em.d01.nc
        ├── geo_em.d02.nc
        ├── namelist.input
        └── namelist.wps
```

### Notes:

- If you want to change the directory structure, **you need to manually modify the file paths yourself.**

## 10_domain_overview.ipynb

### Description:
This notebook visualizes the WRF domain nesting structure using geo_em files (geogrid outputs). It also includes optional cells to visualize land use (LU_INDEX) and elevation (HGT_M) with hillshade.

### Key contents:
- Read XLAT_C/XLONG_C and XLAT_M/XLONG_M to draw grid lines.
- Display parent (d01) and nested (d02, d03) domain boundaries with distinct styles.
- Plot LU_INDEX with a categorical colormap (including optional LCZ mapping).
- Plot topography (HGT_M) with contours and hillshade overlay.

### Required files:
- geo_em.d0*.nc (e.g., geo_em.d01.nc, geo_em.d02.nc, geo_em.d03.nc)
  Place them under data_dir/Run_WRF/{domain_id}/{setting}/.

### Dependencies (main):
- xarray, numpy, matplotlib, cartopy

### Usage:
1. Open the notebook in Jupyter or VS Code.
2. Edit path variables to match your environment:
   - data_dir, domain_id, setting (e.g., data_dir = "~/WRF_tools/sample_data").
3. Confirm the required geo_em files exist.
4. Run cells from top to bottom.

### Notes:
- Cartopy map rendering may require projection and font tweaks depending on environment.
- Large/high-resolution domains may take longer to render.

## 20_timeseries_point.ipynb

### Description
Plot time series at selected station points or arbitrary lat/lon from WRF outputs. Supports near-surface variables (e.g., T2, Q2, U10/V10), accumulated precipitation, and optional comparison with GHCN hourly observations.

### Required files
- WRF outputs: `wrfout_d0?_YYYY-MM-DD_HH:MM:SS` under `data_dir/Run_WRF/{domain_id}/{setting}/`.
- Optional observations: CSVs under `data_dir/point_data/GHCNh/{year}/GHCNh_*.csv`.

### Dependencies (main)
- xarray, numpy, pandas, matplotlib

### Usage
1. Set `data_dir`, `domain_id`, `setting`, and `domain_no` (e.g., 3 for d03).
2. Choose points:
   - Use available GHCN station CSVs, or
   - Provide manual list of lat/lon with labels.
3. Select variables: e.g., `['T2','Q2','U10','V10','RAINNC','RAINC']`.
4. Run all cells to create plots and optional CSV exports.

### Notes
- Precipitation total often uses `RAINNC + RAINC`; difference consecutive times for hourly accumulation.
- All times are UTC; shift to local time if desired.
- Station metadata must match CSV naming if auto-discovering.

## 30_plot_2d_maps.ipynb

### Description
Render 2D map fields from WRF outputs for a chosen time and domain using Cartopy. Typical variables: T2, RH2 (derived), U10/V10 vectors, and accumulated precipitation.

### Required files
- WRF outputs under `data_dir/Run_WRF/{domain_id}/{setting}/`.
- Optional: `geo_em.d0?.nc` for overlays (landuse/topography).

### Dependencies (main)
- xarray, numpy, matplotlib, cartopy

### Usage
1. Set `data_dir`, `domain_id`, `setting`, and `domain_no`.
2. Select a timestamp present in wrfout files.
3. Choose variables to plot and figure options (extent, colormap, vector density).
4. Run cells; optionally save figures to `figs/`.

### Notes
- Cartopy often works best via conda-forge builds (handles shapely/GEOS dependencies).
- Subsample wind vectors to reduce clutter on high-resolution domains.
## 40_plot_from_3d_variables.ipynb
## 50_vertical_xsection.ipynb
## 60_wind_streamline.ipynb
## 70_extreme_event_composite.ipynb
## 80_obs_sat_validation.ipynb
## 90_io_performance.ipynb
## 95_lcz_ucm_analysis.ipynb
## 99_export_figures.ipynb
## variables_description.csv
