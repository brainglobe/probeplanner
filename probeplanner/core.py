from vedo.shapes import Cylinder

import brainrender

from probeplanner.probe import BREGMA, Probe
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


class Core(brainrender.Scene, UI, Hierarchy):
    probe_targets = []
    tip_region = ""

    def __init__(
        self,
        aim_at=None,
        hemisphere="both",
        AP_angle=0,
        ML_angle=0,
        highlight=[],
        probe_file=None,
    ):
        brainrender.Scene.__init__(self)
        UI.__init__(self)
        Hierarchy.__init__(self)

        # initialize brain regions
        self.root_mesh = self.atlas.get_region("root")

        # expand highlighted regions with their descendants
        self.highlight = []
        for region in highlight:
            self.highlight.extend(
                self.atlas.get_structure_descendants(region) + [region]
            )

        # add probe
        self.add_probe(
            aim_at=aim_at,
            hemisphere=hemisphere,
            AP_angle=AP_angle,
            ML_angle=ML_angle,
            probe_file=probe_file,
        )

        # mark bregma
        self.add(
            Cylinder(
                pos=BREGMA, r=150, height=50, c="k", alpha=0.4, axis=(0, 1, 0)
            )
        )

        # update rendering
        self.refresh()

    def add_probe(
        self,
        aim_at=None,
        hemisphere="both",
        AP_angle=0,
        ML_angle=0,
        probe_file=None,
    ):
        """
            Creates a Probe and aims it at a target structure and tilts it/
        """
        if probe_file is not None:
            self.probe = Probe.load(probe_file)
        else:
            self.probe = Probe()

            # get mesh the probe is aimed at
            aim_at = aim_at or "root"
            if hemisphere == "right":
                hemisphere = "left"
            elif hemisphere == "left":
                hemisphere = "right"
            act = self.add_brain_region(
                aim_at, hemisphere=hemisphere, force=True
            )
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

        # keep track of the probe's original configuration
        self._probe = self.probe.clone()

    def refresh(self, new_probe=None, reset_sliders=False):
        # make new probe
        new_probe = new_probe or self.probe.clone()
        self.add(new_probe)
        self.remove(self.probe)
        self.probe = new_probe
        self.probe_display.probe = new_probe

        if reset_sliders:
            self.set_sliders_values()

        # refresh probe targets
        self.remove(*self.get_actors(name=self.tip_region))
        new_regions = self.get_regions()
        self.update_regions(new_regions)
        self._apply_style()

        # refresh probe targets tree
        self.construct_tree()

        # update probe tip target
        self.target_display.target = self.tip_region
