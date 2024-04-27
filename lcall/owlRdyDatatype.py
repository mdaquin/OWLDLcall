from lcall.DLDatatype import DLDatatype


class OwlRdyDatatype(DLDatatype):
    """
    Wrapper for owlready2 datatype objects
    """

    def __init__(self, datatype: (type | None)):
        """
        Initialization

        :param datatype: owlready2 datatype
        (None means that the range wasn't specified and couldn't be obtained from the property)
        """
        self.datatype = datatype

    def get(self) -> (type | None):
        return self.datatype

    def __repr__(self):
        return self.datatype.__name__ if self.datatype is not None else "None"
