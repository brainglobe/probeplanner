import typer
from typing import List, Optional
import sys
import brainrender

sys.path.append("./")
from probeplanner import Planner

app = typer.Typer()


@app.command()
def cli(
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
    )

    planner.plan()


if __name__ == "__main__":
    app()
