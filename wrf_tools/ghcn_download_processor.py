# Global constants for file paths and base URL
#LIST_ISD_HISTORY = 'station_info/list-isd-history_2024.csv'  # Path to the station metadata CSV file

import os
import sys

LIST_ISD_HISTORY = os.path.join(os.path.dirname(__file__), "data", "ghcnh-station-list.csv")
BASE_URL = 'https://www.ncei.noaa.gov/oa/global-historical-climatology-network/hourly/access/by-year/'



# -----------------------------
# Library Imports and Checks
# -----------------------------
# Required libraries (essential for code execution)
required_libraries = {
    "pandas": "pandas",
    "numpy": "numpy",
    "wget": "wget",
    "matplotlib": "matplotlib"
}

# Optional libraries (enhance functionality but not critical)
optional_libraries = {
    "seaborn": "seaborn",       # For plotting heatmaps of data availability
    "cartopy": "cartopy"  # For plotting station locations on a map
}

# Check for missing required libraries
missing_required = []
for module, package in required_libraries.items():
    try:
        __import__(module)
    except ImportError:
        missing_required.append(package)

# Exit if any required libraries are missing
if missing_required:
    print("\n[ERROR] The following required libraries are missing:")
    for lib in missing_required:
        print(f" - {lib}")
    print("\nPlease install them using:")
    print(f"pip install {' '.join(missing_required)}")
    sys.exit(1)

# Import required libraries after successful check
import pandas as pd
import numpy as np
import wget
import matplotlib.pyplot as plt

# Check and import optional libraries
try:
    import seaborn as sns
    seaborn_available = True
except ImportError:
    seaborn_available = False
    print("[WARNING] seaborn is not installed. Availability heatmaps will be skipped.")

try:
    import cartopy.crs as ccrs
    cartopy_available = True
except ImportError:
    cartopy_available = False
    print("[WARNING] Basemap is not installed. Station location plotting will be skipped.")


