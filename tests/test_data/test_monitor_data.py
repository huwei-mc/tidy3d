"""Tests tidy3d/components/data/monitor_data.py"""
import numpy as np
import pytest

import tidy3d as td

from tidy3d.components.monitor import FieldMonitor, FieldTimeMonitor, PermittivityMonitor
from tidy3d.components.monitor import ModeSolverMonitor, ModeMonitor
from tidy3d.components.monitor import FluxMonitor, FluxTimeMonitor
from tidy3d.components.mode import ModeSpec
from tidy3d.log import DataError, SetupError

from tidy3d.components.data.dataset import FieldDataset
from tidy3d.components.data.monitor_data import FieldData, FieldTimeData, PermittivityData

from tidy3d.components.data.monitor_data import ModeSolverData, ModeData
from tidy3d.components.data.monitor_data import FluxData, FluxTimeData, DiffractionData

from .test_data_arrays import make_scalar_field_data_array, make_scalar_field_time_data_array
from .test_data_arrays import make_scalar_mode_field_data_array
from .test_data_arrays import make_flux_data_array, make_flux_time_data_array
from .test_data_arrays import make_mode_amps_data_array, make_mode_index_data_array
from .test_data_arrays import make_diffraction_data_array
from .test_data_arrays import FIELD_MONITOR, FIELD_TIME_MONITOR, MODE_SOLVE_MONITOR
from .test_data_arrays import MODE_MONITOR, PERMITTIVITY_MONITOR, FLUX_MONITOR, FLUX_TIME_MONITOR
from .test_data_arrays import FIELD_MONITOR_2D, FIELD_TIME_MONITOR_2D
from .test_data_arrays import DIFFRACTION_MONITOR, SIM_SYM, SIM
from ..utils import clear_tmp, assert_log_level

# data array instances
AMPS = make_mode_amps_data_array()
N_COMPLEX = make_mode_index_data_array()
FLUX = make_flux_data_array()
FLUX_TIME = make_flux_time_data_array()

""" Make the montor data """


def make_field_data(symmetry: bool = True):
    sim = SIM_SYM if symmetry else SIM
    return FieldData(
        monitor=FIELD_MONITOR,
        Ex=make_scalar_field_data_array("Ex", symmetry),
        Ey=make_scalar_field_data_array("Ey", symmetry),
        Ez=make_scalar_field_data_array("Ez", symmetry),
        Hx=make_scalar_field_data_array("Hx", symmetry),
        Hz=make_scalar_field_data_array("Hz", symmetry),
        symmetry=sim.symmetry,
        symmetry_center=sim.center,
        grid_expanded=sim.discretize(FIELD_MONITOR, extend=True),
    )


def make_field_time_data(symmetry: bool = True):
    sim = SIM_SYM if symmetry else SIM
    return FieldTimeData(
        monitor=FIELD_TIME_MONITOR,
        Ex=make_scalar_field_time_data_array("Ex", symmetry),
        Ey=make_scalar_field_time_data_array("Ey", symmetry),
        Ez=make_scalar_field_time_data_array("Ez", symmetry),
        Hz=make_scalar_field_time_data_array("Hz", symmetry),
        Hx=make_scalar_field_time_data_array("Hx", symmetry),
        symmetry=sim.symmetry,
        symmetry_center=sim.center,
        grid_expanded=sim.discretize(FIELD_TIME_MONITOR, extend=True),
    )


def make_field_data_2d(symmetry: bool = True):
    sim = SIM_SYM if symmetry else SIM
    return FieldData(
        monitor=FIELD_MONITOR_2D,
        Ex=make_scalar_field_data_array("Ex", symmetry).interp(y=[0]),
        Ey=make_scalar_field_data_array("Ey", symmetry).interp(y=[0]),
        Ez=make_scalar_field_data_array("Ez", symmetry).interp(y=[0]),
        Hx=make_scalar_field_data_array("Hx", symmetry).interp(y=[0]),
        Hz=make_scalar_field_data_array("Hz", symmetry).interp(y=[0]),
        symmetry=sim.symmetry,
        symmetry_center=sim.center,
        grid_expanded=sim.discretize(FIELD_MONITOR_2D, extend=True),
    )


