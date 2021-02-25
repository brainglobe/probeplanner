import numpy as np
from loguru import logger
from vedo.shapes import Sphere
from rich import tree
from rich.live import Live as LiveDisplay

import brainrender

from probeplanner.probe import Probe
from probeplanner.live import Live, Target, Tree

brainrender.settings.DEFAULT_CAMERA = {
    "pos": (-16980, -13013, -26161),
    "viewup": (0, -1, 0),
    "clippingRange": (14453, 61143),
    "focalPoint": (6588, 3683, -5280),
    "distance": 35640,
}
brainrender.settings.SHOW_AXES = False
brainrender.settings.WHOLE_SCREEN = False


def in_tree(label, tree):
    return label in [n.label for n in tree.children]


def get_with_label(label, tree):
    return [n for n in tree.children if n.label == label][0]


def rgb2hex(rgb):
    """Convert RGB to Hex color."""
    h = "#%02x%02x%02x" % (int(rgb[0]), int(rgb[1]), int(rgb[2]))
    return h


class Planner(brainrender.Scene):
    probe_targets = []

    def __init__(self):
        super(Planner, self).__init__()
        self.root_mesh = self.atlas.get_region("root")

        # initialize classes for live display
        self.target_display = Target()
        self.tree_display = Tree()

        # initialize sliders
        self._init_sliders()

        # get probe
        self.probe = Probe()
        self.probe.point_at(self.root_mesh)
        self.add(self.probe)

        self.refresh()

    def plan(self):
        display = Live(self.probe, self.target_display, self.tree_display)
        with LiveDisplay(display):
            self.render()

    def get_probe_regions(self):
        """
            Gets details about the regions that the probe is going through
        """
        root = tree.Tree("Targeted structures")
        targets = [act.name for act in self.probe_targets]

        for target in targets:
            parents = self.atlas.get_structure_ancestors(target)

            # add first parent
            color = rgb2hex(
                self.atlas._get_from_structure(parents[0], "rgb_triplet")
            )
            name = f"[b {color}]{parents[0]}"
            if in_tree(name, root):
                node = get_with_label(name, root)
            else:

                node = root.add(name, guide_style=color)

            # add all sub structures
            for structure in parents[1:] + [target]:
                color = rgb2hex(
                    self.atlas._get_from_structure(structure, "rgb_triplet")
                )
                name = f"[b {color}]{structure}"
                if in_tree(name, node):
                    node = get_with_label(name, node)
                else:

                    node = node.add(name, guide_style=color)

        self.tree_display.targets = root

    def mark_probe_regions(self):
        """
            Mark the regions that the probe goes through
        """
        self.probe_targets = []

        targeted = []
        for n, point in enumerate(self.probe.sample()):
            if n == 0:
                alpha = 0.6
                silhouette = True
            else:
                alpha = 0.4
                silhouette = False

            try:
                target = self.atlas.structure_from_coords(
                    point, microns=True, as_acronym=True
                )
            except KeyError:
                pass
            else:
                if n == 0:
                    self.target_display.target = target
                if target not in targeted:
                    # exclude ventricles and fiber tracts
                    if target in ("root", "fiber tracts", "VS"):
                        continue
                    parents = self.atlas.get_structure_ancestors(target)
                    if "fiber tracts" in parents or "VS" in parents:
                        continue

                    # add actor
                    actor = self.add_brain_region(
                        target, alpha=alpha, silhouette=silhouette
                    )
                    self.probe_targets.append(actor)
                    targeted.append(target)

    def refresh(self):
        # make new probe
        new_probe = self.probe.clone()
        self.add(new_probe)
        self.remove(self.probe)
        self.probe = new_probe

        self.remove(*self.probe_targets)
        self.mark_probe_regions()
        self._apply_style()

        self.get_probe_regions()

    def _init_sliders(self):
        bounds = self.root_mesh.bounds()
        com = self.root_mesh.centerOfMass()

        # 3D sliders for XYZ positioning
        p0 = (bounds[0], 0, 0)
        p1 = [bounds[1], 0, 0]
        p2 = (bounds[0], 0, -bounds[5])
        p3 = (bounds[0], bounds[3], 0)

        self.plotter.addSlider3D(
            self.move_AP,
            p0,
            p1,
            bounds[0],
            bounds[1],
            value=com[0],
            title="AP",
            rotation=180,
            showValue=False,
        )
        self.plotter.addSlider3D(
            self.move_ML,
            p0,
            p2,
            bounds[4],
            bounds[5],
            value=com[2],
            title="ML",
            rotation=180,
            showValue=False,
        )
        self.plotter.addSlider3D(
            self.move_DV,
            p0,
            p3,
            bounds[2],
            bounds[3],
            value=com[1],
            title="DV",
            rotation=180,
            showValue=False,
        )
        self.add(Sphere(pos=p0, r=350, c="k"))

        # 2D sliders for tilting
        self.plotter.addSlider2D(
            self.tilt_AP, -90, 90, value=0, title="AP angle",
        )

        self.plotter.addSlider2D(
            self.tilt_ML, -90, 90, value=0, title="ML angle", pos=3,
        )

    def move_AP(self, widget, event):
        value = widget.GetRepresentation().GetValue()
        delta = np.abs(value - self.probe.tip[0])
        if delta > 50:
            logger.debug(f"Move AP: {value:.1f}")
            self.probe.tip[0] = value
            self.refresh()

    def move_ML(self, widget, event):
        value = widget.GetRepresentation().GetValue()
        delta = np.abs(value - self.probe.tip[2])
        if delta > 50:
            logger.debug(f"Move ML: {value:.1f}")
            self.probe.tip[2] = value
            self.refresh()

    def move_DV(self, widget, event):
        value = widget.GetRepresentation().GetValue()
        delta = np.abs(value - self.probe.tip[1])
        if delta > 50:
            logger.debug(f"Move DV: {value:.1f}")
            self.probe.tip[1] = value
            self.refresh()

    def tilt_AP(self, widget, event):
        value = widget.GetRepresentation().GetValue()
        delta = np.abs(value - self.probe.psy)
        if delta > 1:
            logger.debug(f"Tilt AP: {value:.1f}")
            self.probe.psy = value
            self.refresh()

    def tilt_ML(self, widget, event):
        value = widget.GetRepresentation().GetValue()
        delta = np.abs(value - self.probe.theta)
        if delta > 1:
            logger.debug(f"Tilt ML: {value:.1f}")
            self.probe.theta = value
            self.refresh()
