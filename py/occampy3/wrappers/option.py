class Option:
    def __init__(self, ref) -> None:
        self._ref = ref

    @property
    def name(self) -> str:
        return self._ref.getName()

    @property
    def value(self) -> str:
        return self._ref.getValue()