def make_field_time_data_2d(symmetry: bool = True):
    sim = SIM_SYM if symmetry else SIM
    return FieldTimeData(
        monitor=FIELD_TIME_MONITOR_2D,
        Ex=make_scalar_field_time_data_array("Ex", symmetry).interp(y=[0]),
        Ey=make_scalar_field_time_data_array("Ey", symmetry).interp(y=[0]),
        Ez=make_scalar_field_time_data_array("Ez", symmetry).interp(y=[0]),
        Hx=make_scalar_field_time_data_array("Hx", symmetry).interp(y=[0]),
        Hz=make_scalar_field_time_data_array("Hz", symmetry).interp(y=[0]),
        symmetry=sim.symmetry,
        symmetry_center=sim.center,
        grid_expanded=sim.discretize(FIELD_TIME_MONITOR_2D, extend=True),
    )


def make_mode_solver_data():
    return ModeSolverData(
        monitor=MODE_SOLVE_MONITOR,
        Ex=make_scalar_mode_field_data_array("Ex"),
        Ey=make_scalar_mode_field_data_array("Ey"),
        Ez=make_scalar_mode_field_data_array("Ez"),
        Hx=make_scalar_mode_field_data_array("Hx"),
        Hy=make_scalar_mode_field_data_array("Hy"),
        Hz=make_scalar_mode_field_data_array("Hz"),
        symmetry=SIM_SYM.symmetry,
        symmetry_center=SIM_SYM.center,
        grid_expanded=SIM_SYM.discretize(MODE_SOLVE_MONITOR, extend=True),
        n_complex=N_COMPLEX.copy(),
    )


def make_permittivity_data(symmetry: bool = True):
    sim = SIM_SYM if symmetry else SIM
    return PermittivityData(
        monitor=PERMITTIVITY_MONITOR,
        eps_xx=make_scalar_field_data_array("Ex", symmetry),
        eps_yy=make_scalar_field_data_array("Ey", symmetry),
        eps_zz=make_scalar_field_data_array("Ez", symmetry),
        symmetry=sim.symmetry,
        symmetry_center=sim.center,
        grid_expanded=sim.discretize(PERMITTIVITY_MONITOR, extend=True),
    )


def make_mode_data():
    return ModeData(monitor=MODE_MONITOR, amps=AMPS.copy(), n_complex=N_COMPLEX.copy())


def make_flux_data():
    return FluxData(monitor=FLUX_MONITOR, flux=FLUX.copy())


def make_flux_time_data():
    return FluxTimeData(monitor=FLUX_TIME_MONITOR, flux=FLUX_TIME.copy())


def make_diffraction_data():
    sim_size, bloch_vecs, data = make_diffraction_data_array()
    return DiffractionData(
        monitor=DIFFRACTION_MONITOR,
        Etheta=data,
        Ephi=data,
        Er=data,
        Htheta=data,
        Hphi=data,
        Hr=data,
        sim_size=sim_size,
        bloch_vecs=bloch_vecs,
    )


""" Test them out """


def test_field_data():
    data = make_field_data()
    # Check that calling flux and dot on 3D data raise errors
    with pytest.raises(DataError):
        dot = data.dot(data)
    data_2d = make_field_data_2d()
    for field in FIELD_MONITOR.fields:
        _ = getattr(data_2d, field)
    # Compute flux directly
    flux1 = np.abs(data_2d.flux)
    # Compute flux as dot product with itself
    flux2 = np.abs(data_2d.dot(data_2d))
    # Assert result is the same
    assert np.all(flux1 == flux2)


def test_field_data_to_source():
    data = make_field_data_2d(symmetry=True)
    data = data.copy(update={key: val.isel(f=[-1]) for key, val in data.field_components.items()})
    source = data.to_source(source_time=td.GaussianPulse(freq0=2e14, fwidth=2e13), center=(1, 2, 3))
    data = make_field_data_2d(symmetry=False)
    data = data.copy(update={key: val.isel(f=[-1]) for key, val in data.field_components.items()})
    source = data.to_source(source_time=td.GaussianPulse(freq0=2e14, fwidth=2e13), center=(1, 2, 3))


def test_field_time_data():
    data = make_field_time_data_2d()
    for field in FIELD_TIME_MONITOR.fields:
        _ = getattr(data, field)
    # Check that flux can be computed
    flux1 = np.abs(data.flux)
    # Check that trying to call the dot product raises an error for time data
    with pytest.raises(DataError):
        dot = data.dot(data)


