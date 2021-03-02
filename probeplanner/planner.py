from loguru import logger
from rich.live import Live

from probeplanner.core import Core
from probeplanner.ui import TerminalUI


class Planner(Core):
    def __init__(
        self,
        aim_at=None,
        hemisphere="both",
        AP_angle=0,
        ML_angle=0,
        highlight=[],
        probe_file=None,
        interactive=True,
    ):
        """
            Interactive visualization that can be used to edit probe's parameters and save 
            probes to file.

            Arguments:
                aim_at: str. Acronym of brain region in which the probe's tip should be placed.
                hemisphere: str (both, left or right). When aiming the probe at a brain region, which hemisphere
                    should be targeted?
                AP_angle, ML_angle: float. Angles in the AP and ML planes
                highlight: list of str of brain region acronyms of regions to highlight in the rendering
                probe_file: str, Path. Path to a .yaml file with probe parameters.
                interactive: bool. If False the sliders and buttons are not shown.
        """
        Core.__init__(
            self,
            aim_at=aim_at,
            hemisphere=hemisphere,
            AP_angle=AP_angle,
            ML_angle=ML_angle,
            highlight=highlight,
            probe_file=probe_file,
        )

        if interactive:
            # initialize sliders
            self._init_sliders()
            self._init_buttons()

        self.refresh()

    def plan(self):
        """
            Starts interactive displays for planning probes placement.
        """
        display = TerminalUI(
            self.probe_display, self.target_display, self.tree_display
        )
        with Live(display):
            self.render()

    def save_probe(self):
        """
            Save current probe parameters to file.
        """
        logger.debug("Saving probe")
        self.probe.save("probe.yaml")

    def reset(self):
        """
            Reset probe to initial values
        """
        self.plotter.remove(self.probe.mesh)
        self.refresh(new_probe=self._probe.clone(), reset_sliders=True)

    def get_regions(self):
        """
            Produces a list of regions
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
            Removes from scene regions that are not relevant anymore (i.e. probe doesn't
            go through them anymore), 
            and adds new ones that are touched by the probe but not currently rendred.
            Hihlighted regions are rendered with outline and higher alpha.
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
                    alpha, silhouette = 0.1, False
                self.add_brain_region(
                    region, alpha=alpha, silhouette=silhouette
                )
                rendered.append(region)

        # add tip region
        self.add_brain_region(self.tip_region, alpha=0.6, silhouette=True)

        # keep track of regions
        self.probe_targets = rendered
