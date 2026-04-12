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

## [10_domain_overview.ipynb](../notebooks/visualization/10_domain_overview.ipynb)

### Description
Visualize WRF domain nesting from geo_em files, with optional land use and elevation overlays.

### Key contents:
- Read XLAT_C/XLONG_C and XLAT_M/XLONG_M to draw grid lines.
- Display parent (d01) and nested (d02, d03) domain boundaries with distinct styles.
- Plot LU_INDEX with a categorical colormap (including optional LCZ mapping).
- Plot topography (HGT_M) with contours and hillshade overlay.

 

## [20_timeseries_point.ipynb](../notebooks/visualization/20_timeseries_point.ipynb)

### Description
Plot time series at selected points from WRF outputs, optionally compare with GHCN hourly observations.

### Key contents
- Load wrfout files from a chosen domain (e.g., d03) and time range.
- Extract near-surface variables such as T2, Q2, U10/V10; compute RH2 if needed.
- Build precipitation totals from RAINNC + RAINC and hourly accumulations by differencing.
- Select points by station list (GHCN CSVs) or manual lat/lon; interpolate from model grid.
- Plot multi-variable time series and optionally export to CSV for each point.

 

## [30_plot_2d_maps.ipynb](../notebooks/visualization/30_plot_2d_maps.ipynb)

### Description
Render 2D map fields from WRF outputs for a chosen time and domain using Cartopy.

### Key contents
- Open wrfout for a target timestamp and domain; subset the field of interest.
- Plot T2, RH2 (derived), wind vectors (U10/V10), and accumulated precipitation maps.
- Configure Cartopy projection and map extent from domain coordinates.
- Add coastlines, gridlines, and optional landuse/topography overlays from geo_em.
- Save figures to file and embed in the notebook.
 
## 40_plot_from_3d_variables.ipynb
## 50_vertical_xsection.ipynb
## 60_wind_streamline.ipynb
## 70_extreme_event_composite.ipynb
## 80_obs_sat_validation.ipynb
## 90_io_performance.ipynb
## 95_lcz_ucm_analysis.ipynb
## 99_export_figures.ipynb
## variables_description.csv
