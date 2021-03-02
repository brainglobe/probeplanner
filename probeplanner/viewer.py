from probeplanner.planner import Planner


class Viewer(Planner):
    def __init__(
        self, probe_file, highlight=[],
    ):
        Planner.__init__(
            self,
            highlight=highlight,
            probe_file=probe_file,
            interactive=False,
        )

        self.plan()
