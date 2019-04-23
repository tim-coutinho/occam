from occam import Model as Model_cpp


class Model:
    """
    Wrapper class for Model
    """

    def __init__(self, ref=None, size=1):
        """
        :param: ref: the reference to the Model object returned from the CPP engine
        """
        # Create new reference if one not given
        self._ref = ref or Model_cpp(size)
        self._id = 0

    @property
    def id_(self):
        return self._id

    @id_.setter
    def id_(self, id_):
        self._id = id_

    @property
    def fit_table(self):
        pass

    @fit_table.deleter
    def fit_table(self):
        self._ref.deleteFitTable()
