import numpy as np
from numpy import radians as rad
from numpy import cos, sin
from dataclasses import dataclass

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
        """rotation matrix composed of rotations with AP and ML axes"""
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

    @property
    def skull_point(self):
        """
        Returns the probe point with smaller AP distance from bregma
        """
        depths = np.array([p.DV for p in self.points])

        at_skull = np.argmin(np.abs(depths - BREGMA[1]))

        return self.points[at_skull]

    @property
    def tip_point(self):
        """
        The point closest to the tip
        """
        return Point(*self.tip, ROI=-1)

    @property
    def length_in_skull(self):
        """
        The length/ammount of probe shank inside the skull
        (betwee the tip and skull points)
        """
        return np.linalg.norm(self.tip - self.skull_point.coordinates)
