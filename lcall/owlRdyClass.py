from typing import Union

from owlready2 import ThingClass, ClassConstruct

from lcall.DLClass import DLClass


class OwlRdyClass(DLClass):
    """
    Wrapper for owlready2 class objects
    """

    def __init__(self, cls: Union[ThingClass, ClassConstruct]):
        """
        Initialization

        :param cls: owlready2 class
        """
        self.cls = cls

    def get(self) -> Union[ThingClass, ClassConstruct]:
        return self.cls

    def __repr__(self):
        return str(self.cls)
