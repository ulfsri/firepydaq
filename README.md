<p align="center">
  <img src="docs/FIREpyDAQDark.png" alt= “FIREpyDAQ” width="30%" height="30%">
</p> 

<div align="center">

<!-- Releases -->
![GitHub Release](https://img.shields.io/github/v/release/ulfsri/firepydaq?style=flat-square&labelColor=black&color=blue)
![PyPI - Version](https://img.shields.io/pypi/v/firepydaq?style=flat-square&labelColor=black&color=blue)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/firepydaq?style=flat-square&labelColor=black&color=blue)
![GitHub License](https://img.shields.io/github/license/ulfsri/firepydaq?style=flat-square&labelColor=black&color=blue)

<!-- Workflows -->
[![Pytest](https://github.com/ulfsri/firepydaq/actions/workflows/RunPytest.yml/badge.svg?branch=main)](https://github.com/ulfsri/firepydaq/actions/workflows/RunPytest.yml)
[![Exe Release](https://github.com/ulfsri/firepydaq/actions/workflows/MakeExe.yml/badge.svg)](https://github.com/ulfsri/firepydaq/actions/workflows/MakeExe.yml)
[![.github/workflows/BuildDists.yml](https://github.com/ulfsri/firepydaq/actions/workflows/BuildDists.yml/badge.svg?branch=main)](https://github.com/ulfsri/firepydaq/actions/workflows/BuildDists.yml)


<!-- Followers and usage -->
![GitHub forks](https://img.shields.io/github/forks/ulfsri/firepydaq?style=flat-square&labelColor=brown&color=green)
![GitHub Repo stars](https://img.shields.io/github/stars/ulfsri/firepydaq?style=flat-square&labelColor=brown&color=green)
![GitHub watchers](https://img.shields.io/github/watchers/ulfsri/firepydaq?style=flat-square&labelColor=brown&color=green)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/ulfsri/firepydaq?style=flat-square&labelColor=brown&color=green)
![Coverage](tests/coverage.svg)
</div>

# firepydaq

FIREpyDAQ is a python based Facilitated Interface for Recording Experiments (FIRE), for devices that are generally used for data acquisition in engineering research. The device list and general requirements are given below.

## Installation

Using `pip`, you can install this package. `pip` will also install relevant dependencies.

```bash
$ pip install firepydaq
```
## Hardware/Communication Requirements

This interface can be used for three types of devices simultaneously,

- NI hardware, which requires installation of <a href="https://www.ni.com/en/support/downloads/drivers/download.ni-daq-mx.html#532710" target="_blank">NI-DAQmx driver</a> from National Instruments.
	- This has been built so far only for Analog Input and Output data.
- Alicat Mass Flow Controllers and Mass Flow Meter, which is based via serial communication and python API available from <a href="https://github.com/numat/alicat" target="_blank">Numat</a>.
- Thorlabs CLD101X, which is based on serial communication

## Usage

**A brief usage is provided below. Please refer to the documentation for additional details.**

`firepydaq` can be used to compile PyQT based user interface.

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

Example of how Acquisition interface looks like:
![Acquisition Setup](docs/assets/Acquisition/SetUp1.png)

Example of NI config that is required to set-up the acquisition. You can formulate your own config file. You can use the `NISYSCheck.py` utility to get information of the connected NI device.
![ConfigExample](docs/assets/Setup/ConfigExample.png)

Example of Formulae file that is used to post-process data is display in dashboard is selected.
![ConfigExample](docs/assets/Setup/FormulaeExample.png)

Example of Acquisition interface during acquisition:
![Acquisition](docs/assets/Acquisition/16.png)

Example of how the dashboard looks like during acquisition:
![Dashboard](docs/assets/Dashboard/Dashboard2.png)

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
```

Chaudhari, D. M., Mishra, A., (2024). Facilitated interface for recording experiments - a python-based data acquisition program. In Github Repository. Fire Safety Research Institute, UL Research Institutes; Github. https://github.com/ulfsri/firepydaq

```

Bib:
```
@misc{firepydaq,
title={Facilitated Interface for Recording Experiments - A python-package for data acquisition.},
howpublished = {Fire Safety Research Institute, UL Research Institutes},
url = {https://github.com/ulfsri/firepydaq},
author = {Dushyant M. Chaudhari, Anvii Mishra},
publisher = {Github},
journal = {Github Repository},
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

Additionally, the contributors are grateful for the support from [Fire Safety Research Institute](fsri.org), a part of [UL Research Institutes](ul.org), for this project.

