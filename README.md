# wrf_tools

A Python library to process WRF simulations and download ERA5 data.

## Installation
If you want to use [wrf-python](https://wrf-python.readthedocs.io/en/latest/index.html), we recommend using [conda](https://www.anaconda.com/docs/getting-started/miniconda/install#using-miniconda-in-a-commercial-setting) for installation.

You can install necessary enviroments from enviroment.yaml
```bash
conda env create -f environment.yml
```

- Manualy installation.

```bash
conda install -c conda-forge wrf-python
```

You can install it using the following command after downloading it.
```bash
git clone https://github.com/AtmosSciTools/WRF_tools.git
```

```bash
pip install git+https://github.com/AtmosSciTools/WRF_tools.git@feature/visualization
```

## Usage

```python
from wrf_tools import WRFProcessor, ERA5DataDownloader
```
More details in [docs/wrf_tools_usage.md](./docs/wrf_tools_usage.md)


## Analysis and Visualization of WRF output in [notebook](./notebooks/visualization/)

