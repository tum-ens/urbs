"""urbs: A linear optimisation model for distributed energy systems

urbs minimises total cost for providing energy in form of desired commodities
(usually electricity) to satisfy a given demand in form of timeseries. The
model contains commodities (electricity, fossil fuels, renewable energy
sources, greenhouse gases), processes that convert one commodity to another
(while emitting greenhouse gases as a secondary output), transmission for
transporting commodities between sites and storage for saving/retrieving
commodities.

nopt: an extension to urbs. nopt uses urbs cost minimisation as a first step to find optimum cost and than modifies th
optimisation problem to do near optimal feasible space analysis
"""


from .colorcodes_nopt import COLORS
from .model_nopt import create_model
from .input_nopt import *
from .validation_nopt import validate_input
from .output_nopt import get_constants, get_timeseries
from .plot_nopt import plot, result_figures, to_color
from .pyomoio_nopt import get_entity, get_entities, list_entities
from .report_nopt import report
from .runfunctions_nopt import *
from .saveload_nopt import load, save
from .scenarios_nopt import *
from .identify_nopt import identify_mode, identify_expansion