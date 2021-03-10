import typer
import sys
import brainrender

sys.path.append("./")
from probeplanner import Planner, Viewer

app = typer.Typer()


@app.command()
def plan(
    plan_file: str = typer.Option(
        None, "-plan", "--p", help="Path to plan YAML"
    ),
    probe_file: str = typer.Option(
        None, "-probe", "--pp", help="Path to probe YAML"
    ),
    debug: bool = typer.Option(False, "-debug", "--debug", help="Debug?"),
):

    if debug:
        brainrender.set_logging("DEBUG")

    planner = Planner(plan_file, probe_file)

    planner.plan()


@app.command()
def view(
    plan_file: str = typer.Option(
        None, "-plan", "--p", help="Path to plan YAML"
    ),
    probe_file: str = typer.Option(
        None, "-probe", "--pp", help="Path to probe YAML"
    ),
    debug: bool = typer.Option(False, "-debug", "--debug", help="Debug?"),
):
    if debug:
        brainrender.set_logging("DEBUG")

    Viewer(plan_file, probe_file)


if __name__ == "__main__":
    app()
