# FIREpyDAQ

firepydaq is Facilitated Interface for Recording Experiments (FIRE), a python based Data Acquisition (DAQ) system. Currently, it is geared towards devices that are traditionally used for data acquisition. More information can be found at <a href="https://github.com/dushyant-fire/fsripydaq/" target="_blank">firepydaq repository</a>

# Packaging brief for beginners

The comprehensive guide from <a href="https://py-pkgs.org/welcome" target="_blank">py-pkgs</a> will be helpful in case the following guidelines do not help.

To begin with packaging, you can either start by creating your own directories given below, or use the templates that `poetry` (For managing package dependencies) or `sphinx` (For documentation) could create for you. 

## Required modules/packages/formatting
We will start by looking at one section at a time. This section gives an overview of the process.

The repository format that worked reliably is given below. 

```
package_repo
├── .readthedocs.yml
├── CHANGELOG.md
├── CONDUCT.md
├── CONTRIBUTING.md
├── docs
│   ├── changelog.md
│   ├── conduct.md
│   ├── conf.py
│   ├── contributing.md
│   ├── example.ipynb
│   ├── index.md
│   ├── make.bat
│   ├── Makefile
│   └── requirements.txt
├── LICENSE
├── README.md
├── pyproject.toml
├── poetry.lock
├── Makefile
├── package_repo
│   ├── __init__.py
│   ├── main.py
│   ├── moduleA
│   │   ├── __init__py
│   │   └── moduleA.py
│   ├── moduleB
│   │   ├── __init__py
│   │   └── moduleBfile.py
└── tests
    ├── __init__.py
    └── test_package.py

```

Basic steps that reliably worked:

