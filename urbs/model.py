import math
import pyomo.core as pyomo
from datetime import datetime
from .modelhelper import *
from .input import *
from .min_model import*


def create_model(data, mode, timesteps=None, dt=1, dual=False):
    """Create a pyomo ConcreteModel urbs object from given input data.

    Args:
        data: a dict of 6 DataFrames with the keys 'commodity', 'process',
            'transmission', 'storage', 'demand' and 'supim'.
        mode: a bool vector giving the mode in the model should be run
        timesteps: optional list of timesteps, default: demand timeseries
        dt: timestep duration in hours (default: 1)
        dual: set True to add dual variables to model (slower); default: False

    Returns:
        a pyomo ConcreteModel object
    """

    # Optional
    if not timesteps:
        timesteps = data['demand'].index.tolist()

    m = pyomo_model_prep(data, mode, timesteps)  # preparing pyomo model
    m.name = 'urbs'
    m.created = datetime.now().strftime('%Y%m%dT%H%M')
    m._data = data 

    #creating minimum model
    m = create_min_model_sets(m)
    m = create_min_model_tuples(m)
    m = create_params(m)
    m = create_min_model_vars(m)
    m = declare_min_model_equations(m)
    
    if dual:
        m.dual = pyomo.Suffix(direction=pyomo.Suffix.IMPORT)
    return m