from owlready2 import NamedIndividual

from lcall.DLInstance import DLInstance


class OwlRdyInstance(DLInstance):
    """
    Wrapper for owlready2 instance objects
    """

    def __init__(self, instance: NamedIndividual):
        """
        Initialization

        :param instance: owlready2 instance
        """
        self.instance = instance

    def get(self) -> NamedIndividual:
        return self.instance
    
    def get_name(self) -> str:
        return self.instance.name

    def __repr__(self):
        return self.get_name()
