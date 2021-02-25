import numpy as np
from numpy import radians as rad
from numpy import cos, sin
from vedo.shapes import Cylinder, Sphere
from vedo import merge
from dataclasses import dataclass
from loguru import logger
from rich.table import Table

from myterial import blue_light, pink_light, salmon

from brainrender.actor import Actor


BREGMA = [
    5400,  # AP
    0,  # DV
    5700,  # ML
]


@dataclass
class ProbeGeometry:
    tip: np.ndarray = np.zeros(3)  # coordinates of the tip

    theta: float = 0.0  # ML angle
    psy: float = 0.0  # AP angle
    length: int = 10000  # length in microns
    radius: int = 70
    color: str = "k"

    @property
    def R_AP(self):
        """
            Rotation matrix to describe rotation with AP
            as axis.
        """
        psy = rad(self.psy)
        return np.array(
            [[cos(psy), -sin(psy), 0], [sin(psy), cos(psy), 0], [0, 0, 1]]
        )

    @property
    def R_ML(self):
        """
            Rotation matrix to describe rotation with ML
            as axis.
        """
        theta = rad(self.theta)
        return np.array(
            [
                [1, 0, 0],
                [0, cos(theta), -sin(theta)],
                [0, sin(theta), cos(theta)],
            ]
        )

    @property
    def R(self):
        """ rotation matrix """
        return self.R_AP @ self.R_ML

    @property
    def top(self):
        """
            The position of the top of the probe
        """
        top = np.array([0, -self.length, 0])
        top = self.tip + self.R @ top
        return top


class Probe(ProbeGeometry, Actor):
    watched = (
        "tip",
        "theta",
        "psy",
    )

    def __init__(self, *args, _top=None, **kwargs):
        ProbeGeometry.__init__(self, *args, **kwargs)
        Actor.__init__(self, self.get_mesh(), name="Probe", br_class="Probe")

        logger.debug(
            f"Creating probe, angles: tip:{[int(x) for x in self.tip]} psy-{self.psy:.2f}  theta-{self.theta:.2f}"
        )

        # Initialze top position
        if _top is None:
            self._top = self.tip.copy()
            self._top[1] -= self.length
        else:
            self._top = _top
            self.update()

    def __rich_console__(self, console, width):
        tb = Table(box=None)
        tb.add_row(f"[bold {salmon}]Position in CFF coordinates")
        tb.add_row(
            f"[bold {pink_light}]AP:  [{blue_light}] {str(round(self.tip[0], 0))} [grey]micrometers",
        )
        tb.add_row(
            f"[bold {pink_light}]ML:  [{blue_light}] {str(round(self.tip[2], 0))} [grey]micrometers",
        )
        tb.add_row(
            f"[bold {pink_light}]DV:  [{blue_light}] {str(round(self.tip[1], 0))} [grey]micrometers",
        )

        tb.add_row("")
        tb.add_row(f"[bold {salmon}]Angles")
        tb.add_row(
            f"[bold {pink_light}]ML angle:  [{blue_light}] {str(round(self.theta, 0))} [grey]degrees",
        )
        tb.add_row(
            f"[bold {pink_light}]AP angle:  [{blue_light}] {str(round(self.psy, 0))} [grey]degrees",
        )
        # print(str(self.theta))
        # print(str(self.psy))

        tb.add_row("")
        tb.add_row(f"[bold {salmon}]Position relative to bregma")
        tb.add_row(
            f"[bold {pink_light}]AP:  [{blue_light}] {str(-round((BREGMA[0] - self.tip[0])/1000, 3))} [grey]mm",
        )
        tb.add_row(
            f"[bold {pink_light}]ML:  [{blue_light}] {str(-round((BREGMA[2] - self.tip[2])/1000, 3))} [grey]mm",
        )
        tb.add_row(
            f"[bold {pink_light}]DV:  [{blue_light}] {str(-round((BREGMA[1] - self.tip[1])/1000, 3))} [grey]mm",
        )
        yield tb

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
        self.mesh = self.get_mesh()

    def point_at(self, target):
        if isinstance(target, (np.ndarray, list, tuple)):
            new_pos = np.array(target)
        else:
            new_pos = target.centerOfMass()

        delta = new_pos - self.tip
        self.tip += delta
        self.update()

    def sample(self, N=50):
        """
            Sample N points along the length of the probe
        """
        steps = np.linspace(0.001, 0.999, N)
        points = [
            np.array(
                [
                    (1 - u) * self.tip[0] + u * self.top[0],
                    (1 - u) * self.tip[1] + u * self.top[1],
                    (1 - u) * self.tip[2] + u * self.top[2],
                ]
            )
            for u in steps
        ]
        return points

    def clone(self):
        return Probe(
            tip=self.tip,
            theta=float(self.theta),
            psy=float(self.psy),
            color=self.color,
            length=self.length,
            radius=self.radius,
            _top=self._top,
        )
