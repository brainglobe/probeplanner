from vedo.shapes import Cylinder
import yaml
import brainrender
from loguru import logger

from probeplanner.probe import BREGMA, Probe
from probeplanner.ui import UI
from probeplanner.terminal_ui import (
    StructuresTree,
    ProbeTarget,
    ProbeParameters,
)
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
    probe_targets = []  # store brain regions touched by probes
    tip_region = ""  # brain region in which selected probe's tip is

    def __init__(
        self, plan_file, probe_file,
    ):
        """ 
            Base class providing core functionality for Planner and Viewer.
            Expands upon brainrender's Scene class to provide methods to add probes to the 
            rendering and add/remove brain regions touched by probes

        """
        # intialize parent classes
        brainrender.Scene.__init__(self)
        UI.__init__(self)
        Hierarchy.__init__(self)

        self.root_mesh = self.atlas.get_region("root")

        # load params
        with open(plan_file, "r") as fin:
            self.params = yaml.load(fin, Loader=yaml.FullLoader)

        # expand highlighted regions with their descendants
        self.highlight = []
        for region in self.params["highlight"]:
            self.highlight.extend(
                self.atlas.get_structure_descendants(region) + [region]
            )

        # add first probe
        self.add_probe(probe_file)

        # mark bregma
        self.add(
            Cylinder(
                pos=BREGMA, r=150, height=50, c="k", alpha=0.4, axis=(0, 1, 0)
            )
        )

        # initialize classes for live display
        self.probe_target_display = ProbeTarget()
        self.structures_target_display = StructuresTree()
        self.probe_parameters_display = ProbeParameters()

        # update rendering
        self.refresh()

    def add_probe(
        self, probe_file,
    ):
        """
            Creates a Probe by either loading it from file or by positioning and 
            tilting it according to the input parameters.
            
            Arguments:
                aim_at: str. Acronym of brain region in which the probe's tip should be placed.
                hemisphere: str (both, left or right). When aiming the probe at a brain region, which hemisphere
                    should be targeted?
                AP_angle, ML_angle: float. Angles in the AP and ML planes
                probe_file: str, Path. Path to a .yaml file with probe parameters.
        """

        self.probe = Probe.from_file(probe_file)

        # get mesh the probe is aimed at
        if self.params["aim_at"] is not None:
            aim_at = self.params["aim_at"] or "root"
            act = self.add_brain_region(aim_at, force=True)
            self.remove(act)

            # get target coords and aim
            target = act.centerOfMass()
        else:
            target = self.params["tip"]
        self.probe.point_at(target)

        # angle probe
        self.probe.tilt_ML = self.params["ML_angle"]
        self.probe.tilt_AP = self.params["AP_angle"]

        self.probe.update()
        self.add(self.probe)

        # keep track of the probe's original configuration
        self._probe = self.probe.clone()

    def get_regions(self):
        """
            Produces a list of regions
            that the probe goes through
        """

        self.tip_region = None
        names = []
        for p in self.probe.points:
            name = self.get_structure_from_point(p)
            if name == "root":
                continue
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
            Removes from scene regions that are not relevant anymore (i.e. probe doesn't
            go through them anymore), 
            and adds new ones that are touched by the probe but not currently rendred.
            Hihlighted regions are rendered with outline and higher alpha.
        """
        logger.debug("Updating region actors")
        rendered = []
        to_remove = []

        # remove outdated
        for region in self.probe_targets:

            if region not in new_targets and region != "root":
                to_remove.append(region)
            else:
                rendered.append(region)

        self.remove(*self.get_actors(name=to_remove, br_class="brain region"))

        # add new ones
        for region in new_targets:
            if region not in self.probe_targets and region != self.tip_region:
                if region in self.highlight:
                    alpha, silhouette = 0.8, True
                else:
                    alpha, silhouette = 0.1, False
                self.add_brain_region(
                    region, alpha=alpha, silhouette=silhouette
                )
                rendered.append(region)

        # add tip region
        self.add_brain_region(self.tip_region, alpha=0.6, silhouette=True)

        # keep track of regions
        self.probe_targets = rendered

    def refresh(self, new_probe=None, reset_sliders=False):
        """
            Refresh visualization to update the scene and the terminal UI.
            To ensure that the probe's actor is updated in the 3D visualization, 
            the current probe is removed an a new (cloned) probe is added.

            Arguments:
                new_probe: Probe. instance of Probe class, if None the current probe's clone
                    is used.
                reset_sliders: bool. If true the sliders' values are updated using the new
                    probe's parameters.
        """
        # make new probe
        new_probe = new_probe or self.probe.clone()

        # replace old probe in scene
        self.add(new_probe)
        self.remove(self.probe)

        # store new probe
        self.probe = new_probe
        self.probe_parameters_display.probe = new_probe

        # reset sliders
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
        self.probe_target_display.target = self.tip_region
