import os
import tempfile
from datetime import date

from .input import read_config
from .model import create_model


def compute_iis(config, result_dir, timesteps, year=None):
    """Rebuild the model from a run config and write a Gurobi IIS to disk.

    An IIS (Irreducible Inconsistent Subsystem) is the minimal set of
    constraints and variable bounds that together make the model infeasible.
    Inspecting it is the most direct way to find which inputs cause an
    infeasible simulation. The IIS is written as a human-readable
    ``model.ilp`` file inside ``result_dir``.

    Args:
        - config: the run config dict (same structure sent to /simulate)
        - result_dir: directory the .ilp file is written into
        - timesteps: range of modeled timesteps (same as the original run)
        - year: support timeframe year (defaults to the current year)

    Returns:
        the path to the written .ilp file

    Raises:
        RuntimeError: if Gurobi is unavailable or the model is not infeasible.
    """
    try:
        import gurobipy as gp
    except ImportError as exc:
        raise RuntimeError(
            "Computing an IIS requires the Gurobi solver, which is not available."
        ) from exc

    if year is None:
        year = date.today().year

    data = read_config(config, year)
    prob = create_model(data, 1, timesteps, 'cost')

    # symbolic_solver_labels keeps the original variable/constraint names
    # (e.g. res_area(2026_Burundi)) so the resulting .ilp is human readable.
    lp_fd, lp_path = tempfile.mkstemp(suffix='.lp')
    os.close(lp_fd)
    prob.write(lp_path, io_options={'symbolic_solver_labels': True})

    try:
        model = gp.read(lp_path)
        # DualReductions=0 lets Gurobi distinguish INFEASIBLE from UNBOUNDED.
        model.setParam('DualReductions', 0)
        model.optimize()

        if model.Status == gp.GRB.OPTIMAL:
            raise RuntimeError(
                "Model is feasible (an optimal solution exists); "
                "there is no IIS to compute."
            )
        if model.Status == gp.GRB.UNBOUNDED:
            raise RuntimeError(
                "Model is unbounded, not infeasible; an IIS cannot be computed."
            )
        if model.Status != gp.GRB.INFEASIBLE:
            raise RuntimeError(
                f"Model is not infeasible (Gurobi status {model.Status}); "
                "an IIS cannot be computed."
            )

        model.computeIIS()
        os.makedirs(result_dir, exist_ok=True)
        ilp_path = os.path.join(result_dir, 'model.ilp')
        model.write(ilp_path)
        return ilp_path
    finally:
        try:
            os.remove(lp_path)
        except OSError:
            pass