## Poetry installation and makefile for package testing
- Put all the code inside the directory of the same name
- Remove all absolute path references, use `from .ModuleFile1 import Function11` to import a file from a specific file in the same directory. To import from level up, use `from ..level_0.Module0File import Function01`.
- Install poetry in a virtual environment as suggested by poetry. You will need `pipx` for this. Install [`pipx`](https://pipx.pypa.io/stable/installation/) using the methods indicated on the pipx webpage. Install `poetry` as indicated on [poetry webpage](https://python-poetry.org/docs/).
- Create .toml file by `poetry init`. Based on user input, it will create a basic `pyproject.toml` file, which will look something like this. You can even copy the following and update the relevant information. Leave the `build-system` the way it is.

```
[tool.poetry]
name = "firepydaq"
version = "0.1.0"
description = "A user-interface to read data during experiments"
authors = ["Dushyant Chaudhari <dush.chaudhari@gmail.com>"]
license = "GNU General Public v3"
readme = "README.md"

[tool.poetry.dependencies]
python = ">=3.9,<3.13"
nidaqmx = "^1.0.0"
alicat = "0.6.2"
dash = "2.17.1"
dash-auth = "2.3.0"
dash-bootstrap-components = "1.6.0"
matplotlib = "3.8.4"
numpy = "1.26.0"
pandas = "2.2.2"
plotly = "5.22.0"
polars = "1.1.0"
pyarrow = "14.0.2"
pyqtgraph = "0.13.7"
pyserial = "3.5"
PySide6 = "6.7.2"
PyVISA = "1.14.1"
jsonschema = "4.23.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```
- Once the `.toml` file is read, you can call `poetry build`, which will create a `dist` folder that will have two files. The first is a wheel (`.whl`) file and the other is an sdits (`.tar.gz`) file. You can walk into the `dist` file and run `pip install ...whl` file. This will install this package locally. You can also share these wheels or dist files for installation of your package. 

- To automate the poetry functions, a Makefile makes life easier. Makefile require installation of make, which needs to be further explored. Once make is available, create an empty `Makefile` and add commands as below. No you can simple run `make build` from your terminal/command prompt to autmate building of the dist, creating poetry.lock, and installing the lock file in the virtual environment automatically created by poetry.

```
POETRY_OPTS ?=
POETRY ?= poetry $(POETRY_OPTS)
RUN_PYPKG_BIN = $(POETRY) run

##@ Building and Publishing

.PHONY: build
build: ## Runs a build
    $(POETRY) build
    $(POETRY) lock
    $(POETRY) install
```
- If you type `poetry env info`, it will list the virtual env you are working on. This virtual environment will have all the package dependencies installed so that you can run your package now in this environment.

- To test a package in the poetry environment, you can install `pytest` that lets you run a specific set of files that begin or end with `test_` or `_test` respectively inside the `tests` directory.
- You can create a `test_package.py` inside `tests`, which could have various functions for testing. by default `pytest` will only test functions that also has similar naming structure (`test_` or `_test`).
- Before you can test, you will need to add a way for poetry to know that it needs to use pytest for testing the package. This can be done by calling the following two functions in cmd/terminal.

```
$ poetry add --group dev pytest
```
which will add the following lines in `pyproject.toml` file

```
[tool.poetry.group.test.dependencies]
pytest = "^8.2.2"
```

- Once this is done, you can run `poetry run pytest -v` directly and it will tell you in terminal how many `test_` or `_test` functions were tested. The success of running those functions is the passing criteria. Any failure is indicated in the terminal with the source of the error. The verbose option (`-v`) will output the succes/failure of each collected test functions.
- Alternatively, you can add a `test` `PHONY` to the Makefile and run `make test` to initiate the testing.

```
##@ Testing

.PHONY: test
test: ## Runs tests
    $(RUN_PYPKG_BIN) pytest -v \
        tests/*.py
```

## Documentation using sphinx
- Once you test that the package building works fine, you can move to documentation.
- Documentation will be compiled using sphinx, a commonly used resource for auto compilation. You can start by writing CONDUCT.md, CONTRIBUTING.md, CHANGELOG.md in the root folder. The references for each can be found in almost all packages.
- To begin building you will first need to add the following to poetry configuration.

```
$ poetry add --group dev myst-nb --python "^3.9"
$ poetry add --group dev sphinx-autoapi sphinx-rtd-theme

```
which will add the following to the `pyproject.toml` file.

```
[tool.poetry.group.dev.dependencies]
myst-nb = {version = "^1.1.1", python = "^3.9"}
sphinx-autoapi = "^3.1.2"
sphinx-rtd-theme = "^2.0.0"
```
- Before we move on to building the documentation, we need a couple more things. First is the `docs` folder which contains `index.md`. Contents of index.md look something like below. Here, you will need to create `changelog.md`, `contributing.md`, and `conduct.md` that refer to the corresponding files in the root folder as how is done for `README.md` below. The reason for this is that sphinx does not support relative references in `toctree`.

````
    ```{include} ../README.md
    ```

    ```{toctree}
    :maxdepth: 1
    :hidden:

    changelog.md
    contributing.md
    conduct.md
    autoapi/index
    ```
````
- Next thing needed is `conf.py`, `Makefile`, and `make.bat` files in the docs folder. These could have been created automatically if you used a `cookiecutter`. But to create them manually, the contents for each need to include the following (the basic minimum).
- For `conf.py`, include the extensions required to build a sphinx documentation, the directory to build autoapis (by reading the code docstrings), and the theme. You may need to install the extensions, and the html theme manually if poetry cannot build the documentation for you and if you are required to do as a local copy directly. This is possibly due to some issues with `Makefile` or `make.bat` (for windows).

```
extensions = [
    "myst_nb",
    "autoapi.extension",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]
autoapi_dirs = ["../src"]  # location to parse for API reference
html_theme = "sphinx_rtd_theme"
```
- The Makefile has basic info as follows,

```
# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SPHINXPROJ    = PACKAGE_NAME
SOURCEDIR     = .
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
help:
    @$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
    @$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
```
and the make.bat has the following,

```
@ECHO OFF

pushd %~dp0

REM Command file for Sphinx documentation

if "%SPHINXBUILD%" == "" (
    set SPHINXBUILD=sphinx-build
)
set SOURCEDIR=.
set BUILDDIR=_build
set SPHINXPROJ=PACKAGE_NAME

if "%1" == "" goto help

%SPHINXBUILD% >NUL 2>NUL
if errorlevel 9009 (
    echo.
    echo.The 'sphinx-build' command was not found. Make sure you have Sphinx
    echo.installed, then set the SPHINXBUILD environment variable to point
    echo.to the full path of the 'sphinx-build' executable. Alternatively you
    echo.may add the Sphinx directory to PATH.
    echo.
    echo.If you don't have Sphinx installed, grab it from
    echo.http://sphinx-doc.org/
    exit /b 1
)

%SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR% %SPHINXOPTS%
goto end

:help
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS%

:end
popd
```

- With these in place, you can compile the basic documentation by running `make html` command in the `docs` folder. This will create `_build/html/index.html`, which you can open and see the locally compiled documentation.

## Deploying on github/version control

Next steps, along with corresponding larger documentation
