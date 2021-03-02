from rich.panel import Panel
from rich.layout import Layout
from rich.table import Table

from myterial import (
    green,
    green_light,
    light_blue,
    salmon_light,
    blue_light,
    pink_light,
    salmon,
)

from probeplanner.probe import BREGMA


class TerminalUI:
    def __init__(self, probe, target, tree):
        """
            UI for terminal info panels showing probe parameters, regions
            touched by probe etc. Built as a Live dispay of Layout's showing 
            rich renderables (classes above).
        """
        self.layout = Layout()
        self.layout.split(
            Layout(name="left", ratio=2),
            Layout(tree, name="right", ratio=4),
            direction="horizontal",
        )

        self.layout["left"].split(
            Layout(target, name="ltop"),
            Layout(
                Panel(
                    probe,
                    title="Probe",
                    border_style=salmon_light,
                    title_align="left",
                ),
                name="lbottom",
                ratio=3,
            ),
        )

    def __rich_console__(self, console, measure):
        yield self.layout


class ProbeParameters:
    """
        Show current probe parameters
    """

    probe = None

    def __rich_console__(self, console, measure):
        if self.probe is None:
            yield ""
        else:
            tb = Table(box=None)
            tb.add_row(f"[bold {salmon}]Position in CFF coordinates")
            tb.add_row(
                f"[bold {pink_light}]AP:  [{blue_light}] {str(round(self.probe.tip[0], 0))} [grey]micrometers",
            )
            tb.add_row(
                f"[bold {pink_light}]ML:  [{blue_light}] {str(round(self.probe.tip[2], 0))} [grey]micrometers",
            )
            tb.add_row(
                f"[bold {pink_light}]DV:  [{blue_light}] {str(round(self.probe.tip[1], 0))} [grey]micrometers",
            )

            tb.add_row("")
            tb.add_row(f"[bold {salmon}]Angles")
            tb.add_row(
                f"[bold {pink_light}]ML angle:  [{blue_light}] {str(round(self.probe.tilt_ML, 0))} [grey]degrees",
            )
            tb.add_row(
                f"[bold {pink_light}]AP angle:  [{blue_light}] {str(round(self.probe.tilt_AP, 0))} [grey]degrees",
            )

            tb.add_row("")
            tb.add_row(f"[bold {salmon}]Position relative to bregma")
            tb.add_row(
                f"[bold {pink_light}]AP:  [{blue_light}] {str(-round((BREGMA[0] - self.probe.tip[0])/1000, 3))} [grey]mm",
            )
            tb.add_row(
                f"[bold {pink_light}]ML:  [{blue_light}] {str(-round((BREGMA[2] - self.probe.tip[2])/1000, 3))} [grey]mm",
            )
            tb.add_row(
                f"[bold {pink_light}]DV:  [{blue_light}] {str(-round((BREGMA[1] - self.probe.tip[1])/1000, 3))} [grey]mm",
            )
            yield tb


class StructuresTree:
    """
        Tree hierarchy of regions traversed by probe
    """

    targets = []

    def __rich_console__(self, console, measure):
        yield Panel(self.targets, style=light_blue, padding=(0, 1))


class ProbeTarget:
    """
        Shows the current probe target
    """

    target = ""

    def __rich_console__(self, console, measure):
        yield Panel(
            f'[bold {green}]Probe tip is in: "{self.target}"',
            title="Current target",
            title_align="left",
            border_style=green_light,
        )