def test_mode_solver_data():
    data = make_mode_solver_data()
    for field in "EH":
        for component in "xyz":
            _ = getattr(data, field + component)
    # Compute flux directly
    flux1 = np.abs(data.flux)
    # Compute flux as dot product with itself
    flux2 = np.abs(data.dot(data))
    # Assert result is the same
    assert np.all(flux1 == flux2)
    # Compute dot product with a field data
    field_data = make_field_data_2d()
    dot = data.dot(field_data)
    # Check that broadcasting worked
    assert data.Ex.f == dot.f
    assert data.Ex.mode_index == dot.mode_index
    # Also try with a feild data at a single frequency that is not in the data frequencies
    freq = 0.9 * field_data.Ex.f[0]
    fields = field_data.field_components.items()
    fields_single_f = {key: val.isel(f=[0]).assign_coords(f=[freq]) for key, val in fields}
    field_data = field_data.copy(update=fields_single_f)
    dot = data.dot(field_data)
    # Check that broadcasting worked
    assert data.Ex.f == dot.f
    assert data.Ex.mode_index == dot.mode_index


def test_permittivity_data():
    data = make_permittivity_data()
    for comp in "xyz":
        _ = getattr(data, "eps_" + comp + comp)


def test_mode_data():
    data = make_mode_data()
    _ = data.amps
    _ = data.n_complex
    _ = data.n_eff
    _ = data.k_eff


def test_flux_data():
    data = make_flux_data()
    _ = data.flux


def test_flux_time_data():
    data = make_flux_time_data()
    _ = data.flux


def test_diffraction_data():
    data = make_diffraction_data()
    _ = data.Etheta
    _ = data.Ephi
    _ = data.Er
    _ = data.Htheta
    _ = data.Hphi
    _ = data.Hr
    _ = data.orders_x
    _ = data.orders_y
    _ = data.f
    _ = data.ux
    _ = data.uy
    _ = data.angles
    _ = data.sim_size
    _ = data.bloch_vecs
    _ = data.amps
    _ = data.power
    _ = data.fields_spherical
    _ = data.fields_cartesian


def test_colocate():
    # TODO: can we colocate into regions where we dont store fields due to symmetry?
    # regular colocate
    data = make_field_data()
    _ = data.colocate(x=[+0.1, 0.5], y=[+0.1, 0.5], z=[+0.1, 0.5])

    # ignore coordinate
    _ = data.colocate(x=[+0.1, 0.5], y=None, z=[+0.1, 0.5])

    # data outside range of len(coord)==1 dimension
    data = make_mode_solver_data()
    with pytest.raises(DataError):
        _ = data.colocate(x=[+0.1, 0.5], y=1.0, z=[+0.1, 0.5])

    with pytest.raises(DataError):
        _ = data.colocate(x=[+0.1, 0.5], y=[1.0, 2.0], z=[+0.1, 0.5])


def test_sel_mode_index():

    data = make_mode_solver_data()
    field_data = data.sel_mode_index(mode_index=0)
    for _, scalar_field in field_data.field_components.items():
        assert "mode_index" in scalar_field.coords, "mode_index coordinate removed from data."


def _test_eq():
    data1 = make_flux_data()
    data2 = make_flux_data()
    data1.flux.data = np.ones_like(data1.flux.data)
    data2.flux.data = np.ones_like(data2.flux.data)
    data3 = make_flux_time_data_array()
    assert data1 == data2, "same data are not equal"
    data1.flux.data[0] = 1e12
    assert data1 != data2, "different data are equal"
    assert data1 != data3, "different data are equal"


def test_empty_array():
    coords = {"x": np.arange(10), "y": np.arange(10), "z": np.arange(10), "t": []}
    fields = {"Ex": td.ScalarFieldTimeDataArray(np.random.rand(10, 10, 10, 0), coords=coords)}
    monitor = td.FieldTimeMonitor(size=(1, 1, 1), fields=["Ex"], name="test")
    field_data = td.FieldTimeData(
        monitor=monitor,
        symmetry=SIM.symmetry,
        symmetry_center=SIM.center,
        grid_expanded=SIM.discretize(monitor, extend=True),
        **fields
    )


