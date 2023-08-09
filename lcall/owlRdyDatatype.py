from lcall.DLDatatype import DLDatatype


class OwlRdyDatatype(DLDatatype):
    """
    Wrapper for owlready2 datatype objects
    """

    def __init__(self, datatype: type):
        """
        Initialization

        :param datatype: owlready2 datatype
        """
        self.datatype = datatype

    def get(self) -> type:
        return self.datatype

    def __repr__(self):
        return self.datatype.__name__
