""" Container holding all information about simulation and its components"""
from typing import Dict, Tuple, Union, List

import pydantic

from .types import GridSize, Literal
from .geometry import Box
from .medium import Medium, MediumType
from .structure import Structure
from .source import SourceType
from .monitor import MonitorType
from .pml import PMLLayer

# technically this is creating a circular import issue because it calls tidy3d/__init__.py
# from .. import __version__ as version_number


class Simulation(Box):
    """Contains all information about simulation"""

    grid_size: Union[pydantic.PositiveFloat, Tuple[GridSize, GridSize, GridSize]]
    medium: MediumType = Medium()
    run_time: pydantic.NonNegativeFloat = 0.0
    structures: List[Structure] = []
    sources: Dict[str, SourceType] = {}
    monitors: Dict[str, MonitorType] = {}
    pml_layers: Tuple[PMLLayer, PMLLayer, PMLLayer] = (
        PMLLayer(),
        PMLLayer(),
        PMLLayer(),
    )
    symmetry: Tuple[Literal[0, -1, 1], Literal[0, -1, 1], Literal[0, -1, 1]] = [0, 0, 0]
    shutoff: pydantic.NonNegativeFloat = 1e-5
    courant: pydantic.confloat(ge=0.0, le=1.0) = 0.9
    subpixel: bool = True
    # version: str = str(version_number)

    def __init__(self, **kwargs):
        """initialize sim and then do more validations"""
        super().__init__(**kwargs)

        self._check_geo_objs_in_bounds()
        # to do:
        # - check sources in medium frequency range
        # - check PW in homogeneous medium
        # - check nonuniform grid covers the whole simulation domain

    """ Post-Init validations """

    def _check_geo_objs_in_bounds(self):
        """for each geometry-containing object in simulation, make sure it intersects simulation"""

        for i, structure in enumerate(self.structures):
            assert self._intersects(
                structure.geometry
            ), f"Structure '{structure}' (at position {i}) is completely outside simulation"

        for geo_obj_dict in (self.sources, self.monitors):
            for name, geo_obj in geo_obj_dict.items():
                assert self._intersects(
                    geo_obj
                ), f"object '{name}' is completely outside simulation"

    def epsilon(self, box: Box):
        """get permittivity at volume specified by Box"""
