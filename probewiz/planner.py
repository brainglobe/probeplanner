import numpy as np
from loguru import logger

# from rich import print

import brainrender
from brainrender.render import mtx

from probewiz.probe import Probe

brainrender.settings.DEFAULT_CAMERA = {
    "pos": (121, -8158, -38268),
    "viewup": (0, -1, 0),
    "clippingRange": (19940, 55490),
    "focalPoint": (6588, 3683, -5280),
    "distance": 35640,
}
brainrender.settings.SHOW_AXES = False


class Planner(brainrender.Scene):
    def __init__(self):
        super(Planner, self).__init__()

        # get probe
        self.probe = Probe()
        self.probe.point_at(self.root)
        self.add(self.probe)

        # initialize sliders
        self._init_sliders()

    def _init_sliders(self):
        self._get_plotter()

        bounds = self.root.bounds()
        com = self.root.centerOfMass()

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
            value=com[0],
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
            value=com[2],
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
            value=com[1],
            title="DV",
            rotation=180,
            showValue=False,
        )

    def refresh(self):
        new_probe = self.probe.clone()
        new_probe.applyTransform(mtx)
        self.plotter.add(new_probe.mesh)
        self.plotter.remove(self.probe.mesh)
        self.probe = new_probe

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

    def add_probe(self, *probes):
        logger.debug(f"SCENE: adding {len(probes)} probes")

        for probe in probes:
            self.probes.append(probe)
            self.add(probe)

            # Add brain regions the probe touches
            points = probe.sample()
            for point in points:
                try:
                    region = self.atlas.structure_from_coords(
                        point, microns=True, as_acronym=True
                    )
                except KeyError:
                    continue

                self.add_brain_region(region, alpha=0.2)
