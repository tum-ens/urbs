import os
import pandas as pd
import pyomo.environ
import shutil
import urbs
from datetime import datetime
from pyomo.opt.base import SolverFactory

input_files = urbs.read_intertemporal('Input')
print (len(input_files))