# URBS

URBS is a [linear programming](https://en.wikipedia.org/wiki/Linear_programming) optimisation model for capacity expansion planning and unit committment for distributed energy systems. Its name, latin for city, stems from its origina as a model for optimisation for urban energy systems. Since then, it has been adapted to multiple scales from neighbourhoods to to continents.

## Features

  * URBS is a linear programming model for multi-commodity energy systems with a focus on optimal storage sizing and use.
  * It finds the minimum cost energy system to satisfy given demand timeseries for possibly multiple commodities (e.g. electricity).
  * By default, operates on hourly-spaced timesteps (configurable).
  * Thanks to [Pandas](https://pandas.pydata.org), complex data analysis is easy.
  * The model itself is quite small (<50 kB source code) thanks to relying on the [Coopr](https://software.sandia.gov/trac/coopr)/[Pyomo](https://software.sandia.gov/trac/coopr/wiki/Pyomo) and includes reporting and plotting functionality.

## Screenshots

[![](http://ojdo.de/dw/_media/software:urbs:scenario_all_together-elec-north.png?w=400&tok=a9a9d8)](http://ojdo.de/dw/_media/software:urbs:scenario_all_together-elec-north.png)

[![](http://ojdo.de/dw/_media/software:urbs:comp.png?w=400&tok=0e5b95)](http://ojdo.de/dw/_media/software:urbs:comp.png)

## Installation

### Windows

For all packages, best take the latest release or release candidate version. Both 32 bit and 64 bit versions work, though 64 bit is recommended.

  1. **[Python 2.7](https://python.org/download)**. Python 3 support is not possible yet, but planned once all used packages support it.
  2. **[pip](https://pip.pypa.io/en/latest/installing.html)** .The Python package manager. Facilitates installing many packages. After installation, add `C:\Python27\Scripts` to environment variable "Path" ([how](http://geekswithblogs.net/renso/archive/2009/10/21/how-to-set-the-windows-path-in-windows-7.aspx)), so that the `pip` command becomes available on the command prompt.
  3. **IPython**: execute `pip install ipython` in a command prompt.
  4. **SciPy stack:** These require binary installers, made available and maintained by [C. Gohlke](http://www.lfd.uci.edu/~gohlke/pythonlibs/). *How to select the correct file:* Download the newest stable version eache package, whose filename suffix matches both "bitness" (32 bit or 64 bit) and Python version (i.e. 2.7).  
      1. [Numpy](http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy)
      2. [SciPy](http://www.lfd.uci.edu/~gohlke/pythonlibs/#scipy)
      3. [Matplotlib](http://www.lfd.uci.edu/~gohlke/pythonlibs/#matplotlib), requires [dateutil](http://www.lfd.uci.edu/~gohlke/pythonlibs/#python-dateutil), [pytz](http://www.lfd.uci.edu/~gohlke/pythonlibs/#pytz), [pyparsing](http://www.lfd.uci.edu/~gohlke/pythonlibs/#pyparsing) and [six](http://www.lfd.uci.edu/~gohlke/pythonlibs/#six). Now you can start `ipython --pylab` and have a MATLAB-style command line with plotting capabilities.
  5. **[Pandas](https://pypi.python.org/pypi/pandas#downloads)**: its [Series](http://pandas.pydata.org/pandas-docs/stable/dsintro.html#series) and [DataFrame](http://pandas.pydata.org/pandas-docs/stable/dsintro.html#dataframe) are used for representing all model input and output.
  6. **[Coopr](https://software.sandia.gov/trac/coopr/downloader/)**: minimum version 3.5 or the VOTD (Version of the Day) installer. As of 2014-08-01, only the latter is available for Windows users.
  7. **Solver**: [GLPK](http://winglpk.sourceforge.net/). Simply unzip the latest version somewhere, e.g. `C:\GLPK`. Then add the directory containing `glpsol.exe` to the system path (like in step 2), so that the `glpsol` command is available. Other supported solvers are - among others - CPLEX and Gurobi.
  8. **Excel I/O** dependencies for Pandas: `pip install xlrd xlwt openpyxl==1.8.6` (Reason for version: Pandas only [supports openpyxl < 2.0.0 as of 2014-07-22](https://github.com/pydata/pandas/blob/master/pandas/compat/openpyxl_compat.py))

### Linux

Use the package manager to get all the packages listed in the Windows installation section. Below is the installation procedure for Ubuntu & Debian. Other distributions might have slightly different package names or differing procedures to get the individual packages to run:

  - **Everything** except Coopr & Excel I/O `sudo apt-get install python python-pip python-numpy python-scipy python-matplotlib ipython ipython-notebook python-pandas python-sympy python-nose glpk-utils`
  - **Coopr & Excel I/O** `sudo pip install coopr xlwt xlrd openpyxl==1.8.6`

## Get started

Once installation is complete, clone (or download) this repository and execute the run script in CMD:

    git clone https://github.com/tum-ens/urbs.git
    cd urbs
    python runme.py

About a minute later, the folder `results` should contain plots and summary spreadsheets for multiple optimised energy supply scenarios, whose definition is contained in the run script (whatch out for `def scenario` lines). To get a graphical and tabular summary over all scenarios, execute

    python comp.py

and look at the new files `results/comp.xlsx` and `results/comp.png` for a quick comparison. This script parses the summary spreadsheets for all scenarios.

## Next steps

  1. Read the source code of `runme.py` and `comp.py`. 
  2. Quickly scan through `urbs.py`, read docstrings.
  3. Try adding/modifying scenarios in `runme.py` and see their effect on results.
  4. Fire up IPython (`ipython --pylab`) and run the scripts from there using the run command: `run runme` and `run comp`. Then use `whos` and inspect the workspace afterwards (`whos`). See what you can do (analyses, plotting) with the DataFrames. Take the `urbs.get_constants`, `urbs.get_timeseries` and `urbs.plot` functions as inspriation and the [Pandas docs](http://pandas.pydata.org/pandas-docs/stable/) as reference.
