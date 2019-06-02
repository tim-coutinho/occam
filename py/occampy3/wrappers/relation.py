from variable_list import VariableList


class Relation:
    def __init__(self, ref=None) -> None:
        self._ref = ref

    @property
    def ref(self):
        return self._ref

    @property
    def variable_count(self) -> int:
        return self._ref.getVariableCount()

    @property
    def print_name(self) -> str:
        return self._ref.getPrintName(False)

    @property
    def variable_list(self) -> VariableList:
        return VariableList(self._ref.getVariableList())

    def find_lift(self, sample_size: float, lift: float, state_name: str, frequency: float):
        pass

    def find_entropies(self, h1: float, h2: float, h12: float):
        pass
