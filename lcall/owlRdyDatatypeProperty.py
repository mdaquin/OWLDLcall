from owlready2 import DataPropertyClass

from lcall.DLDatatypeProperty import DLDatatypeProperty


class OwlRdyDatatypeProperty(DLDatatypeProperty):
    """
    Wrapper for owlready2 datatype property objects
    """

    def __init__(self, datatype_property: DataPropertyClass):
        """
        Initialization

        :param datatype_property: owlready2 data property
        """
        self.property = datatype_property

    def get(self) -> DataPropertyClass:
        return self.property

    def __repr__(self):
        return "<"+str(self.property.get_iri())+">"
