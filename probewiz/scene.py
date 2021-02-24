import brainrender


class Scene(brainrender.Scene):
    probes = []

    def __init__(self):
        super(Scene, self).__init__()

    def add_probe(self, probe):
        self.probes.append(probe)
        self.add(probe)
