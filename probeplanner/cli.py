import typer
from typing import List, Optional
import sys
import brainrender

sys.path.append("./")
from probeplanner import Planner, Viewer

app = typer.Typer()


@app.command()
def plan(
    aim_at: str = typer.Option(
        None, "-aim-at", "--at", help="Name of brain region to aim at"
    ),
    hemisphere: str = typer.Option(
        None, "-hemisphere", "--h", help="target hemisphere"
    ),
    AP_angle: int = typer.Option(
        0, "-AP-angle", "--AP", help="angle on AP plane"
    ),
    ML_angle: int = typer.Option(
        0, "-ML-angle", "--ML", help="angle on ML plane"
    ),
    highlight: Optional[List[str]] = typer.Option(
        "",
        "-highlight",
        "--hl",
        help="names of brain regions to highlight (separated by space)",
    ),
    probe_file: str = typer.Option(
        None, "-probe", "--p", help=".yaml file with probe data"
    ),
    debug: bool = typer.Option(False, "-debug", "--debug", help="Debug?"),
):

    if debug:
        brainrender.set_logging("DEBUG")

    if highlight:
        highlight = highlight[0].split(" ")

    planner = Planner(
        aim_at=aim_at,
        hemisphere=hemisphere,
        AP_angle=float(AP_angle),
        ML_angle=float(ML_angle),
        highlight=highlight,
        probe_file=probe_file,
    )

    planner.plan()


@app.command()
def view(
    probe_file: str = typer.Argument(None),
    highlight: Optional[List[str]] = typer.Option(
        "",
        "-highlight",
        "--hl",
        help="names of brain regions to highlight (separated by space)",
    ),
    debug: bool = typer.Option(False, "-debug", "--debug", help="Debug?"),
):
    if debug:
        brainrender.set_logging("DEBUG")

    if highlight:
        highlight = highlight[0].split(" ")

    Viewer(probe_file, highlight=highlight)


if __name__ == "__main__":
    app()
