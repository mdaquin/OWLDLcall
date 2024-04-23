from owlready2 import ObjectPropertyClass

from lcall.DLObjectProperty import DLObjectProperty


class OwlRdyObjectProperty(DLObjectProperty):
    """
    Wrapper for owlready2 object property objects
    """

    def __init__(self, object_property: ObjectPropertyClass):
        """
        Initialization

        :param object_property: owlready2 object property
        """
        self.object_property = object_property

    def get(self) -> ObjectPropertyClass:
        return self.object_property

    def __repr__(self):
        return "<"+self.object_property.name+">"
