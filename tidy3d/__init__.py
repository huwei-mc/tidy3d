""" Tidy3d package imports"""
__version__ = "0.0.0"

import pkg_resources

# import component as `from tidy3d import Simulation`
from .components.simulation import Simulation
from .components.pml import PMLLayer
from .components.geometry import Box, Sphere, Cylinder, PolySlab
from .components.structure import Structure
from .components.medium import Medium, PoleResidue, Sellmeier, Debye, Lorentz
from .components.medium import nk_to_eps_complex, nk_to_eps_sigma
from .components.medium import nk_to_medium, eps_sigma_to_eps_complex

from .components.source import GaussianPulse
from .components.source import VolumeSource, PlaneWave, ModeSource
from .components.monitor import TimeSampler, FreqSampler, uniform_freq_sampler, uniform_time_sampler
from .components.monitor import FieldMonitor, FluxMonitor, ModeMonitor
from .components.mode import Mode
from .components.data import SimulationData, FieldData, FluxData, ModeData
from .components.data import monitor_data_map

from .constants import inf

# plugins imported as `from tidy3d.plugins.dispersion_fitter import *` for now
from . import plugins

# web API imported as `from tidy3d.web import *`
from . import web

# material library dict imported as `from tidy3d import material_library`
# specific material imported as `from tidy3d.material_library import SiC_xxx`
from .material_library import material_library

# try:
#     __version__ = pkg_resources.get_distribution("tidy3d").version
# except ImportError:  # pragma: nocover
#     # Local copy, not installed with setuptools
#     __version__ = "0.0.0"
