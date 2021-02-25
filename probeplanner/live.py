from rich.panel import Panel
from rich.layout import Layout

from myterial import green, green_light, light_blue


class Tree:
    targets = []

    def __rich_console__(self, console, measure):
        yield Panel(self.targets, style=light_blue, padding=(2, 2))


class Target:
    target = ""

    def __rich_console__(self, console, measure):
        yield Panel(
            f'[bold {green}]Probe tip is in: "{self.target}"',
            title="Current target",
            title_align="left",
            border_style=green_light,
        )


class Live:
    def __init__(self, probe, target, tree):
        self.layout = Layout()
        self.layout.split(
            Layout(name="left"),
            Layout(tree, name="right", ratio=2),
            direction="horizontal",
        )

        self.layout["left"].split(
            Layout(target, name="ltop"), Layout(probe, name="lbottom", ratio=3)
        )

    def __rich_console__(self, console, measure):
        yield self.layout
