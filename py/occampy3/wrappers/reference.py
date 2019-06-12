import occam


class Reference:
    def __init__(self, ref):
        self._ref = ref

    @property
    def value(self):
        return self._ref.getValue()


class IntRef(Reference):
    def __init__(self, value: int):
        Reference.__init__(self, ref=occam.IntRef(value))
