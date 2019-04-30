import occam3
from manager import Manager


class SBMManager(Manager):
    """
    Wrapper class for SBMManager
    """

    def __init__(self, ref=None):
        """
        :param: ref: the reference to the SBMManager object returned from the CPP engine
        """
        super()
        # Create new reference if one not given
        self._ref = ref or occam3.SBMManager()
