from loguru import logger
from rich.live import Live
import yaml


from probeplanner.core import Core
from probeplanner.terminal_ui import TerminalUI


class Planner(Core):
    def __init__(
        self,
        plan_file,
        probe_file,
        interactive=True,
    ):
        """
        Interactive visualization that can be used to edit probe's parameters and save
        probes to file.

        """
        Core.__init__(
            self,
            plan_file,
            probe_file,
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
            self.probe_parameters_display,
            self.probe_target_display,
            self.structures_target_display,
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

    def save(self):
        """
        Save current planning parameters to file.
        """
        params = dict(
            aim_at=None,
            AP_angle=self.probe.tilt_AP,
            ML_angle=self.probe.tilt_ML,
            tip=[round(float(x), 3) for x in self.probe.tip],
            highlight=None,
        )
        with open("plan.yaml", "w") as out:
            yaml.dump(params, out, default_flow_style=False, indent=4)
