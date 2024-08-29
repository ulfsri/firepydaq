<p align="center">
  <img src="docs/FIREpyDAQDark.png" alt= “FIREpyDAQ” width="30%" height="30%">
</p> 

<div align="center">

<!-- Releases -->
![GitHub Release](https://img.shields.io/github/v/release/ulfsri/firepydaq?style=flat-square&labelColor=black&color=blue)
![PyPI - Version](https://img.shields.io/pypi/v/firepydaq?style=flat-square&labelColor=black&color=blue)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/firepydaq?style=flat-square&labelColor=black&color=blue)
![GitHub License](https://img.shields.io/github/license/ulfsri/firepydaq?style=flat-square&labelColor=black&color=blue)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.13486708.svg)](https://doi.org/10.5281/zenodo.13486708)

<!-- Workflows -->
[![Pytest](https://github.com/ulfsri/firepydaq/actions/workflows/RunPytest.yml/badge.svg?branch=main)](https://github.com/ulfsri/firepydaq/actions/workflows/RunPytest.yml)
![Coverage](tests/coverage.svg)

<!-- Followers and usage -->
![GitHub forks](https://img.shields.io/github/forks/ulfsri/firepydaq?style=flat-square&labelColor=brown&color=green)
![GitHub Repo stars](https://img.shields.io/github/stars/ulfsri/firepydaq?style=flat-square&labelColor=brown&color=green)
![GitHub watchers](https://img.shields.io/github/watchers/ulfsri/firepydaq?style=flat-square&labelColor=brown&color=green)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/ulfsri/firepydaq?style=flat-square&labelColor=brown&color=green)

</div>

# FIREpyDAQ

FIREpyDAQ is a python based Facilitated Interface for Recording Experiments (FIRE), for devices that are generally used for data acquisition in engineering research. The device list and general requirements are given below.

## Installation

Using `pip`, you can install this package. `pip` will also install relevant dependencies. 

```bash
$ pip install firepydaq
```

Else, you can clone this repository and use `poetry` to compile the project locally. 
Once cloned, you can do the following to create a virtual environment using poetry.
```bash
# Create and Install package dependencies. 
$ poetry install
# To activate the virtual environment, unless the IDE you use automatically does this for you
$ poetry shell
```
## Hardware/Communication Requirements

This interface can be used for three types of devices simultaneously,

- NI hardware, which requires installation of <a href="https://www.ni.com/en/support/downloads/drivers/download.ni-daq-mx.html#532710" target="_blank">NI-DAQmx driver</a> from National Instruments.
	- This has been built so far only for Analog Input and Output data.
- Alicat Mass Flow Controllers and Mass Flow Meter, which is based via serial communication and python API available from <a href="https://github.com/numat/alicat" target="_blank">Numat</a>.
- Thorlabs CLD101X, which is based on serial communication

## Usage

**Please refer to the documentation for additional details.**

`firepydaq` can be compiled by using one of the following scripts.

```python
# On Windows: Protect your script from importing child processes
# Required if you need dashboard access.
# Dashboard is spawned as a separate process. 
if __name__ == "__main__":
    from firepydaq.FIREpyDAQ_Acquisition import FIREpyDAQ_Acquisition
    FIREpyDAQ_Acquisition()

```

Alternatively, you can run the following.
 
```python
# On Windows: Protect your script from importing child processes 
# Required if you need dashboard access.
# Dashboard is spawned as a separate process. 
if __name__ == "__main__":
	import multiprocessing as mp
	mp.freeze_support()
	from firepydaq.acquisition.acquisition import application
	import sys
	from PySide6.QTWidgets import QApplication

	app = QApplication(sys.argv)
	main_app = application()
	main_app.show()
	sys.exit(app.exec())
```

### Interface

Example usage is given in the following two videos. The corresponding files and two snapshots are provided after the video for reference.

- FIREpyDAQ Setup
![FIREpyDAQ Setup Video](docs/assets/FIREpyDAQSetup.gif)

- FIREpyDAQ Acquisition and Dashboard
![FIREpyDAQ Acquisition Video](docs/assets/FIREpyDAQAcqDash.gif)

### Config and Formulae file

Example of NI config that is required to set-up the acquisition. You can formulate your own config file. You can use the `NISYSCheck.py` utility to get information of the connected NI device.

|**\#**| **Panel** | **Device** | **Channel** | **ScaleMax** | **ScaleMin** | **Label** | **Type**     | **TCType**   | **Chart** | **AIRangeMin** | **AIRangeMax** | **Layout** | **Position** | **Processed\_Unit** | **Legend** |
|-----------|------------|-------------|--------------|--------------|-----------|--------------|--------------|-----------|----------------|----------------|------------|--------------|--------------------|------------|--------------|
| 0         | 1          | cDAQ1Mod1   | ai0          | 1            | 1         | Temperature1 | Thermocouple | K         | Temperature    | 1              | 1          | 2            | 1                  | C          | Temperature1 |
| 1         | 1          | cDAQ1Mod1   | ai2          | 1            | 1         | Temperature2 | Thermocouple | K         | Temperature    | 1              | 1          | 2            | 1                  | C          | Temperature2 |
| 2         | 1          | cDAQ1Mod3   | ai0          | 1            | 0         | Voltage1     | Voltage      | NA        | V1             | 0              | 1          | 1            | 1                  | V          | Open V1      |
| 3         | 1          | cDAQ1Mod3   | ai2          | 1            | 0         | Voltage2     | Voltage      | NA        | None           | 0              | 1          | 1            | 1                  | C          | Open V2      |


Example of Formulae file that is used to post-process data is display in dashboard is selected.

| **Label** | **RHS**                            | **Chart**       | **Legend**      | **Layout** | **Position** | **Processed\_Unit** |
|-----------|------------------------------------|-----------------|-----------------|------------|--------------|--------------------|
| TF_mult   | 9/5                                | None            | TF_mult         | 1          | 1            | -                  |
| TF_offset | 32                                 | Constant        | TF_mult         | 1          | 1            | -                  |
| Temp_F    | (Temperature1)*TF_mult + TF_offset | Temperature     | Fahrenheit temp | 2          | 2            | F                  |
| T_mean    | (Temperature1 + Temperature2)/2    | Mean Temperture | Mean Temp       | 1          | 1            | C                  |
| V_mA      | Voltage1/1000                      | V1 (mV)         | Volts           | 1          | 1            | mA                 |

## Contributing

Interested in contributing? Check out the [contributing guidelines](CONTRIBUTING.md). 
Please note that this project is released with a Code of Conduct. 
By contributing to this project, you agree to abide by its terms.

Suggested procedure is given below. Note: Pull request into the `main` branch will not be accepted.

- Fork this repository.
- Create a `your_feature` branch from the `dev` branch. 
- Clone your repository on your machine.
- Install poetry using `pipx` as recommended or using `pip`, and `make` (optional). 
- If you install and configure `make` - run `make build`, which will initiate the commands `poetry build`, `poetry lock`, and `poetry install` in succession. This will create a virtual environment for testing your developments.
- Alternatively (without `make`), you can run individual `poetry` commands to install the package on a virtual environment (ideal) for local development.
- Make your edits, and send a PR following the template. 

## License

`firepydaq` was created by Dushyant M. Chaudhari. It is licensed under the terms
of the GNU General Public license, v.3.0.

## Citation

Full citation:
```{note}
Chaudhari, D. M., & Mishra, A. (2024). FIREpyDAQ: Facilitated Interface for Recording Experiments (FIRE), a python-package for Data Acquisition. (v0.1.0). Zenodo. https://doi.org/10.5281/zenodo.13486708
```

Bib:
```
@misc{firepydaq,
title={FIREpyDAQ: Facilitated Interface for Recording Experiments (FIRE), a python-package for Data Acquisition. (v0.1.0)},
url = {https://github.com/ulfsri/firepydaq},
author = {Chaudhari, Dushyant M. and Mishra, Anvii},
publisher = {Zenodo},
doi = {10.5281/zenodo.13486708},
year = {2024}
}
```

## Acknowledgements

Thanks to the following community guidelines which were immensely helpful while making this package.

- <a href="https://py-pkgs.org/welcome" target="_blank">py-pkgs</a>
- <a href="https://coderefinery.github.io/documentation/" target="_blank">Code refinery documentation</a>
- <a href="https://www.sphinx-doc.org/en/master/usage/index.html" target="_blank">Sphinx documentation</a>
- <a href="https://sphinx-autoapi.readthedocs.io/en/latest/" target="_blank">Sphinx AutoAPI documentation</a>
- <a href="https://numpydoc.readthedocs.io/en/latest/format.html" target="_blank">Numpy docstrings style guide</a>
- <a href="https://packaging.python.org/en/latest/" target="_blank">Python packaging guide</a>
- <a href="https://www.pythonguis.com/pyside6/" target="_blank">PythonGUIs, by Martin FitzPatrick</a>

Additionally, the contributors are grateful for the support from [Fire Safety Research Institute](https://fsri.org/?utm_source=sphinx-documentation&utm_medium=direct&utm_campaign=FIREpyDAQ-public-launch), a part of [UL Research Institutes](https://ul.org/?utm_source=sphinx-documentation&utm_medium=direct&utm_campaign=FIREpyDAQ-public-launch), for this project.

