""" global configuration / base class for pydantic models used to make simulation """

import json
import yaml

import pydantic

from .viz import add_ax_if_none, make_aspect_equal
from .types import AxesSubplot

# default indentation (# spaces) in files
INDENT = 4


class Tidy3dBaseModel(pydantic.BaseModel):
    """https://pydantic-docs.helpmanual.io/usage/model_config/"""

    class Config:  # pylint: disable=too-few-public-methods
        """sets config for all Tidy3dBaseModel objects"""

        validate_all = True  # validate default values too
        extra = "forbid"  # forbid extra kwargs not specified in model
        validate_assignment = True  # validate when attributes are set after initialization
        allow_population_by_field_name = True

    def __init_subclass__(cls, **kwargs):
        """add `add_ax_if_none` decorator to all subclass .plot methods"""
        cls.plot = add_ax_if_none(cls.plot)
        cls.plot = make_aspect_equal(cls.plot)

    def _json_string(self) -> str:
        """returns string representation of self"""
        return self.json(
            indent=INDENT
        )  # , exclude_unset=True) # if I exclude unset, it throws away info

    def plot(self, *args, **kwargs) -> AxesSubplot:
        """generic plotting function for tidy3d components, if ax=None, creates one"""
        raise NotImplementedError(".plot() is not implemented for this object")

    def export(self, fname: str) -> None:
        """Exports Tidy3dBaseModel instance to .json file"""
        json_string = self._json_string()
        with open(fname, "w", encoding="utf-8") as file_handle:
            file_handle.write(json_string)

    def export_yaml(self, fname: str) -> None:
        """Exports Tidy3dBaseModel instance to .yaml file"""
        json_string = self._json_string()
        json_dict = json.loads(json_string)
        with open(fname, "w+", encoding="utf-8") as file_handle:
            yaml.dump(json_dict, file_handle, indent=INDENT)

    @classmethod
    def load(cls, fname: str):
        """load Simulation from .json file"""
        return cls.parse_file(fname)

    @classmethod
    def load_yaml(cls, fname: str):
        """load Simulation from .yaml file"""
        with open(fname, "r", encoding="utf-8") as yaml_in:
            json_dict = yaml.safe_load(yaml_in)
        json_raw = json.dumps(json_dict, indent=INDENT)
        return cls.parse_raw(json_raw)
