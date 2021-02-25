import numpy as np
from numpy import radians as rad
from numpy import cos, sin
from vedo.shapes import Cylinder, Sphere
from vedo import merge
from dataclasses import dataclass
from loguru import logger
from rich.panel import Panel
from rich.table import Table

from brainrender.actor import Actor


@dataclass
class ProbeGeometry:
    tip: np.ndarray = np.zeros(3)  # coordinates of the tip
    theta: float = 0.0  # angle relative to vertical AP axis
    psy: float = 0.0  # horizontal angle
    length: int = 4000  # length in microns
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
        top = self.tip.copy()

        # anterio-posterior
        top[0] = self.tip[0] + self.length * np.sin(rad(self.theta)) * np.cos(
            rad(180 - self.psy)
        )

        # dorso-ventral
        top[1] = self.tip[1] - self.length * np.cos(rad(self.theta))

        # medio-latera
        top[2] = self.tip[2] + self.length * np.sin(rad(self.theta)) * np.sin(
            rad(180 - self.psy)
        )

        return top


class Probe(ProbeGeometry, Actor):
    watched = ("tip", "theta", "psy", "length")

    def __init__(self, *args, **kwargs):
        ProbeGeometry.__init__(self, *args, **kwargs)
        Actor.__init__(self, self.get_mesh(), name="Probe", br_class="Probe")

        logger.debug(
            f"Creating probe, angles: tip:{[int(x) for x in self.tip]} psy-{self.psy:.2f}  theta-{self.theta:.2f}"
        )

    def __setattr__(self, name, value):
        self.__dict__[name] = value

        # update mesh if we changed something
        if name in self.watched:
            self.mesh = self.get_mesh()

    def __rich_console__(self, console, width):
        tb = Table(show_header=False, box=None)
        tb.add_column(justify="right", style="bold yellow")
        tb.add_column(justify="left")

        tb.add_row("AP:", str(round(self.tip[0], 0)) + " micrometers")
        tb.add_row("ML:", str(round(self.tip[2], 0)) + " micrometers")
        tb.add_row("DV:", str(round(self.tip[1], 0)) + " micrometers")

        tb.add_row("θ:", str(round(self.theta, 2)) + " degrees")
        tb.add_row("ψ:", str(round(self.psy, 2)) + " degrees")

        yield Panel.fit(tb, title="Probe")

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
            self.tip = np.array(target)
        else:
            self.tip = target.centerOfMass()

    def sample(self, N=100):
        """
            Sample N points along the length of the probe
        """
        steps = np.linspace(0, 1, N)
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
            theta=self.theta,
            psy=self.psy,
            color=self.color,
            length=self.length,
            radius=self.radius,
        )
