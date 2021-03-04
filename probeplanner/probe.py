import numpy as np
from numpy import radians as rad
from numpy import cos, sin
from vedo.shapes import Cylinder, Sphere
from vedo import merge
from dataclasses import dataclass
from loguru import logger
import yaml

from brainrender.actor import Actor

"""
    This bregma coordinates in the Allen CCF are from Shamash et al 2018
    and are only approximated. Good enough for visualization.
"""
BREGMA = [
    5400,  # AP
    0,  # DV
    5700,  # ML
]


@dataclass
class Point:
    AP: float = 0.0  # position on AP axis
    DV: float = 0.0  # position on DV axis
    ML: float = 0.0  # position on ML axis
    ROI: int = 0

    @property
    def coordinates(self):
        return np.array([self.AP, self.DV, self.ML])


@dataclass
class ProbeGeometry:
    """
        Class handling basic geometry operation on 
        the probe.
    """

    tip: np.ndarray = np.zeros(3)  # coordinates of the tip

    tilt_ML: float = 0.0  # ML angle
    tilt_AP: float = 0.0  # AP angle
    length: int = 10000  # length in microns
    radius: int = 70  # radius in microns
    color: str = "k"  # color in rendering

    @property
    def R_AP(self):
        """
            Rotation matrix to describe rotation with AP
            as axis.
        """
        tilt_AP = rad(self.tilt_AP)
        return np.array(
            [
                [cos(tilt_AP), -sin(tilt_AP), 0],
                [sin(tilt_AP), cos(tilt_AP), 0],
                [0, 0, 1],
            ]
        )

    @property
    def R_ML(self):
        """
            Rotation matrix to describe rotation with ML
            as axis.
        """
        tilt_ML = rad(self.tilt_ML)
        return np.array(
            [
                [1, 0, 0],
                [0, cos(tilt_ML), -sin(tilt_ML)],
                [0, sin(tilt_ML), cos(tilt_ML)],
            ]
        )

    @property
    def R(self):
        """ rotation matrix composed of rotations with AP and ML axes """
        return self.R_AP @ self.R_ML

    @property
    def top(self):
        """
            The position of the top of the probe, computed given the probe's 
            tip location, length and rotation matrix.
        """
        top = np.array([0, -self.length, 0])
        top = self.tip + self.R @ top
        return top

    @property
    def points(self):
        """
            Creates a list of points (AP-DV-ML coordinates) along the probe in the 
            regions of intersted (ROIs)

            Returns:
                points: list of Point
        """
        # generated points
        points = []
        for n, roi in enumerate(self.ROIs):
            start = roi[0] / self.length  # ROI start/end in fraction of probe
            end = roi[1] / self.length
            N = int((roi[1] - roi[0]) / 100)  #  a point every 100 microns

            steps = np.linspace(start, end, N)
            for u in steps:
                AP = (1 - u) * self.tip[0] + u * self.top[0]
                DV = (1 - u) * self.tip[1] + u * self.top[1]
                ML = (1 - u) * self.tip[2] + u * self.top[2]
                points.append(Point(AP, DV, ML, n))

        return points


class Probe(ProbeGeometry, Actor):
    def __init__(self, *args, _top=None, ROIs=None, **kwargs):
        """
            Represents a probe as a brainrender actor
        """

        ProbeGeometry.__init__(self, *args, **kwargs)
        Actor.__init__(self, self.get_mesh(), name="Probe", br_class="Probe")

        self.ROIs = ROIs or [
            (0, self.length),
        ]

        logger.debug(
            f"Creating probe, angles: tip:{[int(x) for x in self.tip]} tilt_AP-{self.tilt_AP:.2f}  tilt_ML-{self.tilt_ML:.2f}"
        )

        # Initialze top position
        if _top is None:
            self._top = self.tip.copy()
            self._top[1] -= self.length
        else:
            self._top = _top
            self.update()

    def get_mesh(self):
        """
            Returns the current mesh representation of the probe
        """
        shaft = Cylinder(
            pos=[self.top, self.tip], c="k", r=self.radius, alpha=1
        )
        tip = Sphere(pos=self.tip, r=self.radius + 20, c="k")
        mesh = merge(shaft, tip).c(self.color)
        return mesh

    def update(self):
        """
            Update probe's mesh
        """
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

    def clone(self):
        """
            Returns a new probe with the same parameters as the current one
        """
        return Probe(
            tip=self.tip.copy(),
            tilt_ML=float(self.tilt_ML),
            tilt_AP=float(self.tilt_AP),
            color=self.color,
            length=self.length,
            radius=self.radius,
            _top=self._top,
        )

    def save(self, savepath):
        """
            Save probe params to file
        """
        params = dict(
            tip=[float(x) for x in self.tip],
            tilt_AP=self.tilt_AP,
            tilt_ML=self.tilt_ML,
            length=self.length,
            radius=self.radius,
        )

        with open(savepath, "w") as out:
            yaml.dump(params, out, default_flow_style=False, indent=4)

    @classmethod
    def load(cls, savepath):
        """
            Loads a probe's parameter from YAML file
            and creates a Probe object
        """
        with open(savepath, "r") as fin:
            params = yaml.load(fin, Loader=yaml.FullLoader)

        return cls(
            tip=np.array(params["tip"]),
            tilt_ML=float(params["tilt_ML"]),
            tilt_AP=float(params["tilt_AP"]),
            length=params["length"],
            radius=params["radius"],
        )
