from rich import tree


def in_tree(label, tree):
    """
        Check if a label is in the structure's treee
    """
    return label in [n.label for n in tree.children]


def get_with_label(label, tree):
    """
        Get a tree's node given it's label
    """
    return [n for n in tree.children if n.label == label][0]


def rgb2hex(rgb):
    """Convert RGB to Hex color."""
    h = "#%02x%02x%02x" % (int(rgb[0]), int(rgb[1]), int(rgb[2]))
    return h


class Hierarchy:
    """
        Functions to handle structures' hierarchy
    """

    bad = ("root", "fiber tracts", "VS")  # to be ugnored

    def get_structure_from_point(self, point):
        """
            Give a point's coordinates, get which brain region it is in
            and exclude bad ones. 

            Arguments:
                point: np.ndarray with AP-DV-ML coordinates.
        """
        if not self.root.isInside(point.coordinates):
            return None

        try:
            name = self.atlas.structure_from_coords(
                point.coordinates, microns=True, as_acronym=True
            )
        except (KeyError, IndexError):
            return None

        if name in self.bad:
            return None
        parents = self.atlas.get_structure_ancestors(name)
        if "fiber tracts" in parents or "VS" in parents:
            return None
        return name

    def construct_tree(self):
        """
            Creates a decorated rich Tree with
            the hierarchy of structures touched by the probe.
        """
        root = tree.Tree("Targeted structures")
        targets = [
            act.name for act in self.get_actors(br_class="brain region")
        ]

        for target in targets:
            if target == "root":
                continue

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

                if structure == self.tip_region:
                    style = f"[b #2a2a2a on {color}] "
                else:
                    style = f"[b {color}]"

                name = f"{style}{structure} "
                if in_tree(name, node):
                    node = get_with_label(name, node)
                else:
                    node = node.add(name, guide_style=color)

        self.structures_target_display.targets = root
