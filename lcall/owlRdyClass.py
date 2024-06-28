from owlready2 import ThingClass
from lcall.DLClass import DLClass


class OwlRdyClass(DLClass):
    """
    Wrapper for owlready2 class objects
    """

    def __init__(self, cls: ThingClass):
        """
        Initialization

        :param cls: owlready2 class
        """
        self.cls = cls

    def get(self) -> ThingClass:
        return self.cls

    def __repr__(self):
        return self.cls.name
