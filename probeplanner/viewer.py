from probeplanner.planner import Planner


class Viewer(Planner):
    def __init__(
        self,
        probe_file,
        highlight=[],
    ):
        """
        View previously saved probes, without interactive sliders and buttons.
        """
        Planner.__init__(
            self,
            highlight=highlight,
            probe_file=probe_file,
            interactive=False,
        )

        self.plan()