# NOTE: can remove this? lets not support empty tuple or list, use np.zeros()
def _test_empty_list():
    coords = {"x": np.arange(10), "y": np.arange(10), "z": np.arange(10), "t": []}
    fields = {"Ex": td.ScalarFieldTimeDataArray([], coords=coords)}
    monitor = td.FieldTimeMonitor(size=(1, 1, 1), fields=["Ex"], name="test")
    field_data = td.FieldTimeData(
        monitor=monitor,
        symmetry=SIM.symmetry,
        symmetry_center=SIM.center,
        grid_expanded=SIM.discretize(monitor, extend=True),
        **fields
    )


# NOTE: can remove this? lets not support empty tuple or list, use np.zeros()
def _test_empty_tuple():
    coords = {"x": np.arange(10), "y": np.arange(10), "z": np.arange(10), "t": []}
    fields = {"Ex": td.ScalarFieldTimeDataArray((), coords=coords)}
    monitor = td.FieldTimeMonitor(size=(1, 1, 1), fields=["Ex"], name="test")
    field_data = td.FieldTimeData(
        monitor=monitor,
        symmetry=SIM.symmetry,
        symmetry_center=SIM.center,
        grid_expanded=SIM.discretize(monitor, extend=True),
        **fields
    )


@clear_tmp
def test_empty_io():
    coords = {"x": np.arange(10), "y": np.arange(10), "z": np.arange(10), "t": []}
    fields = {"Ex": td.ScalarFieldTimeDataArray(np.random.rand(10, 10, 10, 0), coords=coords)}
    monitor = td.FieldTimeMonitor(size=(1, 1, 1), name="test", fields=["Ex"])
    field_data = td.FieldTimeData(
        monitor=monitor,
        symmetry=SIM.symmetry,
        symmetry_center=SIM.center,
        grid_expanded=SIM.discretize(monitor, extend=True),
        **fields
    )
    field_data.to_file("tests/tmp/field_data.hdf5")
    field_data = td.FieldTimeData.from_file("tests/tmp/field_data.hdf5")
    assert field_data.Ex.size == 0


def test_mode_solver_plot_field():
    """Ensure we get a helpful error if trying to .plot_field with a ModeSolverData."""
    ms_data = make_mode_solver_data()
    with pytest.raises(DeprecationWarning):
        ms_data.plot_field(1, 2, 3, z=5, b=True)


def test_field_data_symmetry_present():

    coords = {"x": np.arange(10), "y": np.arange(10), "z": np.arange(10), "t": []}
    fields = {"Ex": td.ScalarFieldTimeDataArray(np.random.rand(10, 10, 10, 0), coords=coords)}
    monitor = td.FieldTimeMonitor(size=(1, 1, 1), name="test", fields=["Ex"])

    # works if no symmetry specified
    field_data = td.FieldTimeData(monitor=monitor, **fields)

    # fails if symmetry specified but missing symmetry center
    with pytest.raises(SetupError):
        field_data = td.FieldTimeData(
            monitor=monitor,
            symmetry=(1, -1, 0),
            grid_expanded=SIM.discretize(monitor, extend=True),
            **fields
        )

    # fails if symmetry specified but missing etended grid
    with pytest.raises(SetupError):
        field_data = td.FieldTimeData(
            monitor=monitor, symmetry=(1, -1, 1), symmetry_center=(0, 0, 0), **fields
        )


def test_data_array_attrs():
    """Note, this is here because the attrs only get set when added to a pydantic model."""
    data = make_flux_data()
    assert data.flux.attrs, "data has no attrs"
    assert data.flux.f.attrs, "data coordinates have no attrs"


def test_data_array_json_warns(caplog):
    data = make_flux_data()
    data.to_file("tests/tmp/flux.json")
    assert_log_level(caplog, 30)


def test_data_array_hdf5_no_warnings(caplog):
    data = make_flux_data()
    data.to_file("tests/tmp/flux.hdf5")
    assert_log_level(caplog, None)


def test_diffraction_data_use_medium():
    data = make_diffraction_data()
    data = data.copy(update=dict(medium=td.Medium(permittivity=4)))
    assert np.allclose(data.eta, np.real(td.ETA_0 / 2.0))
