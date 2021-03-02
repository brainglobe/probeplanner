from loguru import logger
from vedo.shapes import Sphere
import numpy as np
from myterial import blue_grey_dark

from rich.panel import Panel
from rich.layout import Layout

from myterial import green, green_light, light_blue, salmon_light


class UI:
    def __init__(self):
        """
            User interface (siders and buttons) for Planner
        """
        # initialize classes for live display
        self.target_display = Target()
        self.tree_display = Tree()
        self.probe_display = ProbeLive()

    def _init_buttons(self):
        """
            Add buttons to 3D visualization
        """
        # reset probe
        self.plotter.addButton(
            self.reset,
            pos=(0.1, 0.95),  # x,y fraction from bottom left corner
            states=["Reset"],
            c=["w"],
            bc=[blue_grey_dark],  # colors of states
            font="courier",  # arial, courier, times
            size=50,
            bold=True,
            italic=False,
        )

        # save probe button
        self.plotter.addButton(
            self.save_probe,
            pos=(0.15, 0.85),  # x,y fraction from bottom left corner
            states=["Save probe"],
            c=["w"],
            bc=[blue_grey_dark],  # colors of states
            font="courier",  # arial, courier, times
            size=50,
            bold=True,
            italic=False,
        )

    def _init_sliders(self):
        """
            Add sliders to 3D visualization
        """
        bounds = self.root_mesh.bounds()

        # 3D sliders for XYZ positioning
        p0 = (bounds[0], 0, 0)
        p1 = [bounds[1], 0, 0]
        p2 = (bounds[0], 0, -bounds[5])
        p3 = (bounds[0], bounds[3], 0)

        move_AP_slider = self.plotter.addSlider3D(
            self.move_AP,
            p0,
            p1,
            bounds[0],
            bounds[1],
            value=self.probe.tip[0],
            title="AP",
            rotation=180,
            showValue=False,
        )
        move_ML_slider = self.plotter.addSlider3D(
            self.move_ML,
            p0,
            p2,
            bounds[4],
            bounds[5],
            value=self.probe.tip[2],
            title="ML",
            rotation=180,
            showValue=False,
        )
        move_DV_slider = self.plotter.addSlider3D(
            self.move_DV,
            p0,
            p3,
            bounds[2],
            bounds[3],
            value=self.probe.tip[1],
            title="DV",
            rotation=180,
            showValue=False,
        )
        self.add(Sphere(pos=p0, r=350, c="k"))

        # 2D sliders for tilting
        tilt_AP_slider = self.plotter.addSlider2D(
            self.tilt_AP, -60, 60, value=self.probe.tilt_AP, title="AP angle",
        )

        tilt_ML_slider = self.plotter.addSlider2D(
            self.tilt_ML,
            -60,
            60,
            value=self.probe.tilt_ML,
            title="ML angle",
            pos=3,
        )

        self.sliders = dict(
            move_AP=move_AP_slider,
            move_DV=move_DV_slider,
            move_ML=move_ML_slider,
            tilt_AP=tilt_AP_slider,
            tilt_ML=tilt_ML_slider,
        )

    def set_sliders_values(self):
        """
            Update the sliders' values based on the current
            probe parameters.
        """
        self.sliders["move_AP"].GetRepresentation().SetValue(self.probe.tip[0])
        self.sliders["move_DV"].GetRepresentation().SetValue(self.probe.tip[1])
        self.sliders["move_ML"].GetRepresentation().SetValue(self.probe.tip[2])
        self.sliders["tilt_AP"].GetRepresentation().SetValue(
            self.probe.tilt_AP
        )
        self.sliders["tilt_ML"].GetRepresentation().SetValue(
            self.probe.tilt_ML
        )

    def move_AP(self, widget, event):
        value = widget.GetRepresentation().GetValue()
        delta = np.abs(value - self.probe.tip[0])
        if delta > 50:
            logger.debug(f"Move AP: {value:.1f}")
            self.probe.tip[0] = value
            self.refresh()

    def move_ML(self, widget, event):
        value = widget.GetRepresentation().GetValue()
        delta = np.abs(value - self.probe.tip[2])
        if delta > 50:
            logger.debug(f"Move ML: {value:.1f}")
            self.probe.tip[2] = value
            self.refresh()

    def move_DV(self, widget, event):
        value = widget.GetRepresentation().GetValue()
        delta = np.abs(value - self.probe.tip[1])
        if delta > 50:
            logger.debug(f"Move DV: {value:.1f}")
            self.probe.tip[1] = value
            self.refresh()

    def tilt_AP(self, widget, event):
        value = widget.GetRepresentation().GetValue()
        delta = np.abs(value - self.probe.tilt_AP)
        if delta > 1:
            logger.debug(f"Tilt AP: {value:.1f}")
            self.probe.tilt_AP = value
            self.refresh()

    def tilt_ML(self, widget, event):
        value = widget.GetRepresentation().GetValue()
        delta = np.abs(value - self.probe.tilt_ML)
        if delta > 1:
            logger.debug(f"Tilt ML: {value:.1f}")
            self.probe.tilt_ML = value
            self.refresh()


class ProbeLive:
    """
        Show current probe parameters
    """

    probe = None

    def __rich_console__(self, console, measure):
        if self.probe is None:
            yield ""
        else:
            yield from list(self.probe.__rich_console__(console, measure))


class Tree:
    """
        Tree hierarchy of regions traversed by probe
    """

    targets = []

    def __rich_console__(self, console, measure):
        yield Panel(self.targets, style=light_blue, padding=(2, 2))


class Target:
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
