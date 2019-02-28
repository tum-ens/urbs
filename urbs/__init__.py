"""urbs: A linear optimisation model for distributed energy systems

urbs minimises total cost for providing energy in form of desired commodities
(usually electricity) to satisfy a given demand in form of timeseries. The
model contains commodities (electricity, fossil fuels, renewable energy
sources, greenhouse gases), processes that convert one commodity to another
(while emitting greenhouse gases as a secondary output), transmission for
transporting commodities between sites and storage for saving/retrieving
commodities.

"""

from .data import COLORS
from .input import read_excel
from .validation import validate_input
from .runfunctions import *
from .scenarios import *
