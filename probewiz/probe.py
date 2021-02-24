import numpy as np
from numpy import radians as rad
from vedo.shapes import Cylinder, Sphere
from vedo import merge
from dataclasses import dataclass

from brainrender.actor import Actor


@dataclass
class ProbeBase:
    tip: np.ndarray = np.zeros(3)  # coordinates of the tip
    theta: float = 0.0  # angle relative to vertical in AP plane
    psy: float = 0.0  # angle relative to vertical in ML plane
    length: int = 150  # length in microns
    radius: int = 10
    color: str = "k"


class Probe(ProbeBase, Actor):
    watched = ("tip", "theta", "psy", "length")

    def __init__(self, *args, **kwargs):
        ProbeBase.__init__(self, *args, **kwargs)
        Actor.__init__(self, self.get_mesh(), name="Probe", br_class="Probe")

    def __setattr__(self, name, value):
        self.__dict__[name] = value

        # update mesh if we changed something
        if name in self.watched:
            self.mesh = self.get_mesh()

    @property
    def top(self):
        """
            The position of the top of the probe
        """
        top = self.tip.copy()
        # top[0] = self.tip[0] + self.length * np.sin(rad(self.theta)) * np.cos(rad(self.psy))
        # top[2] = self.tip[2] + self.length * np.sin(rad(self.theta)) * np.sin(rad(self.psy))
        # top[1] = self.tip[1] - self.length

        top[0] = self.length * np.sin(rad(self.theta)) * np.cos(rad(self.psy))
        top[1] = self.length * np.sin(rad(self.theta)) * np.sin(rad(self.psy))
        top[2] = self.length * np.cos(rad(self.theta))
        return top

    def get_mesh(self):
        """
            Returns the current mesh representation of the probe
        """
        shaft = Cylinder(
            pos=[self.top, self.tip], c="k", r=self.radius, alpha=1
        )
        tip = Sphere(pos=self.tip, r=self.radius + 5, c="k")
        mesh = merge(shaft, tip).c(self.color)
        return mesh

    # def point_at_region(self, region):
    #     self.
