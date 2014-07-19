# URBS

URBS is a [linear programming](https://en.wikipedia.org/wiki/Linear_programming) optimisation model for capacity expansion planning and unit committment for distributed energy systems. Its name, latin for city, stems from its origina as a model for optimisation for urban energy systems. Since then, it has been adapted to multiple scales from neighbourhoods to to continents.

## Features

  * URBS is a linear programming model for multi-commodity energy systems with a focus on optimal storage sizing and use.
  * It searches the minimum cost energy system to satisfy given demand timeseries for possibly multiple commodities (e.g. electricity).
  * By default, operates on hourly-spaced timesteps (configurable).
  * Thanks to [Pandas](https://pandas.pydata.org), complex data analysis become easy.
  * The model itself is small (<50 kB source code) and includes reporting and plotting functionality.
  * Obsessively documented code to make the model as moddable as possible.

## Screenshots

[![](http://ojdo.de/dw/_media/software:urbs:scenario_all_together-elec-north.png?w=400&tok=a9a9d8)](http://ojdo.de/dw/_media/software:urbs:scenario_all_together-elec-north.png)

[![](http://ojdo.de/dw/_media/software:urbs:comp.png?w=400&tok=0e5b95)](http://ojdo.de/dw/_media/software:urbs:comp.png)

## Installation

### Windows

Both 32 bit and 64 bit versions should work. For all packages, always take the latest release or - if you feel brave - development/release candidate version.

  1. **[Python 2.7](https://python.org/download)** Unfortunately, the Coopr package is not (yet) compatible with Python 3.
  2. **[pip](https://pip.pypa.io/en/latest/installing.html)** The Python package manager. Facilitates installing many packages. Add `C:\Python27\Scripts` to system path ([how](http://geekswithblogs.net/renso/archive/2009/10/21/how-to-set-the-windows-path-in-windows-7.aspx), so that the `pip` command is found.
  3. **IPython**: `pip install ipython`, automatically installs the pyreadline dependency.
  4. **SciPy stack:** These require binary installers.
      1. [Numpy](http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy)
      2. [SciPy](http://www.lfd.uci.edu/~gohlke/pythonlibs/#scipy)
      3. [Matplotlib](http://www.lfd.uci.edu/~gohlke/pythonlibs/#matplotlib), requires [dateutil](http://www.lfd.uci.edu/~gohlke/pythonlibs/#python-dateutil), [pytz](http://www.lfd.uci.edu/~gohlke/pythonlibs/#pytz), [pyparsing](http://www.lfd.uci.edu/~gohlke/pythonlibs/#pyparsing) and [six](http://www.lfd.uci.edu/~gohlke/pythonlibs/#six).
      ---
      Now you can start `ipython --pylab` and have a MATLAB-style command line with plotting capabilities.
      ---
  5. **[Pandas](https://pypi.python.org/pypi/pandas#downloads)** is the data workhorse in this model.
  6. **[Coopr](https://software.sandia.gov/trac/coopr/downloader/)** at least version 3.5 or the VOTD installer.
  7. **Solver** like [GLPK](http://winglpk.sourceforge.net/). Add the installation directory to the system path, so that the `glpsol` command is found. Other supported solvers are CPLEX and Gurobi (if available executables).
  8. **Last dependencies** for Excel I/O: `pip install xlrd xlwt openpyxl==1.8.6`
  (Reason vor version: Pandas only [supports openpyxl < 2.0.0 as of 2014-07-11](https://github.com/pydata/pandas/blob/master/pandas/compat/openpyxl_compat.py))

### Linux

Just use the package manager to get the packages mentioned in the Windows installation. Below is the installation procedure for Ubuntu & Debian. Other distributions might have slightly different package names:

  - **Everything** except Coopr & Excel I/O `sudo apt-get install python python-pip python-numpy python-scipy python-matplotlib ipython ipython-notebook python-pandas python-sympy python-nose glpk-utils`
  - **Coopr & Excel I/O** `sudo pip install coopr xlwt xlrd openpyxl==1.8.6`


## Get started

Once you have followed the steps under Installation and have [Git](http://git-scm.com/) installed, execute the following:

    git clone //nas.ads.mwn.de/tuei/ens/Methoden/Modelle/Pyomo/URPS.git urbs
    cd urbs
    python runme.py

Less than a minute((YMMV, depending on your hardware)) later, inspect the folder `results` for plots and summaries for multiple optimised energy supply scenarios. To get a graphical and tabular summary over all scenarios, execute

    python comp.py

and look at `comp.xlsx` and `comp.png` for a quick comparison.

## Next steps

  - Read the source code of `runme.py` and `comp.py`. 
  - Quickly scan through `urbs.py`, read docstrings.
  - Try adding scenarios in `runme.py` and see their effect on results.
  - Fire up IPython `ipython --pylab` and execute the scripts from there using the run command: `run runme` and `run comp`. Then use `whos` and inspect the workspace. See what you can do (analyses, plotting) with the DataFrames. Take the `urbs.get_constants`, `urbs.get_timeseries` and `urbs.plot` functions as inspriation and the [Pandas docs](http://pandas.pydata.org/pandas-docs/stable/) as reference.
