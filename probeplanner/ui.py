from loguru import logger
from vedo.shapes import Sphere
import numpy as np


class UI:
    def _init_sliders(self):
        bounds = self.root_mesh.bounds()

        # 3D sliders for XYZ positioning
        p0 = (bounds[0], 0, 0)
        p1 = [bounds[1], 0, 0]
        p2 = (bounds[0], 0, -bounds[5])
        p3 = (bounds[0], bounds[3], 0)

        self.plotter.addSlider3D(
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
        self.plotter.addSlider3D(
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
        self.plotter.addSlider3D(
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
        self.plotter.addSlider2D(
            self.tilt_AP, -60, 60, value=self.probe.psy, title="AP angle",
        )

        self.plotter.addSlider2D(
            self.tilt_ML,
            -60,
            60,
            value=self.probe.theta,
            title="ML angle",
            pos=3,
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
        delta = np.abs(value - self.probe.psy)
        if delta > 1:
            logger.debug(f"Tilt AP: {value:.1f}")
            self.probe.psy = value
            self.refresh()

    def tilt_ML(self, widget, event):
        value = widget.GetRepresentation().GetValue()
        delta = np.abs(value - self.probe.theta)
        if delta > 1:
            logger.debug(f"Tilt ML: {value:.1f}")
            self.probe.theta = value
            self.refresh()
