class PhaseSequencer(object):
    def __init__(self):
        self.phases = []

    def next_phase(self, fn):
        self.phases.append(fn)
        return fn
