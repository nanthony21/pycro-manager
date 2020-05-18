name = 'pycromanager'  # TODO what is this here for?
__version__ = '0.0.1'

from .acquire import Acquisition, multi_d_acquisition_events
from ._core import Bridge, JavaObjectShadow
from .data import Dataset
