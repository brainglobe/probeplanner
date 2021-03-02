from loguru import logger
from vedo.shapes import Sphere
import numpy as np
from myterial import blue_grey_dark


class UI:
    """
        User interface (siders and buttons) for Planner
    """

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
