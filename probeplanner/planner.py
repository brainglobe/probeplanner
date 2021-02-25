from loguru import logger
from vedo.shapes import Cylinder
from rich.live import Live as LiveDisplay

import brainrender

from probeplanner.probe import Probe, BREGMA
from probeplanner.live import Live, Target, Tree, ProbeLive
from probeplanner.ui import UI
from probeplanner.hierarchy import Hierarchy

brainrender.settings.DEFAULT_CAMERA = {
    "pos": (-16980, -13013, -26161),
    "viewup": (0, -1, 0),
    "clippingRange": (14453, 61143),
    "focalPoint": (6588, 3683, -5280),
    "distance": 35640,
}
brainrender.settings.SHOW_AXES = False
brainrender.settings.WHOLE_SCREEN = False


class Planner(brainrender.Scene, UI, Hierarchy):
    probe_targets = []
    tip_region = ""

    def __init__(
        self,
        aim_at=None,
        hemisphere="both",
        AP_angle=0,
        ML_angle=0,
        highlight=[],
    ):
        brainrender.Scene.__init__(self)
        UI.__init__(self)
        Hierarchy.__init__(self)

        # initialize brain regions
        self.root_mesh = self.atlas.get_region("root")

        # expand highlight with their descendants
        self.highlight = []
        for region in highlight:
            self.highlight.extend(
                self.atlas.get_structure_descendants(region) + [region]
            )

        # initialize classes for live display
        self.target_display = Target()
        self.tree_display = Tree()
        self.probe_display = ProbeLive()

        # aim probe at target
        self.add_probe(
            aim_at=aim_at,
            hemisphere=hemisphere,
            AP_angle=AP_angle,
            ML_angle=ML_angle,
        )

        # initialize sliders
        self._init_sliders()

        # mark bregma
        self.add(
            Cylinder(
                pos=BREGMA, r=150, height=50, c="k", alpha=0.4, axis=(0, 1, 0)
            )
        )

        self.refresh()

    def plan(self):
        """
            Starts interactive displays for planning probes placements
        """
        display = Live(
            self.probe_display, self.target_display, self.tree_display
        )
        with LiveDisplay(display):
            self.render()

    def refresh(self):
        # make new probe
        new_probe = self.probe.clone()
        self.add(new_probe)
        self.remove(self.probe)
        self.probe = new_probe
        self.probe_display.probe = new_probe

        # refresh probe targets
        self.remove(*self.get_actors(name=self.tip_region))
        new_regions = self.get_regions()
        self.update_regions(new_regions)
        self._apply_style()

        # refresh probe targets tree
        self.construct_tree()

    def add_probe(
        self, aim_at=None, hemisphere="both", AP_angle=0, ML_angle=0
    ):
        """
            Creates a Probe and aims it at a target structure and tilts it/
        """
        self.probe = Probe()
        # get mesh the probe is aimed at
        aim_at = aim_at or "root"
        if hemisphere == "right":
            hemisphere = "left"
        elif hemisphere == "left":
            hemisphere = "right"
        act = self.add_brain_region(aim_at, hemisphere=hemisphere, force=True)
        self.remove(act)

        # get target coords and aim
        target = act.centerOfMass()
        target[2] = -target[2]
        delta = self.root_mesh.centerOfMass()[2] - target[2]
        target[2] = self.root_mesh.centerOfMass()[2] - delta
        self.probe.point_at(target)

        # angle probe
        self.probe.theta = ML_angle
        self.probe.psy = AP_angle
        self.add(self.probe)

    def get_regions(self):
        """
            Produces a list of region that names
            that the probe goes through
        """
        points = self.probe.sample()

        self.tip_region = None
        names = []
        for p in points:
            name = self.get_structure_from_point(p)
            if name is None:
                continue
            else:
                names.append(name)
                if self.tip_region is None:
                    self.tip_region = name

        logger.debug(f"Regions touched by probe: {names}")
        return names

    def update_regions(self, new_targets):
        """
            Removes from scene regions that are not relevant anymore, 
            and adds new ones
        """
        logger.debug("Updating region actors")
        rendered = []

        # remove outdated
        for region in self.probe_targets:
            if region not in new_targets:
                self.remove(
                    *self.get_actors(name=region, br_class="brain region")
                )
            else:
                rendered.append(region)

        # add new ones
        for region in new_targets:
            if region not in self.probe_targets and region != self.tip_region:
                if region in self.highlight:
                    alpha, silhouette = 0.8, True
                else:
                    alpha, silhouette = 0.2, False
                self.add_brain_region(
                    region, alpha=alpha, silhouette=silhouette
                )
                rendered.append(region)

        # add tip region
        self.add_brain_region(self.tip_region, alpha=0.6, silhouette=True)

        # keep track of regions
        self.probe_targets = rendered
