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
            Starts interactive displays for planning probes placements
        """
        display = TerminalUI(
            self.probe_display, self.target_display, self.tree_display
        )
        with Live(display):
            self.render()

    def save_probe(self):
        logger.debug("Saving probe")
        self.probe.save("probe.yaml")

    def reset(self):
        self.plotter.remove(self.probe.mesh)
        self.refresh(new_probe=self._probe.clone(), reset_sliders=True)

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
                    alpha, silhouette = 0.1, False
                self.add_brain_region(
                    region, alpha=alpha, silhouette=silhouette
                )
                rendered.append(region)

        # add tip region
        self.add_brain_region(self.tip_region, alpha=0.6, silhouette=True)

        # keep track of regions
        self.probe_targets = rendered
