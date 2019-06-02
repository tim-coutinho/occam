from typing import Optional
import occam


class Table:
    def __init__(self, ref) -> None:
        self._ref = ref

    @classmethod
    def from_ref(cls, ref) -> Optional['Table']:
        if ref is None:
            return None

        return Table(ref)

    @property
    def ref(self):
        return self._ref

    @classmethod
    def new_table(cls, key_size: int, tuple_count: int) -> 'Table':
        return Table.from_ref(occam.Table(key_size, tuple_count))

    @property
    def key_size(self) -> int:
        return self._ref.getKeySize()

    @property
    def tuple_count(self) -> int:
        return self._ref.getTupleCount()

    def copy(self, table: 'Table') -> None:
        self._ref.copy(table.ref)
