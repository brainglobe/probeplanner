import yaml
from vedo.shapes import Cylinder, Sphere, Spheres
from vedo import merge
import numpy as np

from brainrender.actor import Actor

from probeplanner._probe import ProbeGeometry

"""
    This bregma coordinates in the Allen CCF are from Shamash et al 2018
    and are only approximated. Good enough for visualization.
"""
BREGMA = [
    5400,  # AP
    0,  # DV
    5700,  # ML
]


class Probe(ProbeGeometry, Actor):
    def __init__(self, *args, ROIs=None, **kwargs):
        self.ROIs = ROIs or [
            (0, self.length),
        ]

        ProbeGeometry.__init__(self, *args, **kwargs)
        Actor.__init__(self, self.get_mesh(), name="Probe", br_class="Probe")

    @classmethod
    def from_file(cls, probe_file):
        with open(probe_file, "r") as fin:
            params = yaml.load(fin, Loader=yaml.FullLoader)

        probe = cls(
            length=params["length"],
            radius=params["radius"],
            color=params["color"],
            ROIs=params["ROIs"],
        )
        return probe

    def clone(self):
        return Probe(
            tip=self.tip.copy(),
            tilt_ML=self.tilt_ML,
            tilt_AP=self.tilt_AP,
            length=self.length,
            radius=self.radius,
            color=self.color,
            ROIs=self.ROIs,
        )

    def get_mesh(self):
        """
            Returns the current mesh representation of the probe
        """
        shaft = Cylinder(
            pos=[self.top, self.tip], c="k", r=self.radius, alpha=1
        )
        tip = Sphere(pos=self.tip, r=self.radius + 20, c="k")
        rois = Spheres(
            [p.coordinates for p in self.points], r=self.radius + 30, c="r"
        )
        mesh = merge(shaft, tip, rois).c(self.color)
        return mesh

    def update(self):
        self.mesh = self.get_mesh()

    def point_at(self, target):
        """
            Point the probe at a target (either set of coordinates or an actor).
            The "pointing" referes to the positioning of the probe's tip at the point of interest, 
            it doesn't affect the probe's angles.
        """
        if isinstance(target, (np.ndarray, list, tuple)):
            new_pos = np.array(target)
        else:
            new_pos = target.centerOfMass()

        delta = new_pos - self.tip
        self.tip += delta
        self.update()