import pandas as pd
import xarray as xr
import time
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# -----------------------------
# GHCNhProcessor Class Definition
# -----------------------------
class GHCNhProcessor:
    """
    A class for downloading, processing, and analyzing the Global Summary of the Day (GSD) data
    from the National Centers for Environmental Information (NCEI) - NOAA.
    """

    def __init__(self, start_year, end_year, area, output_dir):
        """
        Initialize the processor with configuration parameters.

        Parameters:
            start_year (int): The first year to download and process data.
            end_year (int): The last year to download and process data.
            area (list): Geographical boundaries [lat_min, lat_max, lon_min, lon_max].
            output_dir (str): Directory to save downloaded and processed data.
        """
        self.start_year = start_year
        self.end_year = end_year
        self.area = area
        self.output_dir = output_dir

        # DataFrames to store station information, download results, and availability data
        self.stations_df = None
        self.results_df = None
        self.combined_availability_df = None

        # Ensure the output directory exists
        self.ensure_directory_exists(self.output_dir)

    @staticmethod
    def ensure_directory_exists(directory):
        """Create the directory if it doesn't exist."""
        if not os.path.exists(directory):
            os.makedirs(directory)

    def load_station_data(self):
        """
        Load and filter station metadata based on the specified area.

        Returns:
            pd.DataFrame: DataFrame containing station information within the area.
        """
        la_min, la_max, lo_min, lo_max = self.area
        df = pd.read_csv(LIST_ISD_HISTORY)
        condition = (df['LATITUDE'].between(la_min, la_max)) & (df['LONGITUDE'].between(lo_min, lo_max))
        self.stations_df = df[condition]
        return self.stations_df

    def process_data(self, fil, odir, year, station_id, ofile=None, rm=True):
        """
        Process downloaded station data to calculate data availability.

        Parameters:
            fil (str): Path to the downloaded CSV file.
            odir (str): Directory to save processed files.
            year (int): Year of the data.
            station_id (str): Station identifier.
            ofile (str, optional): Output filename. Defaults to the original filename.
            rm (bool): Remove the original downloaded file after processing if True.

        Returns:
            pd.DataFrame: Availability matrix showing the proportion of available data.
        """
        
        try:
            d = pd.read_csv(fil, index_col=2, parse_dates=True, sep="|")

            # Drop unnecessary columns
            columns_to_drop = ['STATION', 'LATITUDE', 'LONGITUDE', 'Elevation', 'Station_name'] + \
                              [col for col in d.columns if 'ATTRI' in col]
            d = d.drop(columns=columns_to_drop, errors='ignore')

            # Define missing values for variables
            missing_values = {
                'TEMP': 9999.9, 'DEWP': 9999.9, 'SLP': 9999.9, 'STP': 999.9,
                'VISIB': 999.9, 'WDSP': 999.9, 'MXSPD': 999.9, 'GUST': 999.9,
                'MAX': 9999.9, 'MIN': 9999.9, 'PRCP': 99.99, 'SNDP': 999.9, 'FRSHTT': 99999
            }

            # Replace missing values with NaN
            for col in d.columns:
                if col != 'FRSHTT':
                    d[col] = pd.to_numeric(d[col], errors='coerce').replace(missing_values.get(col, np.nan), np.nan)

            # Insert time if a date is not found

            # Convert index to datetime type
            d.index = pd.to_datetime(d.index)

            # Create a full time range to fill missing values (example with 1-hour frequency)
            start_date, end_date =  pd.Timestamp(year, 1, 1),  pd.Timestamp(year+1, 1, 1)
            full_index = pd.date_range(start=start_date, end=end_date, freq='1h')[:-1]

            # Use reindex to add missing times, values automatically become NaN
            d = d.reindex(full_index) 

            # Calculate availability proportion per variable
            total_days = 366 if pd.Timestamp(year=year, month=12, day=31).is_leap_year else 365
            availability_data = {
                'Variable': d.columns,
                year: [(d[d.index.year == year][var].count() / len(d[d.index.year == year][var])) for var in d.columns]
            }
            availability_matrix = pd.DataFrame(availability_data).set_index('Variable')

            # Save processed data
            ofile = os.path.splitext(ofile)[0] + ".csv"

            self.ensure_directory_exists(odir)
            output_file = os.path.join(odir, ofile if ofile else os.path.basename(fil))
            d.to_csv(output_file, float_format='%.2f')

            return availability_matrix
        except Exception as e:
            print(f"Error processing {fil}: {e}")
            return pd.DataFrame()
        finally:
            # Optionally remove the original downloaded file
            if rm and os.path.exists(fil):
                os.remove(fil)

    def download_and_process_data(self, station_row):
        """
        Download and process data for a single station across the specified years.

        Parameters:
            station_row (pd.Series): Row from stations_df containing station metadata.

        Returns:
            tuple: (List of download results, Availability matrix DataFrame)
        """
        station_id = station_row['GHCN_ID']
        # station_start, station_end = pd.to_datetime(station_row['BEGIN']), pd.to_datetime(station_row['END'])

        results = []
        station_availability = pd.DataFrame()

        for year in range(self.start_year, self.end_year + 1):
            # Skip years outside station operational range
            # if year < station_start.year or (station_end.year != 2021 and year > station_end.year):
            #     results.append({'Station': station_id, 'Year': year, 'Status': 'Not Expected'})
            #     continue
            
            filename = f"GHCNh_{station_id}_{year}.psv"
            # output filename to store as csv file
            ofile = os.path.splitext(filename)[0] + ".csv"
            #URL to access and download
            url = f"{BASE_URL}{year}/psv/{filename}"

            try:
                downloaded_dir = os.path.join(self.output_dir, 'download')
                self.ensure_directory_exists(downloaded_dir)
                downloaded_file = os.path.join(downloaded_dir, filename)
                if os.path.exists(downloaded_file):
                    print(f"File {filename} is already exist")
                else:
                    print(f"Downloading: {url}")
                    downloaded_file = wget.download(url, out=downloaded_dir)
                    print("\nDownload completed.")

                year_output_dir = os.path.join(self.output_dir, str(year))
                self.ensure_directory_exists(year_output_dir)

                # Process the downloaded file
                availability_matrix = self.process_data(downloaded_file, year_output_dir, year, station_id, ofile, rm=False)

                # Append availability data
                if not availability_matrix.empty:
                    station_availability = station_availability.join(availability_matrix, how='outer') \
                        if not station_availability.empty else availability_matrix

                results.append({'Station': station_id, 'Year': year, 'Status': 'Success'})
                time.sleep(3)

            except Exception as e:
                print(f"Error for station {station_id}, year {year}: {e}")
                results.append({'Station': station_id, 'Year': year, 'Status': 'Failed'})

        station_availability.insert(0, 'Station', station_id)
        return results, station_availability

    def download_data(self):
        """
        Main workflow: load station data, download/process data, and save results.
        """
        self.stations_df = self.load_station_data()

        if self.stations_df.empty:
            print("No stations found in the specified area.")
            return

        print(f"Found {len(self.stations_df)} stations. Starting download and processing...")

        all_results = []
        all_availability_matrices = []

        # Process each station
        for id, station in self.stations_df.iterrows():
            print(f"\n--- Processing station: {station['GHCN_ID']} ---")
            station_results, availability_matrix = self.download_and_process_data(station)
            all_results.extend(station_results)

            if not availability_matrix.empty:
                all_availability_matrices.append(availability_matrix)

        # Compile results into DataFrames
        self.results_df = pd.DataFrame(all_results)
        self.combined_availability_df = pd.concat(all_availability_matrices, axis=0) if all_availability_matrices else pd.DataFrame()

        # Save results to output directory
        summary_dir = os.path.join(self.output_dir, "summaries")
        self.ensure_directory_exists(summary_dir)

        self.stations_df.to_csv(os.path.join(summary_dir, "stations_summary.csv"), index=False, float_format='%.2f')
        self.results_df.to_csv(os.path.join(summary_dir, "download_results.csv"), index=False, float_format='%.2f')
        self.combined_availability_df.to_csv(os.path.join(summary_dir, "availability_summary.csv"), float_format='%.2f')

        print("\nAll results have been saved successfully.")

    def plot_station_locations(self):
        """
        Plot all station locations categorized into:
        - Successful downloads (green)
        - Failed downloads (red)
        - Not expected downloads (gray)
        """
        if not cartopy_available:
            print("[INFO] Basemap is not available. Skipping station location plotting.")
            return

        if self.stations_df is None or self.results_df is None:
            print("Stations and results dataframes are required. Run the process first.")
            # return
            summary_dir = os.path.join(self.output_dir, "summaries")
            self.stations_df = pd.read_csv(os.path.join(summary_dir, "stations_summary.csv"))
            self.results_df = pd.read_csv(os.path.join(summary_dir, "download_results.csv"))
            self.combined_availability_df = pd.read_csv(os.path.join(summary_dir, "availability_summary.csv"))

        # Categorize stations based on download results
        success_stations = self.results_df[self.results_df['Status'] == 'Success']['Station'].unique()
        failed_stations = self.results_df[self.results_df['Status'] == 'Failed']['Station'].unique()
        not_expected_stations = self.results_df[self.results_df['Status'] == 'Not Expected']['Station'].unique()

        success_df = self.stations_df[self.stations_df['GHCN_ID'].isin(success_stations)]
        failed_df = self.stations_df[self.stations_df['GHCN_ID'].isin(failed_stations)]
        not_expected_df = self.stations_df[self.stations_df['GHCN_ID'].isin(not_expected_stations)]

        # Setup Basemap
        la_min, la_max, lo_min, lo_max = self.area
        # Define extent
        extent = [lo_min - 1, lo_max + 1, la_min - 1, la_max + 1]

        fig, ax = plt.subplots(
            figsize=(10, 8),
            subplot_kw={"projection": ccrs.Mercator()}
        )

        # Set map extent
        ax.set_extent(extent, crs=ccrs.PlateCarree())

        # Draw map features
        ax.add_feature(cfeature.COASTLINE, linewidth=0.8)
        ax.add_feature(cfeature.BORDERS, linewidth=0.8)
        ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth=0.5)  # US states, if needed
        ax.add_feature(cfeature.LAND, facecolor="lightgray")
        ax.add_feature(cfeature.OCEAN, facecolor="aqua")
        ax.add_feature(cfeature.LAKES, facecolor="aqua")

        # Plot station categories
        def plot_stations(df, color, label):
            if not df.empty:
                ax.scatter(
                    df["LONGITUDE"].values, df["LATITUDE"].values,
                    s=70, c=color, marker="o", edgecolors="k",
                    label=label, alpha=0.8,
                    transform=ccrs.PlateCarree()  # <-- required for lon/lat
                )

        plot_stations(success_df, 'green', 'Success')
        plot_stations(failed_df, 'red', 'Failed')
        plot_stations(not_expected_df, 'gray', 'Not Expected')

        plt.title("Station Download Status", fontsize=16)
        plt.legend(loc='upper right')
        summary_dir = os.path.join(self.output_dir, "summaries")
        self.ensure_directory_exists(summary_dir)
        map_path = os.path.join(summary_dir, f"station_location_map.png")
        plt.savefig(map_path)
        print(f"Saved : {map_path}")
        plt.show()

    def plot_availability_heatmaps(self):
        """
        Plot and save heatmaps showing data availability by year and variable.
        """
        if not seaborn_available:
            print("[INFO] Seaborn is not available. Skipping availability heatmaps.")
            return

        if self.combined_availability_df is None or self.combined_availability_df.empty:
            print("No availability data to plot.")
            return

        summary_dir = os.path.join(self.output_dir, "summaries")
        self.ensure_directory_exists(summary_dir)

        for station in self.combined_availability_df['Station'].unique():
            station_data = self.combined_availability_df[
                self.combined_availability_df['Station'] == station
            ].drop(columns=['Station'])
            station_data.columns = station_data.columns.astype(str)

            plt.figure(figsize=(10, 6))
            plt.title(f"Variable Availability for Station {station}")
            sns.heatmap(station_data, annot=True, cmap="YlGnBu", cbar_kws={'label': 'Proportion of Available Data'})
            plt.xlabel("Year")
            plt.ylabel("Variable")
            plt.tight_layout()

            heatmap_path = os.path.join(summary_dir, f"availability_heatmap_{station}.png")
            plt.savefig(heatmap_path)
            print(f"Saved heatmap to: {heatmap_path}")
            #plt.close()



# -----------------------------
# Example Usage
# -----------------------------
if __name__ == "__main__":

    # %%

    # File paths
    domain_id = 'Example'
    geo_em_d3 = f'../sample_data/simulation/wrf_output/{domain_id}/geo_em.d02.nc'

    ds = xr.open_dataset(geo_em_d3)
    min_lat = ds['XLAT_C'].values[0][0, 0]
    max_lat = ds['XLAT_C'].values[0][-1, 0]
    min_lon = ds['XLONG_C'].values[0][0, 0]
    max_lon = ds['XLONG_C'].values[0][0, -1]
    print([min_lat, max_lat, min_lon, max_lon])

    # %%

    dataset_type = {'GHCNh', 'psv'}
    dataset = 'GHCNh'
    area = [min_lat, max_lat, min_lon, max_lon]
    processor = GHCNhProcessor(
        start_year=2025,
        end_year=2025,
        area=area,
        output_dir=f"../sample_data/point_data/{dataset}"
    )

    processor.download_data()                    # Run data download and processing
    processor.plot_station_locations() # Plot station locations with categories
    processor.plot_availability_heatmaps()  # Plot heatmaps (if seaborn is available)
    
    
    
    
    
    
    
    